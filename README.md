# flowchat

## Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then fill in the values.

### Example `.env`

```env
# debug
DEBUG=False
LOGGING_LEVEL="INFO"

# cors middleware
FRONTEND_URL="http://localhost:3000"

# Chat model
API_KEY="your_actual_key_here"
LLM_MODEL="openai/gpt-oss-20b"
MODEL_URL="https://api.groq.com/openai/v1"
MODEL_TEMPERATURE=0
MAX_INPUT_TOKENS=16384
MAX_OUTPUT_TOKENS=8192

# Tools calling limit
TOOL_CALLING_LIMIT=32
SUMMERIZATION_MIDDLEWARE_LIMIT="0.7"

# Data staging limits
MAX_DOCUMENTS_STAGING_LIMIT=10

# database
DATABASE_USERNAME="postgres"
DATABASE_PASSWORD="postgres"
DATABASE_NAME="search-agent"
DATABASE_HOST="localhost"
DATABASE_PORT=5432

# serper
SERPER_API_KEY="api_key"
SERPER_API_URL="https://google.serper.dev/search"
SERPER_DEFAULT_COUNTRY="in"  # india
SERPER_DEFAULT_LANGUAGE="en"  # english
SERPER_DEFAULT_DATE_RANGE="qdr:w"  # past week
SERPER_API_RESULTS_MAX_LIMIT=5

# crawl4ai
CRAWL4AI_HOST="http://localhost:11235"

# langgraph postgres checkpointer (follow readme to generate aes token)
LANGGRAPH_AES_KEY="your-32-byte-base64-encoded" 
```

## Start fastapi server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Langgraph postgres checkpointer

### Generate and Store a Persistent Key (Recommended for Production)

Step 1: Generate a key
Run this Python snippet to generate a key:

```python
import secrets
key = secrets.token_bytes(16)
print(key.hex())
```

Or use bash:

```bash
python3 -c "import secrets; print(secrets.token_bytes(16).hex())"
```

This will output something like:

```txt
5e5563e987a5c71e883d55104d0ae87d
```

Step 2: Add to your .env file

```env
LANGGRAPH_AES_KEY=5e5563e987a5c71e883d55104d0ae87d
```

## Chat conversation body

```md
NORMAL 
    parent_message_id: Optional[UUID]
    context: 
        type: normal
        start: Optional[int] = None
        end: Optional[int] = None

REGENERATE 
    parent_message_id: Optional[UUID]
    context: 
        type: regenerate
        um_id: Optional[UUID] = None
        start: Optional[int] = None
        end: Optional[int] = None

FOLLOW_UP 
    parent_message_id: Optional[UUID]
    context: 
        type: followup
        text: str
        start: Optional[int] = None
        end: Optional[int] = None

```

## TODO

backend

- [ ] add feedback apis
- [ ] langfuse implementation
- [ ] custon recursive sumerization middleware

UI

- [ ] nextjs and reactflow
