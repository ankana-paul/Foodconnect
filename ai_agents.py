import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)

class AIAgents:
    def __init__(self):
        try:
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if not google_api_key:
                raise ValueError("Google API key not found in environment variables")
            
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=google_api_key,
                temperature=0.7
            )
        except Exception as e:
            st.error(f"Failed to initialize AI Agents: {e}")
            raise
        
    def _process_llm_response(self, response):
        """Process LLM response and handle JSON parsing."""
        try:
            # Get content from response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            logger.debug(f"Raw LLM response: {content}")
            
            # Try to parse as JSON
            try:
                if content.strip().startswith('{') or content.strip().startswith('['):
                    return json.loads(content)
                
                # Try to extract JSON from markdown
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                    return json.loads(json_str)
                elif '```' in content:
                    json_str = content.split('```')[1].split('```')[0].strip()
                    if json_str.startswith('{') or json_str.startswith('['):
                        return json.loads(json_str)
                
                # If no JSON found, return as text
                return {"response": content}
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                return {"response": content}
                
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return {
                "error": "Failed to process AI response",
                "details": str(e),
                "raw_response": content[:500] + "..." if len(content) > 500 else content
            }

    def generate_meal_plan(self, user_profile: Dict[str, Any], local_produce: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a personalized meal plan based on user profile and local produce."""
        try:
            system_prompt = """You are a nutritionist AI that creates personalized meal plans. Generate a 7-day meal plan 
            with breakfast, lunch, and dinner options that match the user's preferences and use locally available produce.
            
            Respond in valid JSON format with this structure:
            {
              "days": {
                "Monday": {
                  "breakfast": {
                    "name": "...",
                    "description": "...",
                    "ingredients": ["...", "..."],
                    "nutrition": {
                      "calories": ...,
                      "protein": ...,
                      "carbs": ...,
                      "fat": ...
                    }
                  },
                  "lunch": {...},
                  "dinner": {...}
                },
                // ... other days
              },
              "shopping_list": ["...", "..."],
              "nutritional_summary": {
                "weekly_calories": ...,
                "weekly_protein": ...,
                // ... other metrics
              }
            }
            """
            
            user_prompt = f"""
            User Profile:
            - Age: {user_profile.get('age', 'N/A')}
            - Gender: {user_profile.get('gender', 'N/A')}
            - Dietary Preferences: {', '.join(user_profile.get('dietary_preferences', []))}
            - Allergies: {', '.join(user_profile.get('allergies', []))}
            - Health Goals: {', '.join(user_profile.get('health_goals', []))}
            - Activity Level: {user_profile.get('activity_level', 'moderate')}
            
            Available Local Produce:
            {json.dumps(local_produce, indent=2, cls=JSONEncoder) if local_produce else "None available"}
            
            Create a detailed meal plan that:
            1. Matches the user's dietary needs and goals
            2. Uses locally available ingredients when possible
            3. Provides balanced nutrition
            4. Includes a shopping list
            5. Provides nutritional information for each meal
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            processed_response = self._process_llm_response(response)
            
            if isinstance(processed_response, dict) and "error" in processed_response:
                raise Exception(processed_response["details"])
                
            return processed_response
            
        except Exception as e:
            logger.error(f"Error generating meal plan: {str(e)}")
            return {
                "error": "Failed to generate meal plan",
                "details": str(e)
            }

# Initialize AI Agents
@st.cache_resource
def get_ai_agents():
    return AIAgents()