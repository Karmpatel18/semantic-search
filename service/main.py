from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import user_collection
import uvicorn
from pinecone import Pinecone, ServerlessSpec
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




@app.get("/")
async def read_root(db = Depends(get_database)):
    users = await user_collection.find().to_list(length=None)
    # Convert ObjectId to string for JSON serialization
    for user in users:
        if "_id" in user:
            user["_id"] = str(user["_id"])
    return users

data = [
    {"_id":"68977adbbcb8c5676b2cd1e5","username":"karmpatel","email":"1234","description":"hi i ma karm","skills":["sql","react"]},
    {"_id":"6898c32c4054f35bf5b97f0c","username":"yuvraj parmar","email":"1234","description":"hi i ma yucraj","skills":["sql","react"]},
    {"_id":"689cb285d6c96036bf8001c2","username":"harsh patel","email":"1234 bairo che","description":"hi i am harsh","skills":["sql","react","flutter"]}
]

def prepare_text(item):
    return f"Username: {item['username']}. Description: {item['description']}. Skills: {', '.join(item['skills'])}."

texts = [prepare_text(d) for d in data]
embeddings  = model.encode(texts).tolist()

print(len(embeddings), len(embeddings[0]))

index_name = "test"

if index_name not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=384,  # Must match embedding size
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
index = pc.Index(index_name)

to_upsert = []

for i, item in enumerate(data):
    to_upsert.append((
        item["_id"],
        embeddings[i],
        {
            "username": item["username"],
            "email": item["email"],
            "description": item["description"],
            "skills": item["skills"]
        }
    ))

index.upsert(vectors=to_upsert, namespace="users")
print("✅ Data upserted successfully!")

query = "developer skilled in flutter"
query_vector = model.encode([query]).tolist()

result = index.query(
    vector=query_vector[0],
    top_k=2,
    include_metadata=True,
    namespace="users"
)
print(result)
for match in result['matches']:
    print(match['score'], match['metadata'])

@app.post("/api/v1/register")
async def register_user_v1(user: User, db = Depends(get_database)):
    result = await user_collection.insert_one(user.model_dump())
    return {"message": "User registered successfully!", "user_id": str(result.inserted_id)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)