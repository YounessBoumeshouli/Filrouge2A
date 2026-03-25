# ProtoCare — Cahier des Charges Compliance Audit

> **Instructions for the agent:**
> Go through each section below. For every checklist item, inspect the codebase and mark it as:
> - ✅ `DONE` — fully implemented and functional
> - ⚠️ `PARTIAL` — partially implemented or needs improvement
> - ❌ `MISSING` — not implemented
> - `N/A` — not applicable
>
> Add a short **note** after each item explaining what you found (file paths, function names, issues, etc.).

---

## 1. RAG Pipeline

### 1.1 Preprocessing & Chunking
- [ ] PDF/technical documents can be imported as data sources
- [ ] A chunking strategy is chosen and justified (e.g. recursive, semantic, sentence-based)
- [ ] Chunk size and overlap are configurable
- [ ] Each chunk carries useful **metadata** (source, page number, section title, date, etc.)

### 1.2 Embeddings & Vector Store
- [ ] A vector database is used (ChromaDB / FAISS / Qdrant — pick one and justify)
- [ ] An embedding model is selected and documented (HuggingFace or Ollama)
- [ ] Embeddings are **persisted** (not recomputed on every run)
- [ ] The vector store is loadable across sessions

### 1.3 Retrieval
- [ ] A retriever is configured to fetch relevant chunks based on user query
- [ ] **Query expansion** technique is implemented
- [ ] **Reranking** technique is implemented
- [ ] `k` (number of returned chunks) is configurable

### 1.4 Response Generation
- [ ] A centralized, well-structured **prompt template** is defined
- [ ] An LLM is used to generate answers from retrieved chunks
- [ ] Answers are grounded in retrieved context (no hallucination safeguards in place)
- [ ] The full RAG pipeline is built with **LangChain**

---

## 2. Backend (FastAPI)

### 2.1 API Endpoints
- [ ] `POST /login` — JWT authentication endpoint
- [ ] `POST /query` — accepts a user query, runs RAG, returns response
- [ ] `GET /history` — returns query history for the authenticated user
- [ ] `GET /health` — health check endpoint

### 2.2 Code Quality & Architecture
- [ ] **Pydantic** is used for request/response validation
- [ ] **SQLAlchemy** ORM is used for all DB interactions
- [ ] **JWT** authentication is implemented and protects secured routes
- [ ] **pydantic-settings** + `.env` file used for configuration management
- [ ] Centralized **exception handling** (custom error handlers, HTTP error responses)
- [ ] Code is readable, documented, and follows consistent conventions

### 2.3 Database (PostgreSQL)
- [ ] `users` table: `id, username, email, hashed_password, role`
- [ ] `Query` table: `id, query, reponse, created_at`
- [ ] Migrations or schema creation scripts are present
- [ ] PostgreSQL is used (not SQLite or other)

### 2.4 Unit Tests
- [ ] Unit tests exist for backend logic
- [ ] Tests cover at least: auth, query endpoint, history endpoint
- [ ] Tests can be run with a single command (e.g. `pytest`)

---

## 3. Frontend

### 3.1 Chat Interface
- [ ] A UI (Streamlit or React) allows doctors to send queries to the RAG assistant
- [ ] The interface is **intuitive and professional**
- [ ] Responses are displayed clearly, with sources/context if available
- [ ] Loading states and error messages are handled

### 3.2 History Dashboard
- [ ] A dashboard displays the **query history** for each logged-in doctor
- [ ] Each history entry shows: query, response, timestamp
- [ ] The dashboard is filterable or paginated (bonus)

---

## 4. Containerization

- [ ] A `Dockerfile` exists for the backend
- [ ] A `docker-compose.yml` orchestrates all services (backend, frontend, DB, vector store, monitoring)
- [ ] Services communicate correctly via Docker networking
- [ ] Environment variables are injected via `.env` and not hardcoded
- [ ] The full stack can be launched with a single `docker-compose up` command

---

## 5. LLMOps — MLflow

### 5.1 RAG Configuration Logging
- [ ] **Chunking params** logged: chunk size, overlap, strategy
- [ ] **Embedding params** logged: model name, dimensionality, normalization
- [ ] **Retrieval params** logged: similarity algorithm (cosine/L2), `k`, reranking strategy

### 5.2 LLM Hyperparameters Logging
- [ ] Prompt template logged
- [ ] Temperature logged
- [ ] Model name logged
- [ ] `max_tokens`, `top_p`, `top_k` logged

### 5.3 Responses & Metrics Logging
- [ ] Responses and retrieved contexts are logged per query
- [ ] RAG metrics logged via **DeepEval**:
  - [ ] Answer Relevance
  - [ ] Faithfulness
  - [ ] Precision@k
  - [ ] Recall@k
- [ ] The RAG pipeline (model) is versioned and logged with **LangChain + MLflow**

---

## 6. CI/CD Pipeline

- [ ] CI/CD pipeline is configured (GitHub Actions or equivalent)
- [ ] Pipeline runs **unit tests** (code + RAG tests) on each push/PR
- [ ] Pipeline **builds the Docker image** on success
- [ ] Pipeline **publishes the image to Docker Hub**
- [ ] Pipeline is documented (badge in README or workflow file present)

---

## 7. Monitoring — Prometheus & Grafana

### 7.1 Infrastructure Metrics
- [ ] **CPU usage** is collected
- [ ] **RAM usage** is collected
- [ ] Container-level metrics are visible (via cAdvisor or node-exporter)

### 7.2 Application / RAG Metrics
- [ ] **Latency** per query is tracked
- [ ] **Error rate** is tracked
- [ ] **Number of requests** is tracked
- [ ] **Response quality scores** are tracked (tied to DeepEval/MLflow)

### 7.3 Alerting
- [ ] Alerts are configured in Grafana/Prometheus
- [ ] At least one alert on **latency threshold**
- [ ] At least one alert on **error rate threshold**
- [ ] At least one alert on **response quality threshold**

### 7.4 Dashboards
- [ ] A Grafana dashboard is live and accessible
- [ ] Dashboard panels cover infrastructure + RAG application metrics

---

## 8. Project Documentation & Deliverables

- [ ] **README.md** is present, comprehensive, and includes:
  - Project description and context
  - Architecture diagram or description
  - Setup instructions (local + Docker)
  - Environment variables reference
  - How to run tests
  - How to access MLflow / Grafana dashboards
- [ ] **Architecture diagram** (image or diagram-as-code) is included
- [ ] **GitHub repository** is clean (no secrets committed, `.gitignore` present)
- [ ] `requirements.txt` or `pyproject.toml` is present and up to date

---

## 9. Summary Table

Fill this in after completing the audit above.

| Section | Status | Notes |
|---|---|---|
| RAG — Chunking | | |
| RAG — Embeddings & Store | | |
| RAG — Retrieval | | |
| RAG — Generation | | |
| Backend — Endpoints | | |
| Backend — Auth & Validation | | |
| Backend — Database | | |
| Backend — Tests | | |
| Frontend — Chat UI | | |
| Frontend — History Dashboard | | |
| Containerization | | |
| MLflow — Config & Params | | |
| MLflow — Metrics & Versioning | | |
| CI/CD | | |
| Prometheus & Grafana | | |
| Documentation & README | | |

---

## 10. Agent Final Verdict

> After completing all checks, provide:
> 1. **Overall compliance score** (e.g. 34/42 items ✅)
> 2. **Top 3 critical missing items** that would most impact the jury evaluation
> 3. **Quick wins** — items that are easy to add before the defense
> 4. **Recommendation** — is the project ready for the jury, or does it need significant work?
