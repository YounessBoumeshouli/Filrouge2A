from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, query, users
from app.core.database import engine, Base
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    global_exception_handler,
)
from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
)
from starlette.responses import Response
import time
import mlflow

# Prometheus metrics
active_users = Gauge("active_users", "Number of active users")
rag_pipeline_calls = Counter("rag_pipeline_calls_total", "Total RAG pipeline calls")
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint"]
)
http_request_duration = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"]
)
app_info = Gauge("app_info", "Application info", ["version", "name"])

app = FastAPI(title="CliniQ API")

# Set app info metric
app_info.labels(version="1.0.0", name="CliniQ RAG API").set(1)

# MLflow setup
try:
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("rag_chatbot")
except Exception as e:
    print(f"Warning: MLflow setup failed: {e}")


@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path

    http_requests_total.labels(method=method, endpoint=endpoint).inc()

    response = await call_next(request)

    process_time = time.time() - start_time
    http_request_duration.labels(method=method, endpoint=endpoint).observe(process_time)
    response.headers["X-Process-Time"] = str(process_time)

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(query.router)
app.include_router(users.router)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
def root():
    return {"message": "CliniQ API"}
