from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import user_collection
import uvicorn
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from schemas import User
from database import get_database 
from sentence_transformers import SentenceTransformer

load_dotenv()
app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Specific origins
    allow_credentials=True,         # Allow cookies/auth headers
    allow_methods=["*"],             # Allow all HTTP methods
    allow_headers=["*"],             # Allow all headers
)




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
async def read_root(db = Depends(get_database)):
    users = await user_collection.find().to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    for user in users:
        if "_id" in user:
            user["_id"] = str(user["_id"])
    return users



@app.post("/api/v1/register")
async def register_user_v1(user: User, db = Depends(get_database)):
    result = await user_collection.insert_one(user.model_dump())
    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)