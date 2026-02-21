import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class BusinessChatbot:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
        
    def generate_response(self, query, context):
        prompt = f"""
        You are an AI business analyst for a smartphone company. 
        Use the following data context to answer the business question:
        
        Context:
        {context}
        
        Business Question: {query}
        
        Provide a professional, data-driven answer with specific insights and recommendations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def analyze_sales_trend(self, sales_data, features):
        context = f"""
        Sales Data: {sales_data}
        Feature Importance: {features}
        
        Analyze the sales trend and provide insights on:
        1. Key factors affecting sales
        2. Recommendations for improvement
        3. Market opportunities
        """
        
        prompt = f"Based on this data, provide a comprehensive business analysis: {context}"
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error in analysis: {str(e)}"