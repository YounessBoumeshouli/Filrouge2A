from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import location, price, tracking, admin, journey
import os
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from starlette.responses import Response
import time

# Try to import YOLO router, but make it optional
try:
    from app.routers import yolo

    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ YOLO router not available: {e}")
    YOLO_AVAILABLE = False
except Exception as e:
    print(f"⚠️ YOLO service error: {e}")
    YOLO_AVAILABLE = False

# Check if external YOLO API is available
YOLO_API_URL = os.getenv("YOLO_API_URL", "http://localhost:8002")
print(f"🤖 YOLO API configured at: {YOLO_API_URL}")

# Create database tables
Base.metadata.create_all(bind=engine)

# Prometheus metrics
http_requests_total = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint"]
)
http_request_duration = Histogram(
    "http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"]
)
yolo_detections = Counter("yolo_detections_total", "Total YOLO detections")
price_analyses = Counter("price_analyses_total", "Total price analyses")

app = FastAPI(
    title="Tourist Helper API",
    description="Backend for Tourist Helper application providing Location and Price assistance.",
    version="1.0.0",
)


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


# Configure CORS to allow requests from the frontend
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(location.router)
app.include_router(price.router)
app.include_router(tracking.router)
app.include_router(admin.router)
app.include_router(journey.router)

# Only include YOLO router if available
if YOLO_AVAILABLE:
    app.include_router(yolo.router)
    print("✅ YOLO detection service enabled")
else:
    print("⚠️ YOLO detection service disabled")


@app.get("/")
async def root():
    return {"message": "Welcome to Tourist Helper API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Tourist Helper API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
