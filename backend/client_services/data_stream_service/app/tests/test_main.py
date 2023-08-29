from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)

def clear_database():
    ...

def make_basic_ccount():
    ...

def get_auth_token():
    ...


def test_get_accounts():

    response = client.get("/accounts/accounts")
    assert response.status_code == 200


# get_account

# post_account

# put_account

# delete_account
