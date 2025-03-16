# vcity-circular-api

Circular index API for the vCity project.

## Instructions

### Docker

To run the API in a docker container, exposed in port `8000`, do the following:

1. Build the docker container by running `docker build -t vcity-cci-api-image .`.
2. Run the docker container by `docker run -d --name vcity-cci-api -p 8000:8000 vcity-cci-api-image`.
3. The API runs in `localhost:8000`.


### Local execution

0. Install [uv](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv) if necessary
1. Clone the repository.
2. Create a virtual environment with `uv sync`
3. Activate the  virtual environment. For MacOS/Lunix

```console
source .venv/bin/activate
```

For Windows:

```console
.venv\Scripts\activate
```

4. Install the package in editable mode with `uv pip install -e .`
5. Generate an authentication token with `python post_install.py`
6. Run the API with `apisk -P 8000`.

## Authentication

Go to <http://0.0.0.0:8000/docs>, click on Authorize, set up username and password. See [Authenticating](#authenticating).


## Overview


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
