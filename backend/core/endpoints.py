# endpoints.py
from typing import Annotated
from fastapi import Depends, APIRouter
from schemas import schemas
import asyncio
import logging
from auth.auth import check_token
import datetime
import jwt

logger = logging.getLogger('uvicorn.error')
tasks = {}

router = APIRouter()


###########
#ENDPOINTS
###########

# Endpoint to check tasks running
@router.get("/tasks")
async def check_tasks(token: Annotated[str, Depends(check_token)]):
    '''
    Checks which tasks created by the user are being executed in the backend.
    Parameters:
        token (str): Authenticaton token of bearer type.
    Return:
        list[str]: List of the task IDs being executed.
    '''
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    user = payload['username']

    list_tasks =[]

    for key in tasks.keys():
        task_ob = tasks[key]
        if task_ob['user'] == user:
            list_tasks.append(key)

    return list_tasks

# Endpoint to run the task 
@router.post("/run")
async def run_model(input: schemas.InputData, token: Annotated[str, Depends(check_token)]):
    '''
    Starts execution of a model task.
    Parameters:
        input (JSON): Input parameters for the model (see InputData schema).
        token (str): Authenticaton token of bearer type.
    Return:
        (JSON): ID of the task.
    '''
    #Check user
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    user = payload['username']
    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')

    async def model_task(task_id):
        try:
            await asyncio.sleep(10)  # Fake wait. Replace with model execution.
            logger.info(f'Run with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Run with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(model_task(task_id))
    task_ob = schemas.ModelTask(task=task, user=user, time=time)
    tasks[task_id] = task_ob
    return {"task_id": task_id, }


# Endpoint to stop the task
@router.delete("/stop/{task_id}")
async def stop_model(task_id: str, token: Annotated[str, Depends(check_token)]):
    '''
    Stops a running task.
    Parameter:
        task_id (str): ID of the task to stop.
        token (str): Authenticaton token of bearer type.
    Return:
        (JSON): Confirmation of cancellation.
    '''
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    user = payload['username']
    task_ob = tasks.get(task_id)

    if not 'user'==task_ob['user']:
        raise HTTPException(status_code=404, detail="Access forbidden")


    task = task_ob['task']
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
