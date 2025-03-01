import logging
import colorlog

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router


# Configure logging
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s - "
    "%(module)s - %(funcName)s - \033[37m%(lineno)d%(reset)s: "
    "%(message_log_color)s%(message)s%(reset)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
    secondary_log_colors={
        "message": {
            "DEBUG": "cyan",
            "INFO": "light_green",
            "WARNING": "light_yellow",
            "ERROR": "light_red",
            "CRITICAL": "bold_red",
        },
    },
)


if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Initialize FastAPI
api = FastAPI(
    title="SocksAI API",
    description="API for stock sentiment analysis and scheduling",
    version="1.0.0",
)

# Enable CORS
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
    ],
    allow_headers=["*"],
)

api.include_router(router)

logger.info("API loaded successfully.")

# uvicorn api:api --reload