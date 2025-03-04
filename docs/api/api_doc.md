# SocksAI API Documentation

## Overview

The `api.py` file is the main FastAPI backend responsible for handling API requests, routing, and middleware configuration for `SocksAI`. It facilitates stock sentiment analysis, scheduling, and backend services for the Streamlit frontend.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **fastapi**: Framework for building APIs.
- **uvicorn**: ASGI server for running the FastAPI application.
- **logging & colorlog**: For tracking system activity with color-coded logs.
- **fastapi.middleware.cors.CORSMiddleware**: Enables Cross-Origin Resource Sharing (CORS).
- **routes**: Custom module containing API route definitions.

## Configuration

### Logging Setup

The logging system is configured with `colorlog` for enhanced readability:

```python
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - "
    "%(module)s - %(funcName)s - %(lineno)d: "
    "%(message_log_color)s%(message)s%(reset)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
```

### FastAPI Initialization

The FastAPI app is initialized with a title, description, and version:

```python
api = FastAPI(
    title="SocksAI API",
    description="API for stock sentiment analysis and scheduling",
    version="1.0.0",
)
```

### CORS Configuration

CORS middleware is enabled to allow cross-origin requests:

```python
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Routing

The API routes are imported from an external `routes` module:

```python
from routes import router
api.include_router(router)
```

## Running the API

To start the FastAPI server using Uvicorn:

```bash
uvicorn api:api --reload
```

## Example Usage

### Fetch API Documentation

Once the API is running, access the interactive docs at:

- OpenAPI UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Redoc UI: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Conclusion

The `SocksAI API` serves as the backend for stock sentiment analysis and scheduling. It provides a structured, scalable, and well-logged API using FastAPI, enabling seamless integration with frontend applications.
