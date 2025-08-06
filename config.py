import streamlit as st

class Config:
    def __init__(self):
        self.collections = {
            "users": "users",
            "meal_plans": "meal_plans",
            "local_produce": "local_produce",
            "orders": "orders",
            "nutritional_impact": "nutritional_impact"
        }
        
        self.dietary_preferences = [
            "Vegetarian",
            "Vegan",
            "Pescatarian",
            "Gluten-Free",
            "Dairy-Free",
            "Nut-Free",
            "Keto",
            "Paleo",
            "Low-Carb",
            "Low-Fat",
            "Halal",
            "Kosher",
            "Other"
        ]
        
        self.health_goals = [
            "Weight Loss",
            "Weight Gain",
            "Muscle Building",
            "Diabetes Management",
            "Heart Health",
            "General Wellness",
            "Improved Digestion",
            "Better Sleep",
            "Increased Energy",
            "Stress Reduction"
        ]

# Initialize Config
@st.cache_resource
def get_config():
    return Config()