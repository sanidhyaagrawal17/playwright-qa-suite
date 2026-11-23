import pytest


@pytest.mark.api
def test_get_posts_returns_200_and_valid_schema(api_context):
    resp = api_context.get("/posts/1")
    assert resp.status == 200
    body = resp.json()
    assert body["id"] == 1
    assert isinstance(body["userId"], int)
    assert isinstance(body["title"], str) and len(body["title"]) > 0
    assert isinstance(body["body"], str) and len(body["body"]) > 0


@pytest.mark.api
def test_create_post_returns_201_with_echoed_payload(api_context):
    payload = {
        "title": "Playwright API Contract Test",
        "body": "Verifying POST creation contract",
        "userId": 10,
    }
    resp = api_context.post("/posts", data=payload)
    assert resp.status == 201
    body = resp.json()
    assert body["title"] == payload["title"]
    assert body["userId"] == payload["userId"]
    assert "id" in body


@pytest.mark.api
def test_update_and_delete_post_contracts(api_context):
    put_resp = api_context.put(
        "/posts/1",
        data={"id": 1, "title": "Updated Title", "body": "Updated Body", "userId": 1},
    )
    assert put_resp.status == 200
    assert put_resp.json()["title"] == "Updated Title"

    del_resp = api_context.delete("/posts/1")
    assert del_resp.status == 200


@pytest.mark.api
def test_nonexistent_resource_returns_404(api_context):
    resp = api_context.get("/posts/999999")
    assert resp.status == 404
