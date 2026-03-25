from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.assistant_service import generate
from app.core.exceptions import AppException, app_exception_handler, global_exception_handler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG API", description="Simple RAG API for medical queries")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

class QueryRequest(BaseModel):
    query: str
    k: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    status: str = "success"

@app.get("/")
def root():
    return {"message": "RAG API - Medical Assistant", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "rag-api"}

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    try:
        logger.info(f"Processing query: {request.query[:50]}...")
        
        answer = generate(request.query, k=request.k)
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise AppException(f"Error processing query: {str(e)}", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)