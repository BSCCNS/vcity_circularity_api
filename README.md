# Skeletor
**Generic skeleton for API using FastAPI.**

## Instructions

### Docker

1. Build the docker container by running `docker build -t skeletor .`.
2. Run the docker container by `docker run -p 8000:8000 skeletor`.
3. The API runs by default in `localhost:8000`.


### Local execution
1. Clone the repository.
2. Create a virtual environment with `python -m venv venv`.
3. Enter into the backend folder `cd backend`
4. Install the requirements with `pip install -r requirements.txt`.
5. Run the server with uvicorn `uvicorn main:app`. Add the flag `--reload` for automatic reloading when testing.
6. The API runs by default in `localhost:8000`.


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
│   │   ├── db_methods.py
│   │   ├── fake_db.py
│   │   ├── users_db_fake.json
│   ├── schemas/
│   │   ├── token_schema.py
│   │   ├── user_schema.py
│   ├── user/
│   │   ├── superuser_endpoints.py
│   │   ├── user_methods.py
├── main.py
├── requirements.txt
├── README.md
```

The API is modular. Basic configuration is in the core folder (settings and a file collecting all the router points). It also contains an example of endpoint in `endpoints.py`. 

Different functionalities are implemented in their corresponding folder. Each one through a router object. The `main.py` file calls the application and connects the routers. Detail documentation of endpoints, as well as a login page, using the OpenAPI standard, can be found in `/docs`.


## Folder description

`auth`: Contains functions for user authentication using an Ouath2 scheme. It implements password hashing and identification throug a JWT token. It also allows for defining scopes.

`core`: Contains core functions for the API. In particular, it routes together all routers in the different code pieces. It also provides a configuration file with the API settings, and an example of a get endpoint.

`data`: Contains external data for the API. In this barebones version, it only contains a fake database file implemented through a dictionary.

`schemas`: Contains pydantic schemas for the different variables used.

`user`: Contains methods related to user creation and deletion, as well as user related endpoints.


## Authenticating

Users must authenticate in order to get a token that allows them to perform calls to the endpoints. This is achieved through a Ouath2 scheme in `/token`. Afterwards, every call must provide the bearer token in the authorization header.

The fake database provides two users: `heman` with superuser acces, and `manatarms` being a normal user. Both have the password `password`.

Endpoints must check authenticity of the token through a dependence. See example:

```python
from typing import Annotated
from fastapi import Depends
from auth.auth import check_token

@router.get("/")
def get_endpoint(token: Annotated[str, Depends(check_token)]):
    ...
```

If scopes are present (for example, a `'superuser'` scope by default), one must use instead

```python
from typing import Annotated
from fastapi import Security
from auth.auth import check_token

@router.get("/")
def get_endpoint(token: Annotated[str, Security(check_token, scopes = ['superuser'])]):
    ...
```

Scopes can also be added to the full router instead than to any individual endpoint, by

```python
APIRouter(dependencies=[Security(check_token, scopes=["superuser"])])
```

Superusers must have the flag `is_superuser = True` in the database. Functions restricted to superusers are achieved by replacing the the dependence by `check_superuser` and adding the scope for extra security (e.g. superusers need to be logged as superusers.)