# AGENTS – Image Search Application

## 1. Project Overview
A micro‑services system for text‑based image search.  
Key goals: high‑throughput ingestion, CLIP‑based embedding search, strict deduplication, and real‑time metrics.

## 2. Codebase Map
| Folder | Purpose |
|--------|---------|
| `api_service/`            | FastAPI entrypoint – receives search queries, calls Elasticsearch |
| `file_reader_service/`    | Reads URL lists, pushes to RabbitMQ, Bloom‑filter + Redis dedupe |
| `downloader_service/`     | Downloads images, stores metadata in Postgres, publishes embed jobs |
| `embedding_service/`      | Generates CLIP embeddings, indexes into Elasticsearch |
| `frontend_service/`       | React UI (search box, grid view, dark / light theme) |
| `scripts/`                | Helper scripts (`run_all_tests.sh`, dataset tools, etc.) |
| Infra root files          | `docker-compose.yml`, `.env.example`, Prometheus / Grafana configs |

## 3. Environment & Setup (agent instructions)
1. **Clone & install**  
   ```bash
   git clone https://github.com/hassonor/image-search-app.git
   cd image-search-app
   ./run_and_install.sh     # sets up virtual‑env, pulls Docker images
   ```
2. **Spin up dependencies** (Elasticsearch, Postgres, RabbitMQ, Redis, Prometheus, Grafana):  
   ```bash
   docker compose up -d
   ```

## 4. Build, Quality & Test
| Check | Command | Expectation |
|-------|---------|-------------|
| Unit + integration tests (all services) | `./run_all_tests.sh` | **Must pass** |
| Python style (Black + Ruff + Isort) | `./check-code-quality.sh` | No warnings |
| Front‑end lint / format | `npm run lint && npm run format` inside `frontend_service/` | No changes needed |
| Type checking (optional) | `mypy **/*.py` | 0 errors |

The agent **must** run the quality script *and* full test suite before considering a task done.  
If tests fail, debug and iterate until green.

## 5. Coding Conventions
* **Python:** Black (line‑length 88), Ruff rules from `ruff.toml`, Isort profile = `black`.
* **Type hints:** required for new Python code.
* **React/TS:** Prettier 2‑space indent; favor functional components & hooks.
* **Commits / PRs:** Conventional Commits (`feat:`, `fix:`, `refactor:`…) and include linked Issue/Jira key.

## 6. Agent Behaviour Guidelines
* Focus on **feature work, bug‑fixing, refactors, or test authoring**.  
* When adding a feature: create/extend tests and update docs where relevant.  
* Never commit `.env.*` or secrets.  
* Large binary/image assets → object storage, not Git.  
* Open a new branch, push, and create a PR. Include:  
  * Problem statement  
  * Solution summary  
  * “How to test” steps  
* If quality or tests fail in CI, keep iterating until they pass.

## 7. Optional Sub‑agents
| Name | Scope | Notes |
|------|-------|-------|
| **UI-Agent** | Files in `frontend_service/` | Keeps UI consistent, adds unit/Jest tests |
| **Ingestion-Agent** | `file_reader_service/`, `downloader_service/` | Optimises throughput, dedupe logic |
| **Search-Agent** | `api_service/`, `embedding_service/` | Embedding & query performance |

*(If you spin up multiple Codex tasks, initialise them with these role descriptions.)*

## 8. Further Reading
* `README.md` – high‑level architecture & setup.  
* Grafana dashboards (`grafana/`) – check performance after changes.
