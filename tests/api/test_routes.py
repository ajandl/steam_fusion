from app.users_model import User


def test_homepage(client):
    response = client.get("/")
    assert(response.status_code == 200)


def create_user_data():
    return {
        'username': 'mock_user',
        'email': 'mock@mock.com',
        'password': 'mock',
    }


def test_login_response_code(client, app_mixer):
    mock_data = {
        'username': 'mock_user',
        'password': 'mock',
    }
    user = app_mixer.blend(
        User,
        username=mock_data['username'],
    )

    user.set_password(mock_data['password'])

    response = client.post('/login', json=mock_data)

    assert(response.status_code == 200)


def test_login_response_has_token(client, app_mixer):
    assert(True)
