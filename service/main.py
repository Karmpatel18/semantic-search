from fastapi import FastAPI
import uvicorn
from database import db
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from pydantic import BaseModel
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

class User(BaseModel):
    username: str
    email: str
    description: str
    skills: list[str]
    

@app.post("/api/v1/register")
async def register_user_v1(user: User):
    await db["users"].insert_one(user.model_dump())
    return {"message": "User registered successfully!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)