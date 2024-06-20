import pytest

from fastapi import status


@pytest.mark.anyio
async def test_api_status(api_client):
    response = await api_client.get("/api/status")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "OK"}


@pytest.mark.anyio
@pytest.mark.parametrize("http_method", ["post", "patch", "put"])
async def test_invalid_methods_on_status_endpoint(api_client, http_method):
    response = await getattr(api_client, http_method)(
        "/api/status", json={"status": "Not OK"}
    )
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": "Method Not Allowed"}


@pytest.mark.anyio
async def test_delete_method_on_status_endpoint(api_client):
    response = await api_client.delete("/api/status")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.json() == {"detail": "Method Not Allowed"}
