from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import warnings
warnings.filterwarnings('ignore')

from models import Product, SalesData, SimulationRequest, ChatRequest
from database import *
from ml_model import MLModels
from shap_analysis import ShapAnalyzer
from chatbot import BusinessChatbot

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Smartphone Sales Intelligence API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ml_models = MLModels()
chatbot = BusinessChatbot()

@app.on_event("startup")
async def startup_event():
    try:
        init_database()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

@app.get("/")
async def root():
    return {"message": "Smartphone Sales Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/add-product")
async def add_product(product: Product):
    try:
        result = smartphones_collection.insert_one(product.dict())
        return {"message": "Product added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/add-sales")
async def add_sales(sales: SalesData):
    try:
        result = sales_collection.insert_one(sales.dict())
        return {"message": "Sales data added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/predict/{model_name}")
async def predict_sales(model_name: str):
    try:
        # Get product data
        product = smartphones_collection.find_one({"model": model_name})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get sales data for training
        sales_data = list(sales_collection.find({"model": model_name}))
        if not sales_data:
            raise HTTPException(status_code=404, detail="Sales data not found")
        
        # Prepare data for training
        df = pd.DataFrame(sales_data)
        
        # Train models
        metrics = ml_models.train_regression_models(df)
        ml_models.train_prophet_model(df)
        
        # Make prediction
        features = [product['price'], product['ram'], product['storage'], 
                   product['battery'], product['camera_mp']]
        prediction = ml_models.hybrid_prediction(features)
        
        # Store prediction
        prediction_data = {
            "model": model_name,
            "predicted_sales": float(prediction),
            "confidence_score": 0.85,
            "created_at": datetime.now()
        }
        predictions_collection.insert_one(prediction_data)
        
        return {
            "model": model_name,
            "predicted_sales": float(prediction),
            "metrics": metrics,
            "feature_importance": ml_models.feature_importance.to_dict('records') if ml_models.feature_importance is not None else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate")
async def simulate(simulation: SimulationRequest):
    try:
        # Get base product data
        product = smartphones_collection.find_one({"model": simulation.model_name})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Use simulated values
        features = [simulation.price, simulation.ram, simulation.battery, 
                   product['storage'], simulation.camera_mp]
        
        # Get original prediction
        original_features = [product['price'], product['ram'], product['battery'], 
                           product['storage'], product['camera_mp']]
        
        original_sales = ml_models.predict_sales(original_features)
        simulated_sales = ml_models.predict_sales(features)
        
        # Calculate impact
        percent_change = ((simulated_sales - original_sales) / original_sales) * 100
        revenue_impact = (simulated_sales - original_sales) * product['price']
        
        return {
            "original_sales": float(original_sales),
            "simulated_sales": float(simulated_sales),
            "percent_change": float(percent_change),
            "revenue_impact": float(revenue_impact)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feature-importance/{model_name}")
async def get_feature_importance(model_name: str):
    try:
        importance_data = list(feature_importance_collection.find({"model": model_name}))
        if importance_data:
            return importance_data
        else:
            return {"message": "No feature importance data found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get context from database
        sales_summary = list(sales_collection.aggregate([
            {"$group": {
                "_id": None,
                "total_sales": {"$sum": "$units_sold"},
                "avg_sales": {"$avg": "$units_sold"},
                "total_revenue": {"$sum": "$revenue"}
            }}
        ]))
        
        feature_importance = list(feature_importance_collection.find().limit(5))
        
        context = {
            "sales_summary": sales_summary[0] if sales_summary else {},
            "feature_importance": feature_importance,
            "query_context": request.context
        }
        
        response = chatbot.generate_response(request.query, context)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard-data")
async def get_dashboard_data():
    try:
        # Get total sales
        total_sales = sales_collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$units_sold"}}}
        ])
        total_sales = list(total_sales)[0]['total'] if list(total_sales) else 0
        
        # Get total revenue
        total_revenue = sales_collection.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$revenue"}}}
        ])
        total_revenue = list(total_revenue)[0]['total'] if list(total_revenue) else 0
        
        # Get latest predictions
        latest_predictions = list(predictions_collection.find().sort("created_at", -1).limit(5))
        
        # Get sales trend
        sales_trend = list(sales_collection.find().sort("month", 1))
        
        return {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "latest_predictions": latest_predictions,
            "sales_trend": sales_trend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)