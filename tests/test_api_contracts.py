import pytest

POST_REQUIRED_KEYS = {"userId", "id", "title", "body"}
COMMENT_REQUIRED_KEYS = {"postId", "id", "name", "email", "body"}


@pytest.mark.api
def test_get_single_post_enforces_headers_and_strict_schema(api_context):
    resp = api_context.get("/posts/1")
    assert resp.status == 200
    assert "application/json" in resp.headers.get("content-type", "")

    body = resp.json()
    assert set(body.keys()) == POST_REQUIRED_KEYS
    assert body["id"] == 1
    assert isinstance(body["userId"], int) and body["userId"] > 0
    assert isinstance(body["title"], str) and len(body["title"].strip()) > 0
    assert isinstance(body["body"], str) and len(body["body"].strip()) > 0


@pytest.mark.api
def test_query_filter_returns_strict_subset_matching_user_id(api_context):
    all_resp = api_context.get("/posts")
    filtered_resp = api_context.get("/posts", params={"userId": 1})
    assert all_resp.status == 200
    assert filtered_resp.status == 200

    all_posts = all_resp.json()
    filtered_posts = filtered_resp.json()

    assert len(all_posts) > len(filtered_posts) > 0
    assert all(set(p.keys()) == POST_REQUIRED_KEYS for p in filtered_posts)
    assert all(p["userId"] == 1 for p in filtered_posts), "Filter leaked posts from another userId"
    ids = [p["id"] for p in filtered_posts]
    assert len(ids) == len(set(ids)), "Duplicate post IDs returned"


@pytest.mark.api
def test_nested_comments_match_parent_post_and_valid_emails(api_context):
    resp = api_context.get("/posts/1/comments")
    assert resp.status == 200
    comments = resp.json()
    assert len(comments) > 0

    for comment in comments:
        assert set(comment.keys()) == COMMENT_REQUIRED_KEYS
        assert comment["postId"] == 1
        assert "@" in comment["email"] and "." in comment["email"].split("@")[-1]
        assert len(comment["body"].strip()) > 0


@pytest.mark.api
def test_write_endpoints_honor_http_contracts_and_echo_payload(api_context):
    """Note: JSONPlaceholder is a stateless public API; writes are not persisted server-side.
    This test verifies status codes, content-type headers, and response payload contracts."""
    payload = {
        "title": "Playwright API Contract Test",
        "body": "Verifying POST creation contract",
        "userId": 10,
    }
    create_resp = api_context.post("/posts", data=payload)
    assert create_resp.status == 201
    assert "application/json" in create_resp.headers.get("content-type", "")
    created = create_resp.json()
    assert created["title"] == payload["title"]
    assert created["body"] == payload["body"]
    assert created["userId"] == payload["userId"]
    assert isinstance(created["id"], int) and created["id"] > 0

    patch_resp = api_context.patch("/posts/1", data={"title": "Patched Title Only"})
    assert patch_resp.status == 200
    patched = patch_resp.json()
    assert patched["id"] == 1
    assert patched["title"] == "Patched Title Only"
    assert len(patched["body"].strip()) > 0  # Unmodified fields preserved

    del_resp = api_context.delete("/posts/1")
    assert del_resp.status == 200
    assert del_resp.json() == {}


@pytest.mark.api
@pytest.mark.parametrize("path", ["/posts/999999", "/nonexistent-resource"])
def test_invalid_resources_return_404_with_empty_body(api_context, path):
    resp = api_context.get(path)
    assert resp.status == 404
    assert resp.json() == {}
