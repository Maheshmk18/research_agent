from fastapi import FastAPI
from api.routes import history_router, research_router


app = FastAPI(title="Research Agent API")
app.include_router(research_router)
app.include_router(history_router)


@app.get("/")
def root():
    return {"message": "Research Agent API is running"}
