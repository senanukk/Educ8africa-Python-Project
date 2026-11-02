# VoltSafe: Substation Safety Academy

A Flask web app that trains everyone who enters a **power substation**. Each person gets the course that fits their role, and the app remembers every substation area they visit.

| Who | Course | Valid for |
|---|---|---|
| 🪪 **Visitor** | Visitor Safety Induction (4 lessons) | 30 days |
| 🛠️ **New Engineer** | New Engineer Safety Onboarding (6 lessons) | 365 days |
| ⚡ **Experienced Engineer** | Experienced Engineer Refresher (4 lessons) | 365 days |

When a new engineer's onboarding certificate expires, they move to the experienced-engineer refresher.

## Features

- **Role-based training**: lessons, an assessment (80% pass mark, retakes allowed) and a printable certificate.
- **Interactive substation map** with 11 zones (switchyard, transformer bay, GIS hall, battery room, cable basement and more). Each zone shows its hazards, required PPE and which roles may enter.
- **Visit memory**: people check in and out of zones. Visited zones are highlighted on their map and kept in a full visit history.
- **Access control**: you can't check in without valid training. Restricted zones are locked by role, and visitors must name their escort.
- **Supervisor console**: an emergency roll-call of who is on site now, everyone's training status, visit totals per area and the full visit log.
- **Modern UI**: glass cards and gradients, with four switchable themes (Midnight Volt, Aurora, Ember, Daylight). The chosen theme is remembered, and the layout works on phones.

## Run it

```bash
pip install -r requirements.txt
python -m safety_app.app          # open http://127.0.0.1:5000
python -m pytest                  # run the tests
```

A supervisor account is created on first start: `supervisor@voltsafe.local` / `ChangeMe123!`.
Override it with the `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables, and set `SECRET_KEY` for real use.
The SQLite database is stored in `safety_app/instance/` (override with `VOLTSAFE_DB`).

Course content and the substation layout are in `safety_app/content.py`.

## Website version (no server needed)

`website/` holds a standalone version of VoltSafe written in plain HTML, CSS and JavaScript. It has the same courses, quizzes, certificates, interactive substation map, check-in/out with role rules, and a gate log for emergency roll-calls. It runs entirely in the browser and keeps its data in that browser's local storage, which suits a shared tablet at the substation gate.

- Open `website/index.html` in a browser, or host the `website/` folder on any static host such as GitHub Pages.
- After editing `safety_app/content.py`, run `python website/build.py` to regenerate `website/content.js` and `website/index.html`. Edit `website/page.html` for layout changes.
