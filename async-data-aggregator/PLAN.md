# Async Data Aggregator — Implementation Plan

Based on the project specification document. This plan is aligned strictly with the requirements.

---

## Tech Stack (from document)

| Component | Technology |
|-----------|------------|
| Frontend | React (Vite) |
| Backend | FastAPI |
| Task Queue | Celery + Redis |
| Database | PostgreSQL |
| Storage | AWS S3 |
| Deployment | Docker, Docker Compose, AWS ECS |
| CI/CD | GitHub Actions |
| External APIs | OpenWeatherMap, NewsAPI |

**Prerequisites:** Python 3.11+, Node.js 18+, Docker, Docker Compose, AWS CLI configured, GitHub account, OpenWeatherMap API key, NewsAPI API key

---

## Architecture (from document)

```
React Frontend (Vite)
        │
        ▼
FastAPI Backend ──► Redis (Broker) ──► Celery Worker
        │                    │
        ▼                    ▼
   PostgreSQL            S3 (Results)
        │
        └───────────── AWS ECS ─────────────────┘
                              ▲
                   GitHub Actions CI/CD
```

---

## Phase 1: Backend (FastAPI + Celery) — ~3 hours

### Step 1.1: Project Structure

| Sub-task | Description |
|----------|-------------|
| 1.1.1 | Create directories: `data-aggregator/{backend,frontend,docker,.github/workflows}` |
| 1.1.2 | Create `backend/{app,workers}` |
| 1.1.3 | Create `backend/app/__init__.py`, `main.py`, `models.py`, `schemas.py`, `config.py`, `database.py` |
| 1.1.4 | Create `backend/workers/__init__.py`, `celery_app.py`, `tasks.py` |
| 1.1.5 | Create `backend/requirements.txt` |

### Step 1.2: Dependencies — `backend/requirements.txt`

| Sub-task | Description |
|----------|-------------|
| 1.2.1 | Add fastapi==0.111.0, uvicorn==0.30.1 |
| 1.2.2 | Add celery==5.4.0, redis==5.0.7 |
| 1.2.3 | Add sqlalchemy==2.0.31, psycopg2-binary==2.9.9 |
| 1.2.4 | Add boto3==1.34.144, httpx==0.27.0 |
| 1.2.5 | Add python-dotenv==1.0.1, pydantic-settings==2.3.4, alembic==1.13.2 |

### Step 1.3: Configuration — `backend/app/config.py`

| Sub-task | Description |
|----------|-------------|
| 1.3.1 | Create Settings class with Pydantic BaseSettings |
| 1.3.2 | Add DATABASE_URL, REDIS_URL |
| 1.3.3 | Add AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET |
| 1.3.4 | Add OPENWEATHER_API_KEY, NEWSAPI_API_KEY |
| 1.3.5 | Add CORS_ORIGINS |
| 1.3.6 | Add Config with env_file = ".env" |
| 1.3.7 | Instantiate settings object |

### Step 1.4: Database Setup — `backend/app/database.py`

| Sub-task | Description |
|----------|-------------|
| 1.4.1 | Create SQLAlchemy engine from DATABASE_URL |
| 1.4.2 | Create SessionLocal with sessionmaker |
| 1.4.3 | Define Base (DeclarativeBase) |
| 1.4.4 | Implement get_db() generator dependency |

### Step 1.5: Models — `backend/app/models.py`

| Sub-task | Description |
|----------|-------------|
| 1.5.1 | Define JobStatus enum: PENDING, PROCESSING, COMPLETED, FAILED |
| 1.5.2 | Define AggregationJob model with columns: id, status, sources, parameters, result_url, error_message, created_at, completed_at |

### Step 1.6: Pydantic Schemas — `backend/app/schemas.py`

| Sub-task | Description |
|----------|-------------|
| 1.6.1 | Define JobCreate (sources, parameters) |
| 1.6.2 | Define JobResponse (id, status, sources, parameters, result_url, error_message, created_at, completed_at) |
| 1.6.3 | Define JobStatusResponse (id, status, result_url, error_message) |
| 1.6.4 | Set Config from_attributes = True for JobResponse |

