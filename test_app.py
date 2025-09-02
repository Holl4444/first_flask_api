import pytest
from uuid import UUID
from datetime import datetime, timezone

from app import server

@pytest.fixture
def client():
    return server.test_client() # # Built in flask method. Auto cleaned up

@pytest.fixture
def mock_tasks():
        return [{
        'id': UUID('9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'), 'task': 'Mocked Task', 'completed': False, 'created': datetime(2025, 9, 2, 15, 21, 59, 331225, tzinfo=timezone.utc) # Datetime obj expected
    }]

def test_get_tasks(client):
    response = client.get('todo/tasks')
    assert response.status_code == 200


def test_get_tasks(client, monkeypatch, mock_tasks):
    monkeypatch.setattr('app.tasks', mock_tasks) # Temporarily replace tasks (list in app) with the mock (auto runs fixture function)
    response = client.get('/todo/tasks') # Mock get request

    assert response.status_code == 200
    assert b'Mocked Task' in response.data # b = bytes. To check as string = in response.data.decode()

def test_post_task(client):
    mock_body = {
        'task': 'Mock Post', 
    }
    response = client.post('/todo/tasks', json=mock_body)
    assert response.status_code == 201

    data = response.get_json()
    assert data['task'] == 'Mock Post'
    assert 'id' in data
    assert 'created' in data
    assert data['completed'] == False
    
    UUID(data['id']) # Check valid id format - throws ValueError if not and fails test

def test_get_task(client, monkeypatch, mock_tasks):
    monkeypatch.setattr('app.tasks', mock_tasks)
    response = client.get('/todo/tasks/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d')

    assert response.status_code == 200
    assert b'Mocked Task' in response.data

def test_put_task(client, monkeypatch, mock_tasks):
     mock_body = {
          'task': 'Mock Put Task', 'completed': True
     }
     monkeypatch.setattr('app.tasks', mock_tasks)
     response = client.put('/todo/tasks/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d', json=mock_body)

     assert response.status_code == 200

     data = response.get_json()
     assert data['task'] == 'Mock Put Task'
     assert data['completed'] == True
     assert data['id'] == '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'
     assert data['created'] == '2025-09-02T15:21:59.331225+00:00'

def test_delete_task(client, monkeypatch, mock_tasks):
     monkeypatch.setattr('app.tasks', mock_tasks)
     response = client.delete('/todo/tasks/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d')

     assert response.status_code == 204
     assert len(mock_tasks) == 0
