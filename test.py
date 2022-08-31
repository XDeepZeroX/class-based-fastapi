from fastapi import FastAPI
from starlette.testclient import TestClient

#
# def main():
# Simple intuitive injection
from tests.test_crud_view import ExampleRoutableParent, ExampleRoutableChildren

child_routes = ExampleRoutableChildren(1)
parent_routes = ExampleRoutableParent(2)

app = FastAPI()
# router memeber inherited from cr.Routable and configured per the annotations.
app.include_router(child_routes.router)
app.include_router(parent_routes.router)
# print()

name_module = 'test-view/'
client = TestClient(app)

# Children

response = client.get(f'{name_module}/example-routable-children/v1.0/100')
print(f'[GET]    {response.status_code}:  {response.text}')

response = client.delete(f'{name_module}/example-routable-children/v1.0/100')
print(f'[DELETE] {response.status_code}:  {response.text}')

response = client.post(f'{name_module}/example-routable-children/v1.0')
print(f'[POST]   {response.status_code}:  {response.text}')

response = client.put(f'{name_module}/example-routable-children/v1.0')
print(f'[PUT]    {response.status_code}:  {response.text}')

response = client.patch(f'{name_module}/example-routable-children/v1.0/100')
print(f'[PATCH]  {response.status_code}:  {response.text}')

## Parent

response = client.get(f'{name_module}/example-routable-parent/v1.0/100')
print(f'[GET]    {response.status_code}:  {response.text}')

response = client.delete(f'{name_module}/example-routable-parent/v1.0/100')
print(f'[DELETE] {response.status_code}:  {response.text}')

response = client.post(f'{name_module}/example-routable-parent/v1.0')
print(f'[POST]   {response.status_code}:  {response.text}')

response = client.put(f'{name_module}/example-routable-parent/v1.0')
print(f'[PUT]    {response.status_code}:  {response.text}')

response = client.patch(f'{name_module}/example-routable-parent/v1.0/100')
print(f'[PATCH]  {response.status_code}:  {response.text}')
