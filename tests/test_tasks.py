"""Task CRUD endpoint tests."""


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    payload = {
        "title": "Write homework",
        "description": "Implement task manager API",
        "status": "todo",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["description"] == payload["description"]
    assert body["status"] == "todo"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_validation_error(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400


def test_get_task(client):
    created = client.post("/tasks", json={"title": "Read docs"}).json()
    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_task_not_found(client):
    response = client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Draft"}).json()
    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "Final", "status": "done"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Final"
    assert body["status"] == "done"


def test_update_task_not_found(client):
    response = client.put(
        "/tasks/00000000-0000-0000-0000-000000000000",
        json={"title": "Missing"},
    )
    assert response.status_code == 404


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temp"}).json()
    response = client.delete(f"/tasks/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    response = client.delete("/tasks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_list_tasks_after_create(client):
    client.post("/tasks", json={"title": "One"})
    client.post("/tasks", json={"title": "Two", "status": "in_progress"})
    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2
