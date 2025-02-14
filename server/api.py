from fastapi import FastAPI
from routes import router

# Initialize FastAPI app
app = FastAPI()

# Include the router from routes.py
app.include_router(router)


@app.get("/", tags=["home"])
async def home():
    return {"message": "Welcome to SocksAI!"}
