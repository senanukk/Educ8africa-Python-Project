"""VoltSafe - power-substation safety learning app.

Run with:  python -m safety_app.app   (then open http://127.0.0.1:5000)
"""

import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import (
    Flask, abort, flash, g, redirect, render_template, request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .content import AREAS, AREAS_BY_CODE, PASS_MARK, ROLES, TRACKS

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    company TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS module_progress (
    user_id INTEGER NOT NULL REFERENCES users(id),
    track TEXT NOT NULL,
    module_slug TEXT NOT NULL,
    completed_at TEXT NOT NULL,
    PRIMARY KEY (user_id, track, module_slug)
);
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    track TEXT NOT NULL,
    score INTEGER NOT NULL,
    passed INTEGER NOT NULL,
    taken_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    area_code TEXT NOT NULL,
    escort TEXT,
    check_in TEXT NOT NULL,
    check_out TEXT
);
"""


def now():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.isoformat(timespec="seconds")


def parse(ts):
    return datetime.fromisoformat(ts) if ts else None


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        DATABASE=os.environ.get(
            "VOLTSAFE_DB", os.path.join(app.instance_path, "voltsafe.sqlite3")
        ),
        ADMIN_EMAIL=os.environ.get("ADMIN_EMAIL", "supervisor@voltsafe.local"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", "ChangeMe123!"),
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    # ------------------------------------------------------------------ db
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.executescript(SCHEMA)
        exists = db.execute(
            "SELECT 1 FROM users WHERE email = ?", (app.config["ADMIN_EMAIL"],)
        ).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO users (name, email, password_hash, role, company, is_admin, created_at)"
                " VALUES (?, ?, ?, 'experienced', 'Site Safety Office', 1, ?)",
                (
                    "Site Supervisor",
                    app.config["ADMIN_EMAIL"],
                    generate_password_hash(app.config["ADMIN_PASSWORD"]),
                    iso(now()),
                ),
            )
        db.commit()

    with app.app_context():
        init_db()

    # ------------------------------------------------------------ helpers
    def current_user():
        if "user" not in g:
            uid = session.get("uid")
            g.user = (
                get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
                if uid else None
            )
        return g.user

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if current_user() is None:
                flash("Please sign in to continue.", "info")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)
        return wrapped

    def admin_required(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user()["is_admin"]:
                abort(403)
            return view(*args, **kwargs)
        return wrapped

    def last_pass(user_id, track):
        row = get_db().execute(
            "SELECT * FROM quiz_attempts WHERE user_id = ? AND track = ? AND passed = 1"
            " ORDER BY taken_at DESC LIMIT 1",
            (user_id, track),
        ).fetchone()
        return row

    def active_track(user):
        """Which course this person must take next.

        Visitors take the induction and experienced engineers the refresher.
        A new engineer takes onboarding; once their onboarding certificate has
        expired they graduate to the experienced-engineer refresher.
        """
        if user["role"] == "new":
            onboarding = last_pass(user["id"], "new")
            if onboarding and parse(onboarding["taken_at"]) + timedelta(
                days=TRACKS["new"]["validity_days"]
            ) < now():
                return "experienced"
        return ROLES[user["role"]]["track"]

    def training_status(user):
        track_key = active_track(user)
        track = TRACKS[track_key]
        done = {
            r["module_slug"]
            for r in get_db().execute(
                "SELECT module_slug FROM module_progress WHERE user_id = ? AND track = ?",
                (user["id"], track_key),
            )
        }
        passed = last_pass(user["id"], track_key)
        valid_until = (
            parse(passed["taken_at"]) + timedelta(days=track["validity_days"])
            if passed else None
        )
        if valid_until and valid_until >= now():
            state = "valid"
        elif valid_until:
            state = "expired"
        elif done:
            state = "in_progress"
        else:
            state = "not_started"
        total = len(track["modules"])
        return {
            "track_key": track_key,
            "track": track,
            "done": done,
            "modules_done": len(done & {m["slug"] for m in track["modules"]}),
            "modules_total": total,
            "all_modules_done": all(m["slug"] in done for m in track["modules"]),
            "passed": passed,
            "valid_until": valid_until,
            "days_left": (valid_until - now()).days if valid_until else None,
            "state": state,
        }

    def open_visit(user_id):
        return get_db().execute(
            "SELECT * FROM visits WHERE user_id = ? AND check_out IS NULL"
            " ORDER BY check_in DESC LIMIT 1",
            (user_id,),
        ).fetchone()

    def check_csrf():
        token = request.form.get("csrf_token", "")
        if not token or not secrets.compare_digest(token, session.get("csrf", "")):
            abort(400, "Invalid or missing form token. Please reload the page.")

    @app.before_request
    def csrf_protect():
        session.setdefault("csrf", secrets.token_hex(16))
        if request.method == "POST":
            check_csrf()

    @app.context_processor
    def inject_globals():
        return {
            "current_user": current_user(),
            "csrf_token": session.get("csrf", ""),
            "ROLES": ROLES,
            "year": now().year,
        }

    @app.template_filter("nicedate")
    def nicedate(value):
        if isinstance(value, str):
            value = parse(value)
        return value.strftime("%d %b %Y, %H:%M UTC") if value else "-"

    # -------------------------------------------------------------- pages
    @app.route("/")
    def index():
        return render_template("index.html", tracks=TRACKS, areas=AREAS)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            role = request.form.get("role", "")
            company = request.form.get("company", "").strip()
            error = None
            if not name or not email or "@" not in email:
                error = "Please enter your name and a valid email address."
            elif len(password) < 8:
                error = "Password must be at least 8 characters."
            elif role not in ROLES:
                error = "Please choose who you are: visitor, new or experienced engineer."
            if error is None:
                db = get_db()
                try:
                    cur = db.execute(
                        "INSERT INTO users (name, email, password_hash, role, company, created_at)"
                        " VALUES (?, ?, ?, ?, ?, ?)",
                        (name, email, generate_password_hash(password), role, company, iso(now())),
                    )
                    db.commit()
                except sqlite3.IntegrityError:
                    error = "An account with that email already exists."
                else:
                    session.clear()
                    session["uid"] = cur.lastrowid
                    flash(f"Welcome aboard, {name}! Your {TRACKS[ROLES[role]['track']]['title']} is ready.", "success")
                    return redirect(url_for("dashboard"))
            flash(error, "error")
        return render_template("register.html", selected=request.args.get("role", ""))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
                session.clear()
                session["uid"] = user["id"]
                nxt = request.args.get("next", "")
                if not nxt.startswith("/") or nxt.startswith("//"):
                    nxt = url_for("dashboard")
                return redirect(nxt)
            flash("Incorrect email or password.", "error")
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("You have signed out. Stay safe!", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        status = training_status(user)
        db = get_db()
        visited = db.execute(
            "SELECT area_code, COUNT(*) AS n, MAX(check_in) AS last FROM visits"
            " WHERE user_id = ? GROUP BY area_code",
            (user["id"],),
        ).fetchall()
        recent = db.execute(
            "SELECT * FROM visits WHERE user_id = ? ORDER BY check_in DESC LIMIT 5",
            (user["id"],),
        ).fetchall()
        return render_template(
            "dashboard.html",
            status=status,
            visited={r["area_code"]: r for r in visited},
            recent=recent,
            areas=AREAS,
            areas_by_code=AREAS_BY_CODE,
            here=open_visit(user["id"]),
        )

    @app.route("/learn/<slug>", methods=["GET", "POST"])
    @login_required
    def module(slug):
        user = current_user()
        status = training_status(user)
        modules = status["track"]["modules"]
        idx = next((i for i, m in enumerate(modules) if m["slug"] == slug), None)
        if idx is None:
            abort(404)
        if request.method == "POST":
            db = get_db()
            db.execute(
                "INSERT OR IGNORE INTO module_progress (user_id, track, module_slug, completed_at)"
                " VALUES (?, ?, ?, ?)",
                (user["id"], status["track_key"], slug, iso(now())),
            )
            db.commit()
            if idx + 1 < len(modules):
                return redirect(url_for("module", slug=modules[idx + 1]["slug"]))
            flash("All modules complete - time for the assessment!", "success")
            return redirect(url_for("quiz"))
        return render_template(
            "module.html",
            status=status,
            mod=modules[idx],
            idx=idx,
            prev=modules[idx - 1] if idx > 0 else None,
        )

    @app.route("/quiz", methods=["GET", "POST"])
    @login_required
    def quiz():
        user = current_user()
        status = training_status(user)
        if not status["all_modules_done"]:
            flash("Complete every module before taking the assessment.", "info")
            return redirect(url_for("dashboard"))
        questions = status["track"]["quiz"]
        if request.method == "POST":
            results = []
            for i, q in enumerate(questions):
                raw = request.form.get(f"q{i}")
                chosen = int(raw) if raw is not None and raw.isdigit() else None
                results.append({"q": q, "chosen": chosen, "correct": chosen == q["answer"]})
            score = round(100 * sum(r["correct"] for r in results) / len(questions))
            passed = score >= PASS_MARK
            db = get_db()
            db.execute(
                "INSERT INTO quiz_attempts (user_id, track, score, passed, taken_at)"
                " VALUES (?, ?, ?, ?, ?)",
                (user["id"], status["track_key"], score, int(passed), iso(now())),
            )
            db.commit()
            return render_template(
                "result.html", score=score, passed=passed, results=results,
                status=training_status(user), pass_mark=PASS_MARK,
            )
        return render_template("quiz.html", status=status, questions=questions, pass_mark=PASS_MARK)

    @app.route("/certificate")
    @login_required
    def certificate():
        status = training_status(current_user())
        if status["state"] != "valid":
            flash("You need a valid, passed course to view your certificate.", "info")
            return redirect(url_for("dashboard"))
        return render_template("certificate.html", status=status)

    @app.route("/substation")
    @login_required
    def substation():
        user = current_user()
        db = get_db()
        visited = db.execute(
            "SELECT area_code, COUNT(*) AS n, MAX(check_in) AS last FROM visits"
            " WHERE user_id = ? GROUP BY area_code",
            (user["id"],),
        ).fetchall()
        history = db.execute(
            "SELECT * FROM visits WHERE user_id = ? ORDER BY check_in DESC LIMIT 50",
            (user["id"],),
        ).fetchall()
        return render_template(
            "substation.html",
            areas=AREAS,
            areas_by_code=AREAS_BY_CODE,
            visited={r["area_code"]: r for r in visited},
            history=history,
            here=open_visit(user["id"]),
            status=training_status(user),
        )

    @app.route("/substation/checkin", methods=["POST"])
    @login_required
    def checkin():
        user = current_user()
        area = AREAS_BY_CODE.get(request.form.get("area", ""))
        if area is None:
            abort(404)
        status = training_status(user)
        if status["state"] != "valid":
            flash("Access denied: complete (or renew) your safety training before entering any area.", "error")
            return redirect(url_for("substation"))
        if user["role"] not in area["allowed"]:
            flash(f"Access denied: {ROLES[user['role']]['label']}s are not authorised to enter the {area['name']}.", "error")
            return redirect(url_for("substation"))
        escort = request.form.get("escort", "").strip()
        if user["role"] == "visitor" and not escort:
            flash("Visitors must name the authorised engineer escorting them.", "error")
            return redirect(url_for("substation"))
        db = get_db()
        ts = iso(now())
        db.execute(
            "UPDATE visits SET check_out = ? WHERE user_id = ? AND check_out IS NULL",
            (ts, user["id"]),
        )
        db.execute(
            "INSERT INTO visits (user_id, area_code, escort, check_in) VALUES (?, ?, ?, ?)",
            (user["id"], area["code"], escort or None, ts),
        )
        db.commit()
        flash(f"Checked in to {area['name']}. Required PPE: {', '.join(area['ppe'])}.", "success")
        return redirect(url_for("substation"))

    @app.route("/substation/checkout", methods=["POST"])
    @login_required
    def checkout():
        db = get_db()
        db.execute(
            "UPDATE visits SET check_out = ? WHERE user_id = ? AND check_out IS NULL",
            (iso(now()), current_user()["id"]),
        )
        db.commit()
        flash("Checked out. Your visit has been recorded.", "info")
        return redirect(url_for("substation"))

    @app.route("/supervisor")
    @admin_required
    def supervisor():
        db = get_db()
        on_site = db.execute(
            "SELECT v.*, u.name, u.role, u.company FROM visits v JOIN users u ON u.id = v.user_id"
            " WHERE v.check_out IS NULL ORDER BY v.check_in DESC"
        ).fetchall()
        log = db.execute(
            "SELECT v.*, u.name, u.role FROM visits v JOIN users u ON u.id = v.user_id"
            " ORDER BY v.check_in DESC LIMIT 200"
        ).fetchall()
        people = [
            {"user": u, "status": training_status(u)}
            for u in db.execute("SELECT * FROM users ORDER BY created_at DESC")
        ]
        area_counts = {
            r["area_code"]: r["n"]
            for r in db.execute(
                "SELECT area_code, COUNT(*) AS n FROM visits GROUP BY area_code"
            )
        }
        return render_template(
            "supervisor.html", on_site=on_site, log=log, people=people,
            areas=AREAS, areas_by_code=AREAS_BY_CODE, area_counts=area_counts,
        )

    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(400)
    def error_page(err):
        return render_template("error.html", err=err), err.code

    return app


if __name__ == "__main__":
    create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1")
