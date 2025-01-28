# endpoints.py
from typing import Annotated
from fastapi import Depends, APIRouter
from auth.auth import *
from schemas import schemas
import asyncio
import logging

logger = logging.getLogger('uvicorn.error')
tasks = {}

router = APIRouter()


###########
#ENDPOINTS
###########

# Endpoint to check tasks running
@router.get("/tasks")
async def check_tasks():
    '''
    Checks which tasks are being executed in the backend.
    Return:
        list[str]: List of the tasks being executed.
    '''
    return list(tasks.keys())

# Endpoint to run the task 
@router.post("/run")
async def run_model(input: schemas.Input_Data):
    '''
    Starts execution of a model task.
    Parameters:
        input (JSON): Input parameters for the model (see Input_Data schema).
    Return:
        (JSON): ID of the task.
    '''

    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')

    async def model_task(task_id):
        try:
            await asyncio.sleep(10)  # Fake wait. Replace with model execution.
            logger.info(f'Run with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Run with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    task = asyncio.create_task(model_task(task_id))
    tasks[task_id] = task
    return {"task_id": task_id}


# Endpoint to stop the task
@router.delete("/stop/{task_id}")
async def stop_model(task_id: str):
    '''
    Stops a running task.
    Parameter:
        task_id (str): ID of the task to stop.
    Return:
        (JSON): Confirmation of cancellation.
    '''

    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.done():
        raise HTTPException(status_code=400, detail="Task already completed")

    task.cancel()  # Cancel the running task
    try:
        await task  # Wait for the task to handle the cancellation
    except asyncio.CancelledError:
        logger.info(f'Task {task_id} successfully cancelled')
    finally:
        tasks.pop(task_id, None)  # Clean up the task from the dictionary

    return {"status": "cancelled", "task_id": task_id}
