# SocksAI API Routes Documentation

## Overview

The `routes.py` file defines the API routes for `SocksAI`, enabling stock sentiment analysis and scheduling functionalities. It provides endpoints to manage the daily stock sentiment scheduler and monitor its status.

## Libraries and Tools Used

The following libraries and tools are utilized in the project:

- **fastapi**: Framework for creating API routes and handling requests.
- **logging**: For logging request activities and errors.
- **fastapi.HTTPException**: Used for handling API errors.
- **modules.daily_stock_scheduler_agent**: Manages stock sentiment analysis scheduling.

## Configuration

### Router Initialization

The API routes are defined under a FastAPI `APIRouter` instance:

```python
router = APIRouter()
```

### Scheduler Agent

An instance of `DailyStockSchedulerAgent` is created to handle scheduling:

```python
scheduler_agent = DailyStockSchedulerAgent()
```

## API Endpoints

### 1. Home Route

Checks if the API is running.

```python
@router.get("/", tags=["Home"])
async def home():
    return {"success": True, "message": "Welcome to SocksAI!", "status": "SocksAI server is running!"}
```

### 2. Start Scheduler

Starts the daily stock sentiment scheduler.

```python
@router.post("/start_scheduler", tags=["Scheduler"])
async def start_schedule():
    scheduler_agent.start_scheduler()
    return {"success": True, "message": "Scheduler started successfully."}
```

### 3. Stop Scheduler

Stops the daily stock sentiment scheduler.

```python
@router.post("/stop_scheduler", tags=["Scheduler"])
async def stop_schedule():
    scheduler_agent.stop_scheduler()
    return {"success": True, "message": "Scheduler stopped successfully."}
```

### 4. Get Scheduler Status

Retrieves the current scheduler status.

```python
@router.get("/scheduler_status", tags=["Scheduler"])
async def get_scheduler_status():
    status = scheduler_agent.get_scheduler_status()
    return {"success": True, "status": status}
```

### 5. Reload Stocks

Reloads the stock list.

```python
@router.post("/reload_stocks", tags=["Daily Stocks"])
async def reload_stocks():
    scheduler_agent.reload_stocks()
    return {"success": True, "message": "Stocks reloaded successfully."}
```

### 6. Toggle Scheduler

Toggles the scheduler between running and paused states.

```python
@router.post("/toggle_scheduler", tags=["Scheduler"])
async def toggle_scheduler():
    status = scheduler_agent.toggle_scheduler()
    return {"success": True, "message": f"Scheduler toggled to {status} successfully."}
```

### 7. Refresh Scheduler

Refreshes the scheduler process.

```python
@router.post("/refresh_scheduler", tags=["Scheduler"])
async def refresh_scheduler():
    scheduler_agent.refresh_scheduler()
    return {"success": True, "message": "Scheduler refreshed successfully."}
```

### 8. Get Scheduler State

Returns the current state of the scheduler.

```python
@router.get("/scheduler_state", tags=["Scheduler"])
async def get_scheduler_state():
    state = scheduler_agent.get_scheduler_state()
    return {"success": True, "state": state}
```

## Example Usage

### Starting the Scheduler

```bash
curl -X POST http://127.0.0.1:8000/start_scheduler
```

### Checking Scheduler Status

```bash
curl -X GET http://127.0.0.1:8000/scheduler_status
```

### Stopping the Scheduler

```bash
curl -X POST http://127.0.0.1:8000/stop_scheduler
```

## Conclusion

The `routes.py` file defines the API structure for managing stock sentiment analysis and scheduler operations. It ensures smooth API interactions for stock monitoring and analysis automation.
