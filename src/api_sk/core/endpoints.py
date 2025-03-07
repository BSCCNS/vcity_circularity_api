# endpoints.py
from typing import Annotated
from fastapi import Depends, APIRouter
from api_sk.auth.auth import check_token
import logging
import uuid
import datetime
import asyncio
from api_sk.schemas import schemas

router = APIRouter()
logger = logging.getLogger("uvicorn.error")  # Logger for logging info
tasks = {}  # Dictionary to store the queue of tasks running/completed

# Metadata for the tags in the documentation
tags_metadata = [
    {
        "name": "Model endpoints",
        "description": "Operations from the model.",
    },
    {
        "name": "Task management",
        "description": "Operations to manage the tasks being executed in the backend.",
    },
    {
        "name": "User management",
        "description": "Operations to manage the tasks being executed in the backend.",
    },
]


def after_task_done(task, task_id):
    """
    After a task is finished, it changes its status in the queue to completed.

    ### Parameters:
    - task (asyncio.task): Task being executed.
    - task_id (str): ID of the task, acting as the key of a dictionary.
    """

    tasks[task_id].status = "Completed"


# Generic example of a GET endpoint


@router.get("/hello", summary="Generic endpoint.", tags=["Model endpoints"])
async def hello_api(token: Annotated[str, Depends(check_token)]):
    """'
    GET call to /. Returns a hello message. User must be authenticated.

    """
    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f"Starting run with task ID: {task_id}")

    async def setup_task(task_id):
        try:
            await asyncio.to_thread(
                lambda x: print("By the Power of Grayskull! I have the power!"), 1
            )

            logger.info(f"Run with task ID: {task_id} finished")
        except asyncio.CancelledError:
            logger.info(f"Run with task ID: {task_id} cancelled")
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())

    task = asyncio.create_task(setup_task(task_id))
    task_ob = schemas.ModelTask(task=task, start_time=time, type="Example")
    tasks[task_id] = task_ob
    task.add_done_callback(lambda t: after_task_done(t, task_id))
    return {"task_id": task_id}


####### Task Management endpoints ###########
#####################
###Task management###
####################
# Endpoint to check tasks running
@router.get(
    "/list",
    summary="Query running and completed tasks.",
    tags=["Task management"],
)
async def check_tasks():
    """
    Checks which tasks are being executed or finished in the backend.
    """

    return tasks


# Endpoint to check the status of a specific task
@router.get(
    "/status/{task_id}",
    summary="Check the status of a given task.",
    tags=["Task management"],
)
async def status(task_id: str):
    """
    Checks the current status of a task by ID.

    ### Parameters:
        - Task_id (str): ID of the task to check.
    """
    try:
        task_ob = tasks.get(task_id)
    except:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_ob.task

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"status": task_ob.status}


# Endpoint to stop the task
@router.delete(
    "/stop/{task_id}",
    summary="Stop a running task.",
    tags=["Task management"],
)
async def stop_model(task_id: str):
    """
    Stops a running task, provided its ID.

    ### Parameters:
        - Task_id (str): ID of the task to stop.
    """

    try:
        task_ob = tasks.get(task_id)
    except:
        raise HTTPException(status_code=404, detail="Task not found")

    task = task_ob.task

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.done():
        raise HTTPException(status_code=400, detail="Task already completed")

    task.cancel()  # Cancel the running task

    try:
        await task  # Wait for the task to handle the cancellation
    except asyncio.CancelledError:
        logger.info(f"Task {task_id} successfully cancelled")
    finally:
        tasks.pop(task_id, None)  # Clean up the task from the dictionary

    return {"status": "Task cancelled", "task_id": task_id}
