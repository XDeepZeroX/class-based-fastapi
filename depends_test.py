from http.client import HTTPException

import uvicorn as uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from pydantic import BaseModel

#
# def main():
# Simple intuitive injection
from class_based_fastapi import Routable, get

security = HTTPBasic()


def verify_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = credentials.username == "john"
    correct_password = credentials.password == "silver"
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect auth",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class Foo(BaseModel):
    bar: str = "wow"


async def amazing_fn():
    return Foo(bar="amazing_variable")


class ExampleController(Routable):

    # add class wide dependencies e.g. auth
    dependencies = [Depends(verify_auth)]

    # you can define in the Controller init some FastApi Dependency and them are automatically loaded in controller methods
    def __init__(self, x: Foo = Depends(amazing_fn)):
        super().__init__()
        self.x = x
        self.inject = 123

    @get(
        "/some_api", summary="A sample description", response_model=Foo
    )
    def sample_api(self):
        # print(self.x.bar)  # -> amazing_variable
        # return self.x
        return self.inject


app = FastAPI()

controller = ExampleController()
# router memeber inherited from cr.Routable and configured per the annotations.
app.include_router(controller.router)
# print()
uvicorn.run(app, host="localhost", port=9090)
