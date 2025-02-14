from fastapi import APIRouter, HTTPException
from modules.daily_stock_scheduler_agent import DailyStockSchedulerAgent

# Create a router
router = APIRouter()

# Initialize the SchedulerAgent
scheduler_agent = DailyStockSchedulerAgent()


@router.post("/scheduler", tags=["Scheduler"])
async def schedule():
    """
    Schedule the daily stock sentiment analysis.
    """
    try:
        scheduler_agent.start_agents()

        return {"Success": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in Scheduler: {str(e)}")


@router.post("/stop_scheduler", tags=["Scheduler"])
async def stop_schedule():
    """
    Stop the daily stock sentiment analysis scheduler.
    """
    try:
        scheduler_agent.stop_agents()
        return {"message": "Scheduler stopped successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error stopping Scheduler: {str(e)}"
        )
