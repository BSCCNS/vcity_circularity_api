# Fast_API_sk
**Generic skeleton for API using FastAPI.**

## Instructions

1. Clone the repository.
2. Create a virtual environment with `python -m venv venv`.
3. Enter into the backend folder `cd backend`
4. Install the requirements with `pip install -r requirements.txt`.
5. Run the server with uvicorn `uvicorn main:app`. Add the flag `--reload` for automatic reloading when testing.


## Overview

```bash
├── backend/
│   ├── auth/
│   │   ├── auth.py
│   │   ├── hashing.py
│   ├── core/
│   │   ├── config.py
│   │   ├── endpoints.py 
│   │   ├── routers.py    
│   ├── data/
│   │   ├── fake_db.py
│   ├── schemas/
│   │   ├── token_schema.py
│   │   ├── user_schema.py
├── main.py
├── requirements.txt
├── README.md
```
The API is modular. Basic configuration is in the core folder (settings and a file collecting all the router points). Different functionalities are implemented in their corresponding folder. Each one through a router object. The `main.py`file calls the application and connects the routers.


## Folder description

`auth`: Contains functions for user authentication using an Ouath2 scheme. It implements password hashing and identification throug a JWT token.

`core`: Contains core functions for the API. In particular, it routes together all routers in the different code pieces. It also provides a configuration file with the API settings.

`data`: Contains external data for the API. In this barebones version, it only contains a fake database file implemented through a dictionary.

`schemas`: Contains pydantic schemas for the different variables used.
