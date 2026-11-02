from datetime import timedelta

import pytest

from safety_app.app import create_app, iso, now
from safety_app.content import TRACKS


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db"), "SECRET_KEY": "test"})


@pytest.fixture
def client(app):
    return app.test_client()


def csrf(client):
    client.get("/")
    with client.session_transaction() as s:
        return s["csrf"]


def register(client, role, email="a@b.com"):
    return client.post("/register", data={
        "csrf_token": csrf(client), "name": "Ama Mensah", "email": email,
        "password": "password123", "role": role, "company": "GridCo",
    }, follow_redirects=True)


def complete_track(client, track, correct=True):
    t = TRACKS[track]
    tok = csrf(client)
    for m in t["modules"]:
        client.post(f"/learn/{m['slug']}", data={"csrf_token": tok})
    answers = {f"q{i}": str(q["answer"] if correct else (q["answer"] + 1) % len(q["options"]))
               for i, q in enumerate(t["quiz"])}
    return client.post("/quiz", data={"csrf_token": tok, **answers})


@pytest.mark.parametrize("role,title", [
    ("visitor", "Visitor Safety Induction"),
    ("new", "New Engineer Safety Onboarding"),
    ("experienced", "Experienced Engineer Refresher"),
])
def test_role_gets_matching_course(client, role, title):
    r = register(client, role)
    assert title.encode() in r.data


def test_pages_render(client):
    assert client.get("/").status_code == 200
    register(client, "new")
    for path in ["/dashboard", "/substation", "/learn/hazards"]:
        assert client.get(path).status_code == 200


def test_post_without_csrf_rejected(client):
    assert client.post("/login", data={"email": "x", "password": "y"}).status_code == 400


def test_quiz_locked_until_modules_done(client):
    register(client, "visitor")
    r = client.get("/quiz")
    assert r.status_code == 302


def test_checkin_requires_training(client):
    register(client, "new")
    r = client.post("/substation/checkin", data={"csrf_token": csrf(client), "area": "CTRL"},
                    follow_redirects=True)
    assert b"Access denied" in r.data


def test_failed_quiz_does_not_grant_access(client):
    register(client, "new")
    r = complete_track(client, "new", correct=False)
    assert b"Not quite yet" in r.data
    r = client.post("/substation/checkin", data={"csrf_token": csrf(client), "area": "CTRL"},
                    follow_redirects=True)
    assert b"Access denied" in r.data


def test_visits_are_remembered(client):
    register(client, "new")
    assert b"You passed" in complete_track(client, "new").data
    tok = csrf(client)
    client.post("/substation/checkin", data={"csrf_token": tok, "area": "CTRL"})
    client.post("/substation/checkin", data={"csrf_token": tok, "area": "GIS"})
    client.post("/substation/checkout", data={"csrf_token": tok})
    page = client.get("/substation").data.decode()
    assert "2 of 11 zones visited" in page
    assert "Indoor GIS / Switchgear Hall" in page
    assert client.get("/certificate").status_code == 200


def test_role_area_restrictions(client):
    register(client, "new")
    complete_track(client, "new")
    r = client.post("/substation/checkin", data={"csrf_token": csrf(client), "area": "CAP"},
                    follow_redirects=True)
    assert b"not authorised" in r.data


def test_visitor_needs_escort(client):
    register(client, "visitor")
    complete_track(client, "visitor")
    tok = csrf(client)
    r = client.post("/substation/checkin", data={"csrf_token": tok, "area": "HVYARD"},
                    follow_redirects=True)
    assert b"escort" in r.data.lower() and b"Checked in" not in r.data
    r = client.post("/substation/checkin", data={"csrf_token": tok, "area": "HVYARD", "escort": "Kofi"},
                    follow_redirects=True)
    assert b"Checked in to HV Switchyard" in r.data


def test_expired_new_engineer_moves_to_refresher(app, client):
    register(client, "new")
    complete_track(client, "new")
    with app.app_context():
        from flask import g  # noqa: F401
        import sqlite3
        db = sqlite3.connect(app.config["DATABASE"])
        db.execute("UPDATE quiz_attempts SET taken_at = ?", (iso(now() - timedelta(days=400)),))
        db.commit()
        db.close()
    page = client.get("/dashboard").data
    assert b"Experienced Engineer Refresher" in page
    assert b"Training required" in page


def test_supervisor_console(app, client):
    assert client.get("/supervisor").status_code == 302
    client.post("/login", data={"csrf_token": csrf(client), "email": app.config["ADMIN_EMAIL"],
                                "password": app.config["ADMIN_PASSWORD"]})
    r = client.get("/supervisor")
    assert r.status_code == 200 and b"roll-call" in r.data


def test_non_admin_forbidden(client):
    register(client, "experienced")
    assert client.get("/supervisor").status_code == 403
