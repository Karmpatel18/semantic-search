from fastapi import FastAPI
from database import db
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Initialize FastAPI application
app = FastAPI()
# Initialize Pinecone with the API key from environment variables
pc = Pinecone(api_key=os.getenv("PINE_API"))

index_name = "semantic-search-index"

if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )
    
    



@app.get("/")
async def read_root():
    # Example: Fetch all documents from 'users' collection
    await db["test_collection"].insert_one({"message": "Hello, Mongo!"})
    return {"message": "Welcome to the Semantic Search API!"}

@app.post("/register")
def register_user():
    return {'data': 'User registered successfully!'}

@app.post("/api/v1/register")
def register_user_v1():
    return {'data': 'User registered successfully in v1!'}