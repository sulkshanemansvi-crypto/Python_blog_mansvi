from app.models import Comment, Post, User
from tests.conftest import register


def make_post(client, title="Hello World", body="<p>First story</p>", **kw):
    data = {"title": title, "body": body, "category": "Life", "tags": "a, b", **kw}
    return client.post("/post/new", data=data, follow_redirects=True)


def test_register_login_logout(client):
    r = register(client)
    assert b"Welcome to Mansvi" in r.data
    client.get("/auth/logout")
    r = client.post("/auth/login", data={"username": "asha", "password": "secret123"}, follow_redirects=True)
    assert r.status_code == 200 and b"Write" in r.data
    r = client.get("/auth/logout", follow_redirects=True)
    assert b"logged out" in r.data


def test_bad_login_and_duplicate(client):
    register(client)
    client.get("/auth/logout")
    r = client.post("/auth/login", data={"username": "asha", "password": "nope"})
    assert b"Invalid" in r.data
    r = register(client)
    assert b"taken" in r.data


def test_post_crud_and_sanitize(client, app):
    register(client)
    r = make_post(client, body="<p>Hi</p><script>alert(1)</script>")
    assert b"Hello World" in r.data and b"<script>alert" not in r.data
    post = Post.query.first()
    assert post.category.name == "Life" and len(post.tags) == 2
    client.post(f"/post/{post.id}/edit", data={"title": "Edited", "body": "<p>x</p>", "category": "", "tags": ""})
    assert Post.query.first().title == "Edited"
    client.post(f"/post/{post.id}/delete")
    assert Post.query.count() == 0


def test_empty_body_rejected(client):
    register(client)
    make_post(client, body="<p><br></p>")
    assert Post.query.count() == 0


def test_only_author_can_edit(client):
    register(client)
    make_post(client)
    client.get("/auth/logout")
    register(client, "bob", "bob@example.com")
    pid = Post.query.first().id
    assert client.get(f"/post/{pid}/edit").status_code == 403
    assert client.post(f"/post/{pid}/delete").status_code == 403


def test_comments_require_login(client):
    register(client)
    make_post(client)
    pid = Post.query.first().id
    client.post(f"/post/{pid}/comment", data={"body": "Nice!"})
    assert Comment.query.count() == 1
    client.get("/auth/logout")
    r = client.post(f"/post/{pid}/comment", data={"body": "anon"})
    assert r.status_code == 302 and "login" in r.location
    assert Comment.query.count() == 1


def test_search_filter_pagination(client):
    register(client)
    for i in range(5):
        make_post(client, title=f"Story {i}", body=f"<p>content {i}</p>", tags="t" if i else "special")
    r = client.get("/")
    assert b"Page 1 of 2" in r.data
    assert b"Story 0" in client.get("/?q=content 0").data
    assert b"Story 3" not in client.get("/?q=content 0").data
    from app.models import Tag
    tid = Tag.query.filter_by(name="special").first().id
    r = client.get(f"/?tag={tid}")
    assert b"Story 0" in r.data and b"Story 1" not in r.data


def test_profile_page(client):
    register(client)
    make_post(client)
    r = client.get("/user/asha")
    assert b"Hello World" in r.data
    assert client.get("/user/ghost").status_code == 404
