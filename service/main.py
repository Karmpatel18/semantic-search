from fastapi import FastAPI
from pinecone import Pinecone
import os
from dotenv import load_dotenv


load_dotenv()

# Initialize FastAPI application
app = FastAPI()
# Initialize Pinecone with the API key from environment variables
pc = Pinecone(api_key=os.getenv("PINE_API"))


@app.get("/")
def read_root():
    return {'data': 'Hello, World!'}

@app.post("/register")
def register_user():
    return {'data': 'User registered successfully!'}