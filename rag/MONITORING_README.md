# RAG Chatbot Monitoring Setup

## Overview
Complete monitoring stack with MLflow, Prometheus, and Grafana for your RAG chatbot.

## Services & Ports
| Service | URL | Purpose |
|---------|-----|---------|
| MLflow UI | http://localhost:5009 | Experiment tracking |
| Prometheus | http://localhost:9099 | Metrics collection |
| Grafana | http://localhost:3009 | Dashboards (admin/admin) |
| RAG API | http://localhost:8009 | Your chatbot API |
| App Metrics | http://localhost:8009/metrics | Prometheus metrics endpoint |

## Quick Start
1. Run: `start_monitoring.bat`
2. Wait for services to start
3. Access Grafana at http://localhost:3009 (login: admin/admin)

## Grafana Setup
1. Go to Connections → Data Sources → Add → Prometheus
2. Set URL to `http://prometheus:9090`
3. Click "Save & Test"
4. Import dashboard from `monitoring/grafana/rag-dashboard.json`

## Key Metrics
- `rate(rag_queries_total[1m])` - Queries per minute
- `histogram_quantile(0.95, rag_latency_seconds_bucket)` - P95 latency
- `rag_retrieval_docs_sum / rag_retrieval_docs_count` - Avg docs retrieved
- `ollama_calls_total` - Total Ollama API calls
- `ollama_errors_total` - Ollama API errors

## MLflow Experiments
- Experiment: "rag_chatbot"
- Tracks: query parameters, latency, docs retrieved, model used
- Access at: http://localhost:5009

## Troubleshooting
- Check Docker is running: `docker --version`
- View logs: `docker-compose logs [service_name]`
- Restart services: `docker-compose restart`
- Stop all: `docker-compose down`