### Step 1.7: Celery App — `backend/workers/celery_app.py`

| Sub-task | Description |
|----------|-------------|
| 1.7.1 | Create Celery app with broker and backend from REDIS_URL |
| 1.7.2 | Configure task_serializer, accept_content, result_serializer as json |
| 1.7.3 | Configure timezone="UTC", enable_utc=True |
| 1.7.4 | Configure task_track_started=True, task_acks_late=True, worker_prefetch_multiplier=1 |
| 1.7.5 | Autodiscover tasks from workers package |

### Step 1.8: Celery Tasks — `backend/workers/tasks.py`

| Sub-task | Description |
|----------|-------------|
| 1.8.1 | Implement fetch_weather task (OpenWeatherMap API, bind=True, max_retries=3, default_retry_delay=5) |
| 1.8.2 | Implement fetch_news task (NewsAPI, bind=True, max_retries=3, default_retry_delay=5) |
| 1.8.3 | Implement aggregate_results chord callback (merge results, upload to S3, update job to COMPLETED) |
| 1.8.4 | Implement update_job_status task |
| 1.8.5 | Create FETCHER_MAP: weather → fetch_weather, news → fetch_news |
| 1.8.6 | Implement run_aggregation_pipeline (chord: parallel fetch tasks → aggregate_results) |

### Step 1.9: FastAPI Application — `backend/app/main.py`

| Sub-task | Description |
|----------|-------------|
| 1.9.1 | Create FastAPI app, add CORS middleware |
| 1.9.2 | Create tables: Base.metadata.create_all(bind=engine) |
| 1.9.3 | Implement GET /health |
| 1.9.4 | Implement POST /api/jobs (validate sources: weather, news; create job; trigger pipeline) |
| 1.9.5 | Implement GET /api/jobs/{job_id} |
| 1.9.6 | Implement GET /api/jobs (list, order by created_at desc, limit 20) |
| 1.9.7 | Implement GET /api/jobs/{job_id}/result (fetch JSON from S3) |

---

## Phase 2: React Frontend — ~2 hours

### Step 2.1: Create React App

| Sub-task | Description |
|----------|-------------|
| 2.1.1 | Run `npm create vite@latest . -- --template react` in frontend directory |
| 2.1.2 | Install axios |

### Step 2.2: API Client — `frontend/src/api.js`

| Sub-task | Description |
|----------|-------------|
| 2.2.1 | Create axios instance with VITE_API_URL base |
| 2.2.2 | Export createJob(sources, parameters) |
| 2.2.3 | Export getJob(jobId) |
| 2.2.4 | Export listJobs() |
| 2.2.5 | Export getJobResult(jobId) |

### Step 2.3: Main App — `frontend/src/App.jsx`

| Sub-task | Description |
|----------|-------------|
| 2.3.1 | State: jobs, selectedSources (weather, news), city, topic, loading, activeResult, pollingIds |
| 2.3.2 | Load jobs on mount via refreshJobs() |
| 2.3.3 | Poll PENDING/PROCESSING jobs every 2 seconds; remove from polling when COMPLETED/FAILED |
| 2.3.4 | handleSubmit: create job, add to pollingIds, refresh jobs |
| 2.3.5 | handleViewResult: fetch result for completed job |
| 2.3.6 | toggleSource for weather/news checkboxes |
| 2.3.7 | Job creation form: sources checkboxes, city input, topic input, submit button |
| 2.3.8 | Jobs table: ID, Sources, Status, Created, Actions |
| 2.3.9 | Status badges with colors (PENDING, PROCESSING, COMPLETED, FAILED) |
| 2.3.10 | View Result button for completed jobs; spinner for pending/processing |
| 2.3.11 | Result viewer: weather section (temp, humidity, wind, description) |
| 2.3.12 | Result viewer: news section (articles with title, link, source) |
| 2.3.13 | Collapsible "View Raw JSON" in result section |

### Step 2.4: Styles — `frontend/src/App.css`

