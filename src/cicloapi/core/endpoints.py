# endpoints.py

from typing import Annotated
from fastapi import Depends, APIRouter
from cicloapi.schemas import schemas
import asyncio
import logging
from cicloapi.auth.auth import check_token
from fastapi.responses import FileResponse
import datetime
import uuid
import os

current_working_directory = os.getcwd()

logger = logging.getLogger('uvicorn.error')
tasks = {}

router = APIRouter()



###########
#ENDPOINTS
###########

# Endpoint to check tasks running
@router.get("/list")
async def check_tasks(token: Annotated[dict, Depends(check_token)]):
    '''
    Checks which tasks created by the user are being executed in the backend.
    Parameters:
        token (dict): Decoded authentication token.
    Return:
        list[dict]: Dictionary containing the tasks. Task IDs are used as keys and values indicate starting time.
    '''

    user = token['user']

    list_dict ={}

    for key in tasks.keys():
        task_ob = tasks[key]
        if task_ob.user == user:
            list_dict[key] = task_ob.start_time

    return list_dict

# Endpoint to run the task 
@router.post("/run")
async def run_model(input: schemas.InputData, token: Annotated[dict, Depends(check_token)]):
    '''
    Starts execution of a model task.
    Parameters:
        input (JSON): Input parameters for the model (see InputData schema).
        token (dict): Decoded authenticaton token.
    Return:
        (JSON): ID of the task.
    '''
    #Check user
    
    user = token['user']
    task_id = str(uuid.uuid4())  # Generate a unique ID for the task
    logger.info(f'Starting run with task ID: {task_id}')

    async def model_task(task_id):
        try:
            await asyncio.sleep(1000)  # Fake wait. Replace with model execution.
            logger.info(f'Run with task ID: {task_id} finished')
        except asyncio.CancelledError:
            logger.info(f'Run with task ID: {task_id} cancelled')
            raise  # Propagate the cancellation exception

    time = str(datetime.datetime.now())
    task = asyncio.create_task(model_task(task_id))
    task_ob = schemas.ModelTask(task=task, user=user, start_time=time)
    tasks[task_id] = task_ob
    return {"task_id": task_id}


# Endpoint to stop the task
@router.delete("/stop/{task_id}")
async def stop_model(task_id: str, token: Annotated[dict, Depends(check_token)]):
    '''
    Stops a running task.
    Parameters:
        task_id (str): ID of the task to stop.
        token (dict): Decoded authenticaton token.
    Return:
        (JSON): Confirmation of cancellation.
    '''
    
    task_ob = tasks.get(task_id)
    
    try:
        user = token['user']
    except:
        raise HTTPException(status_code=404, detail="No task with ID "+ task_id)
    
    if not user==task_ob.user:
        raise HTTPException(status_code=404, detail="Access forbidden")

    task = task_ob.task
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

    return {"status": "task cancelled", "task_id": task_id}


# Endpoint to download the map

@router.get("/map/{task_id}")
async def download_map(task_id: str, token: Annotated[dict, Depends(check_token)]):
    '''
    Streams the download of the map stored in disk for the task with ID equal to task_id.
    Parameters:
        task_id (str): ID of the task to stop.
        token (dict): Decoded authenticaton token.
    Return:
        (FileResponse): Map file in jpeg format.

    '''

    task_ob = tasks.get(task_id)
    
    try:
        user = token['user']
    except:
        raise HTTPException(status_code=404, detail="No task with ID "+ task_id)
    
    if not user==task_ob.user:
        raise HTTPException(status_code=404, detail="Access forbidden")
    
    file_path = os.path.join(current_working_directory, 'src', 'cicloapi', 'data', 'images.jpeg')
    
    return FileResponse(file_path)
