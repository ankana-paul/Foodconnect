from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            mongodb_db = os.getenv("MONGODB_DATABASE")
            
            if not mongodb_uri or not mongodb_db:
                raise ValueError("MongoDB credentials not found in environment variables")
            
            self.client = MongoClient(
                mongodb_uri,
                server_api=ServerApi('1'),
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                serverSelectionTimeoutMS=30000
            )
            self.db = self.client[mongodb_db]
            
            # Test the connection
            self.client.admin.command('ping')
            st.success("Successfully connected to MongoDB!")
            
            # Initialize collections
            self._initialize_collections()
            
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def _initialize_collections(self):
        """Ensure all required collections exist with indexes"""
        required_collections = {
            "users": [
                ("email", 1),
                ("created_at", -1)
            ],
            "meal_plans": [
                ("user_id", 1),
                ("created_at", -1)
            ],
            "local_produce": [
                ("name", "text"),
                ("supplier", 1)
            ],
            "orders": [
                ("user_id", 1),
                ("created_at", -1)
            ]
        }
        
        existing_collections = self.db.list_collection_names()
        
        for collection_name, indexes in required_collections.items():
            if collection_name not in existing_collections:
                self.db.create_collection(collection_name)
                
            # Create indexes
            collection = self.db[collection_name]
            for index in indexes:
                if isinstance(index, tuple):
                    collection.create_index([index])
                elif isinstance(index, dict):
                    collection.create_index(index)

    def get_collection(self, collection_name: str):
        """Get a reference to a collection"""
        return self.db[collection_name]
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert a document into a collection"""
        collection = self.get_collection(collection_name)
        document['created_at'] = datetime.now()
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    def find_documents(self, collection_name: str, query: Dict[str, Any] = {}, limit: int = 100) -> List[Dict[str, Any]]:
        """Find documents in a collection"""
        collection = self.get_collection(collection_name)
        return list(collection.find(query).limit(limit))
    
    def update_document(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update documents in a collection"""
        collection = self.get_collection(collection_name)
        update_data['updated_at'] = datetime.now()
        result = collection.update_many(query, {'$set': update_data})
        return result.modified_count
    
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> int:
        """Delete documents from a collection"""
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        return result.deleted_count
    
    def get_dataframe(self, collection_name: str, query: Dict[str, Any] = {}, limit: int = 100) -> pd.DataFrame:
        """Get data from a collection as a pandas DataFrame"""
        data = self.find_documents(collection_name, query, limit)
        return pd.DataFrame(data)

# Initialize database connection
@st.cache_resource
def get_db():
    return Database()