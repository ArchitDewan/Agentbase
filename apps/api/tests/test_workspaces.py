from httpx import AsyncClient


async def test_create_workspace(client: AsyncClient) -> None:
    response = await client.post("/workspaces", json={"name": "Personal"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Personal"
    assert body["id"]
    assert body["created_at"]


async def test_list_workspaces_starts_empty(client: AsyncClient) -> None:
    response = await client.get("/workspaces")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_workspaces_returns_created_records(client: AsyncClient) -> None:
    await client.post("/workspaces", json={"name": "Personal"})
    await client.post("/workspaces", json={"name": "Demo"})

    response = await client.get("/workspaces")

    assert response.status_code == 200
    names = {workspace["name"] for workspace in response.json()}
    assert names == {"Personal", "Demo"}


async def test_create_workspace_rejects_empty_name(client: AsyncClient) -> None:
    response = await client.post("/workspaces", json={"name": ""})

    assert response.status_code == 422


async def test_create_workspace_rejects_too_long_name(client: AsyncClient) -> None:
    response = await client.post("/workspaces", json={"name": "x" * 121})

    assert response.status_code == 422