| Sub-task | Description |
|----------|-------------|
| 2.4.1 | Base styles: dark theme (#0f172a background, #e2e8f0 text) |
| 2.4.2 | Card, form-group, form-row styles |
| 2.4.3 | Table, status-badge, mono styles |
| 2.4.4 | Result section: result-header, stat-grid, article-list |
| 2.4.5 | Spinner animation |

---

## Phase 3: Docker Compose — ~1 hour

### Step 3.1: Backend Dockerfile — `backend/Dockerfile`

| Sub-task | Description |
|----------|-------------|
| 3.1.1 | Base: python:3.11-slim |
| 3.1.2 | WORKDIR /app, COPY requirements.txt, pip install |
| 3.1.3 | COPY application, CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 |

### Step 3.2: Frontend Dockerfile — `frontend/Dockerfile`

| Sub-task | Description |
|----------|-------------|
| 3.2.1 | Build stage: node:18-alpine, npm ci, npm run build |
| 3.2.2 | Build arg: VITE_API_URL (default http://localhost:8000) |
| 3.2.3 | Serve stage: nginx:alpine, copy dist to /usr/share/nginx/html |
| 3.2.4 | Copy nginx.conf, EXPOSE 80 |

### Step 3.3: Nginx Config — `frontend/nginx.conf`

| Sub-task | Description |
|----------|-------------|
| 3.3.1 | Listen 80, root /usr/share/nginx/html |
| 3.3.2 | location /: try_files $uri $uri/ /index.html |
| 3.3.3 | location /api/: proxy_pass to api:8000 |

### Step 3.4: Docker Compose — `docker-compose.yml`

| Sub-task | Description |
|----------|-------------|
| 3.4.1 | db: postgres:16-alpine, POSTGRES_USER/PASSWORD/DB, port 5432, volume pgdata |
| 3.4.2 | redis: redis:7-alpine, port 6379 |
| 3.4.3 | api: build ./backend, port 8000, env from .env, depends_on db redis |
| 3.4.4 | worker: build ./backend, command celery worker, env from .env, depends_on db redis |
| 3.4.5 | frontend: build ./frontend with VITE_API_URL="", port 80, depends_on api |

### Step 3.5: Environment File — `.env`

| Sub-task | Description |
|----------|-------------|
| 3.5.1 | Add AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET |
| 3.5.2 | Add OPENWEATHER_API_KEY, NEWSAPI_API_KEY |

### Step 3.6: Test Locally

| Sub-task | Description |
|----------|-------------|
| 3.6.1 | Run docker compose up --build |
| 3.6.2 | Test GET http://localhost:8000/health |
| 3.6.3 | Test POST /api/jobs with sources and parameters |
| 3.6.4 | Open http://localhost in browser |

---

## Phase 4: AWS Deployment — ~2–3 hours

### Step 4.1: Create S3 Bucket

| Sub-task | Description |
|----------|-------------|
| 4.1.1 | Run aws s3 mb s3://data-aggregator-results --region us-east-1 |

### Step 4.2: Create ECR Repositories

| Sub-task | Description |
|----------|-------------|
| 4.2.1 | Create data-aggregator/api |
| 4.2.2 | Create data-aggregator/worker |
| 4.2.3 | Create data-aggregator/frontend |

### Step 4.3: Push Images to ECR

| Sub-task | Description |
|----------|-------------|
| 4.3.1 | ECR login with aws ecr get-login-password |
| 4.3.2 | Build and push API image |
| 4.3.3 | Tag and push worker image (same as API) |
| 4.3.4 | Build and push frontend image |

### Step 4.4: Create ECS Cluster

| Sub-task | Description |
|----------|-------------|
| 4.4.1 | Run aws ecs create-cluster --cluster-name data-aggregator |

### Step 4.5: Create Task Definitions — `ecs/task-definition.json`

| Sub-task | Description |
|----------|-------------|
| 4.5.1 | Define Fargate task: api and worker containers |
| 4.5.2 | Set DATABASE_URL, REDIS_URL, S3_BUCKET from RDS/ElastiCache |
| 4.5.3 | Configure CloudWatch logs (awslogs) |

### Step 4.6: Alternative — EC2 with Docker Compose

| Sub-task | Description |
|----------|-------------|
| 4.6.1 | Launch EC2 (Amazon Linux 2023, t3.medium) |
| 4.6.2 | Install Docker, Docker Compose, git |
| 4.6.3 | Clone repo, copy .env.example to .env, fill values |
| 4.6.4 | Run docker-compose up -d |
| 4.6.5 | Open port 80 in security group |

---

## Phase 5: GitHub Actions CI/CD — ~1–2 hours

### Step 5.1: AWS Setup for CI/CD

| Sub-task | Description |
|----------|-------------|
| 5.1.1 | Create IAM user github-actions-deployer |
| 5.1.2 | Attach AmazonEC2ContainerRegistryPowerUser |
| 5.1.3 | Attach AmazonECS_FullAccess |
| 5.1.4 | Create access key |

### Step 5.2: GitHub Secrets

| Sub-task | Description |
|----------|-------------|
| 5.2.1 | Add AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY |
| 5.2.2 | Add AWS_REGION, AWS_ACCOUNT_ID |
| 5.2.3 | Add OPENWEATHER_API_KEY, NEWSAPI_API_KEY |
| 5.2.4 | Add EC2_HOST, EC2_SSH_KEY (if using EC2) |

### Step 5.3: CI/CD Workflow — `.github/workflows/deploy.yml`

**Option A: ECR + ECS Fargate**

| Sub-task | Description |
|----------|-------------|
| 5.3.1 | Trigger on push to main |
| 5.3.2 | Configure AWS credentials, ECR login |
| 5.3.3 | Build and push API, worker, frontend images |
| 5.3.4 | Update ECS task definition with new image tags |
| 5.3.5 | Register new task definition, update ECS service |
| 5.3.6 | Wait for services-stable |

**Option B: ECR + EC2 (document-recommended for one-day)**

| Sub-task | Description |
|----------|-------------|
| 5.3.1 | Trigger on push to main |
| 5.3.2 | Build-and-push job: build and push API, frontend to ECR |
| 5.3.3 | Deploy job: SSH to EC2, ECR login, docker-compose pull, up -d --force-recreate |
| 5.3.4 | docker image prune -f |

---

## Phase 6: Testing & Polish — ~1–2 hours

### Step 6.1: Manual Integration Test

| Sub-task | Description |
|----------|-------------|
| 6.1.1 | POST /api/jobs with sources ["weather","news"], parameters {city, topic} |
| 6.1.2 | Poll GET /api/jobs/{job_id} for status |
| 6.1.3 | GET /api/jobs/{job_id}/result when COMPLETED |

### Step 6.2: Verify Celery Pipeline

| Sub-task | Description |
|----------|-------------|
| 6.2.1 | Watch docker compose logs -f worker |
| 6.2.2 | Confirm fetch_weather, fetch_news, aggregate_results task flow |

### Step 6.3: Verify S3

| Sub-task | Description |
|----------|-------------|
| 6.3.1 | Run aws s3 ls s3://data-aggregator-results/reports/ --recursive |

### Step 6.4: Quick Unit Test (optional) — `backend/tests/test_api.py`

| Sub-task | Description |
|----------|-------------|
| 6.4.1 | test_health: GET /health returns 200, {"status":"ok"} |
| 6.4.2 | test_create_job_invalid_source: POST with invalid source returns 400 |
| 6.4.3 | test_create_job_valid: POST with weather, mocked pipeline, returns 200, status PENDING |
| 6.4.4 | Run: cd backend && pip install pytest && pytest tests/ -v |

---

## File Tree (from document)

```
data-aggregator/
├── .env
├── .gitignore
├── docker-compose.yml
├── .github/workflows/deploy.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   └── tasks.py
│   └── tests/
│       └── test_api.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    └── src/
        ├── App.jsx
        ├── App.css
        ├── api.js
        └── main.jsx
```

---

## .gitignore (from document)

```
.env
__pycache__/
*.pyc
node_modules/
dist/
.venv/
```
