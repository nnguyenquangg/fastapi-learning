# Learning Resources

## Official docs (ưu tiên)

- **FastAPI**: https://fastapi.tiangolo.com — doc chất lượng, có tutorial
- **Pydantic V2**: https://docs.pydantic.dev/latest/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Python**: https://docs.python.org/3/
- **PostgreSQL**: https://www.postgresql.org/docs/

## Sách (nếu thích)

- **"Architecture Patterns with Python"** — Harry Percival & Bob Gregory
  - DDD, repository pattern, CQRS applied với Python
  - Free online: https://www.cosmicpython.com/

- **"Designing Data-Intensive Applications"** — Martin Kleppmann
  - Không phải Python, nhưng hiểu DB/distributed → build backend tốt hơn

- **"Effective Python"** — Brett Slatkin
  - 90 tip Python idiomatic

## Video / Course

- **ArjanCodes** (YouTube) — pattern, architecture
- **mCoding** (YouTube) — deep Python internals
- **TestDriven.io** — FastAPI + Docker tutorials (trả phí)
- **Talk Python To Me** podcast

## Blog / Newsletter

- **Real Python** — tutorial chất lượng
- **Awesome FastAPI** (GitHub): https://github.com/mjhea0/awesome-fastapi
- **PyCoder's Weekly** — newsletter hàng tuần

## Community

- **FastAPI Discord**: link trên trang chủ
- **r/FastAPI**: https://www.reddit.com/r/FastAPI/
- **Python Discord**: https://pythondiscord.com/
- **FastAPI Experts** (github): danh sách người giỏi để theo dõi

## Repo mẫu để đọc

Học từ code người khác là cách rút kinh nghiệm nhanh:

- **full-stack-fastapi-template** (official): https://github.com/fastapi/full-stack-fastapi-template
  - FastAPI + React + PostgreSQL, best practices
- **fastapi-best-practices**: https://github.com/zhanymkanov/fastapi-best-practices
  - Collection pattern thực tế
- **fastapi-users**: https://github.com/fastapi-users/fastapi-users
  - Thư viện auth chuẩn, đọc source học cách tổ chức

## Tools quan trọng

### Editor/IDE
- **VSCode** + Python extension + Pylance + Ruff
- **PyCharm Professional** (trả phí) — hỗ trợ FastAPI tốt nhất
- **Cursor** hoặc **Zed** — nếu muốn AI-assisted

### Package manager
- **uv** (Astral) — nhanh, hiện đại, mình khuyến khích
- **Poetry** — phổ biến trước uv
- **pip-tools** — nhẹ

### Quality tools
- **Ruff** — lint + format (rất nhanh, thay cho black + flake8 + isort)
- **mypy** — static type check
- **pyright** — type check của Microsoft (nhanh, có trong Pylance)

### Testing
- **pytest** + plugin: pytest-asyncio, pytest-cov, pytest-mock, pytest-xdist
- **httpx** — HTTP client cho test
- **factory-boy** — tạo test data
- **freezegun** — mock datetime

### Database tools
- **TablePlus** (macOS) — nhẹ, đẹp
- **DBeaver** — full-feature, free
- **pgcli** — terminal, có autocomplete
- **pg_dump** — backup

### API testing
- **Bruno** — open source Postman
- **httpie** — CLI đẹp hơn curl
- **Swagger UI** — FastAPI tự cung cấp ở `/docs`

### Monitoring (production)
- **Sentry** — error tracking, free tier đủ dùng
- **Grafana Cloud** — log + metric, free tier
- **Better Stack** — all-in-one, UX tốt
- **Prometheus + Grafana** — self-host

### Deployment
- **Railway** — dễ nhất, DB + Redis kèm theo
- **Fly.io** — control nhiều hơn, global
- **Render** — giống Railway
- **Cloud Run** (GCP) — serverless container
- **Docker Compose + VPS** — nếu thích tự quản

## Stack tham khảo cho startup

```
Runtime:     Python 3.12 + FastAPI + uvicorn
Package:     uv
DB:          PostgreSQL 16 + SQLAlchemy 2.0 (async) + Alembic
Cache:       Redis 7
Queue:       Taskiq hoặc arq (async-native)
Auth:        JWT (access + refresh rotate) + passlib[bcrypt]
Storage:     S3 compat (MinIO local, AWS/R2/Backblaze prod)
Search:      Postgres full-text (< 100k docs) → Meilisearch/Typesense
Observe:     Sentry + structured JSON log → Grafana/Better Stack
Deploy:      Docker + Railway/Fly.io + GitHub Actions CI
```

## Khi nào học thêm gì

Sau khi hoàn thành roadmap này, tùy hướng bạn đi:

### Scale / Performance
- Caching patterns (Redis + cache-aside)
- Database optimization (partition, replication)
- Load testing (k6, Locust)
- Async patterns sâu (trio, anyio)

### Architecture
- Domain-Driven Design
- Event-driven (Kafka, RabbitMQ)
- CQRS + Event Sourcing
- Microservices (chỉ khi thật cần)

### Infrastructure
- Kubernetes basics
- Terraform / Pulumi
- CI/CD nâng cao (ArgoCD, Flux)
- Observability sâu (OpenTelemetry)

### AI integration
- LLM API (OpenAI, Anthropic)
- RAG (LangChain, LlamaIndex, Haystack)
- Vector DB (pgvector, Qdrant, Weaviate)
- Fine-tuning

## Nguyên tắc học lâu dài

1. **Build > Read**: 1 project nhỏ hoàn thành > 10 tutorial đọc dở
2. **Teach to learn**: viết blog, share code — forcing function
3. **Read source**: khi dùng library lạ, đọc source 30p trước khi google
4. **Stay updated**: theo 2-3 người expert, không cần follow hết
5. **Lateral move**: học 1 framework khác (Go, Rust) để hiểu Python sâu hơn

Chúc học vui! 🎉
