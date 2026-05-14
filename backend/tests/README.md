# AI Writer API Tests

This directory contains comprehensive API tests for the AI Writer backend endpoints.

## Test Structure

```
tests/
├── __init__.py           # Package marker
├── conftest.py           # Test fixtures and configuration
├── test_writer_api.py    # Tests for drafts, generate, templates, stats
└── test_content_api.py   # Tests for existing content endpoints
```

## Test Categories

### `test_writer_api.py`

Comprehensive tests for new Writer endpoints:

- **TestDraftsEndpoints**: CRUD operations for drafts
  - List drafts (with pagination, filtering)
  - Get single draft
  - Delete draft
  - Batch delete drafts
  - Authorization checks

- **TestGenerateEndpoint**: Content generation
  - Generate with source content
  - Generate with source URL
  - Validation errors
  - Mocked LLM calls
  - Database draft creation

- **TestTemplatesEndpoint**: Template listing
  - List all templates
  - Filter by category
  - Pagination

- **TestStatsEndpoint**: Writer statistics
  - Stats calculation
  - Today's/week/month counts
  - User isolation

- **TestWriterAPIIntegration**: End-to-end workflows
- **TestWriterAPISecurity**: Security validation
- **TestWriterAPIPerformance**: Performance benchmarks

### `test_content_api.py`

Tests for existing content endpoints:

- Content CRUD operations
- Agent chat endpoint
- Pagination and filtering

## Fixtures

Key fixtures in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `test_db_engine` | In-memory SQLite engine for isolation |
| `db_session` | Database session per test |
| `client` | FastAPI TestClient with dependency overrides |
| `test_user` | Authenticated test user |
| `auth_headers` | Bearer token headers for API calls |
| `test_draft` | Single test draft |
| `test_drafts` | Multiple test drafts |
| `test_template` | Single test template |
| `test_templates` | Multiple test templates |
| `mock_openai_response` | Mocked OpenAI API response |
| `mock_httpx_response` | Mocked httpx response for URL fetching |

## Setup

1. Install test dependencies:

```bash
pip install -r requirements-test.txt
```

Or install directly:

```bash
pip install pytest pytest-asyncio httpx
```

2. Set up environment (optional):

```bash
# Create .env.test with test-specific settings
OPENROUTER_API_KEY=test-key  # Will be mocked anyway
```

## Running Tests

### Run all tests

```bash
cd backend
pytest tests/ -v
```

### Run specific test file

```bash
pytest tests/test_writer_api.py -v
```

### Run specific test class

```bash
pytest tests/test_writer_api.py::TestDraftsEndpoints -v
```

### Run specific test

```bash
pytest tests/test_writer_api.py::TestDraftsEndpoints::test_list_drafts_empty -v
```

### Run with coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run with markers

```bash
# Run only integration tests
pytest tests/ -m integration -v

# Run only security tests
pytest tests/ -m security -v
```

## Mock Strategy

### OpenAI Mock

```python
with patch("app.services.openai.OpenAI") as mock_openai:
    mock_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "# Generated content"
    mock_instance.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_instance

    response = client.post("/api/writer/generate", ...)
```

### URL Fetching Mock

```python
with patch("app.services.crawler.httpx.AsyncClient") as mock_client:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>...</html>"
    mock_client.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

    response = client.post("/api/writer/generate", ...)
```

## Test Database

Tests use an **in-memory SQLite database** for isolation:

- Each test gets a fresh database
- No data persists between tests
- Foreign key constraints are enabled
- Models are automatically created before each test

## Expected API Endpoints

The tests expect the following endpoints to be implemented:

```
GET    /api/writer/drafts/           - List drafts (paginated, filterable)
GET    /api/writer/drafts/{id}       - Get single draft
DELETE /api/writer/drafts/{id}       - Delete draft
POST   /api/writer/drafts/batch-delete - Batch delete drafts
POST   /api/writer/generate           - Generate content (async)
GET    /api/writer/templates/        - List templates
GET    /api/writer/stats             - Get writer statistics

GET    /api/writer/content/          - List content
POST   /api/writer/content/          - Create content
GET    /api/writer/content/{id}      - Get content
PUT    /api/writer/content/{id}      - Update content
DELETE /api/writer/content/{id}      - Delete content

POST   /api/writer/agent/chat        - Agent chat (existing)
```

## Authentication

All endpoints require Bearer token authentication:

```python
headers = {"Authorization": "Bearer <jwt_token>"}
```

The `auth_headers` fixture provides a valid token for test user.

## Notes

- Tests are designed to be **independent** and **order-independent**
- Each test cleans up after itself
- Tests validate **authorization** (users only see their own data)
- Security tests check for SQL injection, invalid tokens, etc.
- Performance tests verify response times are within SLA
