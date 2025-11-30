# Virtual AI Company MVP

Monorepo with FastAPI backend and Next.js frontend that simulates a virtual AI company generating MVP artifacts. The backend orchestrates CEO/developer agents, streams logs over WebSocket, manages project files, and can publish generated code to GitHub. The frontend visualises file trees, DAG execution, editor, and GitHub publishing.

## Prerequisites

- Python 3.11+
- Node.js 18+

## Quick start

```bash
make init    # install Python packages and frontend dependencies
make dev     # starts uvicorn and next dev together
```

`make dev` spawns both servers; stop them with `Ctrl+C`. During development the backend listens on `http://localhost:8000` and the frontend on `http://localhost:3000`.

### Useful environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECTS_ROOT` | Directory for generated artifacts | `./projects` |
| `LLM_MODE` | `mock` or `ollama` | `mock` |
| `LLM_SEMAPHORE` | Max concurrent LLM calls | `3` |
| `GITHUB_API_URL` | GitHub API base URL | `https://api.github.com` |

Set `LLM_MODE=ollama` to invoke the local Ollama CLI instead of the mock adapter.

## API reference (curl)

Create project:

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"title":"test","description":"demo","target":"web"}'
```

Connect to WebSocket (example with `wscat`):

```bash
wscat -c ws://localhost:8000/ws/projects/<project_id>
```

List files:

```bash
curl http://localhost:8000/api/projects/<project_id>/files
```

Download ZIP:

```bash
curl -OJ http://localhost:8000/api/projects/<project_id>/download
```

Publish to GitHub:

```bash
curl -X POST http://localhost:8000/api/projects/<project_id>/publish/github \
  -H "Content-Type: application/json" \
  -d '{"token":"<PAT>","repo_name":"repo-name","private":false}'
```

### Tests

```bash
source .venv/bin/activate
pytest
```

## Notes

- Projects are stored under `./projects/<project_id>` alongside `meta.json` and cached `project.zip`.
- WebSocket supports `{"type":"command","command":"stop"}` to cancel orchestration.
- Publishing never stores the provided PAT; it is used only for the current request.

