from fastapi import APIRouter, HTTPException
from modules.daily_stock_scheduler_agent import DailyStockSchedulerAgent
import logging

logger = logging.getLogger("api")

# Create a router
router = APIRouter()

# Initialize the Scheduler Agent
scheduler_agent = DailyStockSchedulerAgent()


@router.get("/", tags=["Home"])
async def home():
    """
    Home route to check if the API is running.
    """
    logger.info("Home route accessed")
    return {
        "message": "Welcome to SocksAI!",
        "status": "SocksAI server is running!",
    }


@router.post("/start_scheduler", tags=["Scheduler"])
async def start_schedule():
    """
    Start the daily stock sentiment analysis scheduler.
    """
    logger.info("Received request to start the scheduler.")
    try:
        scheduler_agent.start_agents()
        logger.info("Scheduler started successfully.")
        return {"success": True, "message": "Scheduler started successfully."}
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.post("/stop_scheduler", tags=["Scheduler"])
async def stop_schedule():
    """
    Stop the daily stock sentiment analysis scheduler.
    """
    logger.info("Received request to stop the scheduler.")
    try:
        scheduler_agent.stop_agents()
        logger.info("Scheduler stopped successfully.")
        return {"success": True, "message": "Scheduler stopped successfully."}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})


@router.get("/scheduler_status", tags=["Scheduler"])
async def get_scheduler_status():
    """
    Get the current status of the stock sentiment analysis scheduler.
    """
    logger.info("Received request to get scheduler status.")
    try:
        status = scheduler_agent.get_scheduler_status()
        logger.info(f"Scheduler Status: {status}")
        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})

@router.get("/reload_stocks", tags=["Daily Stocks"])
async def reload_stocks():
    """
    Reload the stock list.
    """
    logger.info("Received request to reload stocks.")
    try:
        scheduler_agent.reload_stocks()
        logger.info("Stocks reloaded successfully.")
        return {"success": True, "message": "Stocks reloaded successfully."}
    except Exception as e:
        logger.error(f"Error reloading stocks: {str(e)}")
        raise HTTPException(status_code=500, detail={"success": False, "error": str(e)})