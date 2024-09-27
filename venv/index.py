from fastapi import FastAPI
from routes.user import user_router  # Import the router correctly

app = FastAPI()

app.include_router(user_router)  # Including the user_router

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="127.0.0.1", port=8000, reload=True)
