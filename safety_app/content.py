"""Training content and power-substation layout for VoltSafe.

Three learning tracks exist, one per kind of person who enters the substation:

* ``visitor``     - Visitor Safety Induction (short, escorted-access focus)
* ``new``         - New Engineer Onboarding (full foundation course)
* ``experienced`` - Experienced Engineer Refresher (periodic fresher course)
"""

PASS_MARK = 80  # percent needed to pass a track quiz

ROLES = {
    "visitor": {
        "label": "Visitor",
        "track": "visitor",
        "blurb": "Contractors, auditors, students and guests entering the site.",
        "icon": "🪪",
    },
    "new": {
        "label": "New Engineer",
        "track": "new",
        "blurb": "Engineers and technicians in their first year on site.",
        "icon": "🛠️",
    },
    "experienced": {
        "label": "Experienced Engineer",
        "track": "experienced",
        "blurb": "Authorised engineers who need a periodic refresher course.",
        "icon": "⚡",
    },
}

TRACKS = {
    "visitor": {
        "title": "Visitor Safety Induction",
        "subtitle": "Everything you must know before you are escorted on site.",
        "validity_days": 30,
        "accent": "cyan",
        "modules": [
            {
                "slug": "welcome",
                "title": "Welcome to a Live Substation",
                "minutes": 4,
                "summary": "Why a substation is one of the most hazardous places you will ever visit.",
                "points": [
                    "Every conductor, busbar and piece of equipment must be treated as LIVE unless an authorised person has proved it dead and earthed it.",
                    "High-voltage electricity can arc (jump) through air - you do not need to touch anything to be injured.",
                    "You must be escorted by an authorised engineer at all times. Never wander off alone.",
                    "Sign in at the gate and sign out when you leave so everyone can be accounted for in an emergency.",
                ],
            },
            {
                "slug": "ppe",
                "title": "Personal Protective Equipment",
                "minutes": 3,
                "summary": "The minimum PPE you must wear beyond the gate.",
                "points": [
                    "Safety helmet, safety boots, high-visibility vest and safety glasses are mandatory in all outdoor yards.",
                    "No loose clothing, jewellery, metal watch straps or synthetic fabrics that can melt in an arc flash.",
                    "Hearing protection is required near operating transformers and generators.",
                    "Your escort will tell you if additional PPE is needed for a specific area.",
                ],
            },
            {
                "slug": "boundaries",
                "title": "Boundaries, Signs & Barriers",
                "minutes": 3,
                "summary": "Reading the site: what the colours, signs and barriers mean.",
                "points": [
                    "Red danger signs and barriers mark live equipment - never cross, lean on or reach over them.",
                    "Keep at least the posted safe-approach distance from all HV equipment.",
                    "Never carry long objects (ladders, poles, tape measures) upright in the switchyard.",
                    "Do not touch fences, gates, structures or cabinets unless your escort tells you it is safe.",
                ],
            },
            {
                "slug": "emergency",
                "title": "Emergency Procedures",
                "minutes": 3,
                "summary": "What to do if the alarm sounds or someone is hurt.",
                "points": [
                    "Learn where the assembly (muster) point is before you enter the site.",
                    "If the alarm sounds, stop, follow your escort calmly to the muster point and wait to be counted.",
                    "Never touch a person who is in contact with electrical equipment - raise the alarm and shout for an authorised person.",
                    "Report every incident, near miss or unsafe condition to your escort immediately.",
                ],
            },
        ],
        "quiz": [
            {
                "q": "How should you treat equipment in the substation?",
                "options": ["Live only if it is humming", "Live unless proved dead and earthed by an authorised person", "Dead if the lights are off", "Dead if it has a sign"],
                "answer": 1,
            },
            {
                "q": "As a visitor, when may you walk around the site alone?",
                "options": ["After the induction", "Inside the control room", "Never - you must always be escorted", "When the escort is on a call"],
                "answer": 2,
            },
            {
                "q": "Which item should NOT be worn in the switchyard?",
                "options": ["Safety helmet", "High-visibility vest", "Metal jewellery", "Safety boots"],
                "answer": 2,
            },
            {
                "q": "Someone is in contact with live equipment. What do you do?",
                "options": ["Pull them away by hand", "Raise the alarm and call an authorised person", "Throw water on them", "Walk away"],
                "answer": 1,
            },
            {
                "q": "When the emergency alarm sounds you should...",
                "options": ["Finish what you are doing", "Go back to your car", "Follow your escort to the muster point", "Hide in the control room"],
                "answer": 2,
            },
        ],
    },
    "new": {
        "title": "New Engineer Safety Onboarding",
        "subtitle": "The foundation every engineer needs before working in a substation.",
        "validity_days": 365,
        "accent": "violet",
        "modules": [
            {
                "slug": "hazards",
                "title": "Electrical Hazards in Substations",
                "minutes": 6,
                "summary": "Shock, arc flash, step & touch potential and induced voltages.",
                "points": [
                    "Electric shock: current through the body can stop the heart at levels as low as tens of milliamps.",
                    "Arc flash: an arc can reach temperatures hotter than the surface of the sun, causing burns, blast and blindness.",
                    "Step and touch potential: during an earth fault the ground itself can carry dangerous voltage gradients.",
                    "Induced and back-fed voltages can appear on 'dead' circuits from parallel lines, generators or VTs.",
                ],
            },
            {
                "slug": "loto",
                "title": "Isolation, Lock-Out / Tag-Out",
                "minutes": 7,
                "summary": "Making equipment safe before anyone touches it.",
                "points": [
                    "Follow the five golden rules: disconnect, secure against reconnection, verify absence of voltage, earth and short-circuit, protect against adjacent live parts.",
                    "Every isolation point gets your personal lock and a danger tag with your name, date and reason.",
                    "Only the person who applied a lock may remove it.",
                    "Always test your voltage detector on a known live source before and after proving dead (live-dead-live).",
                ],
            },
            {
                "slug": "permits",
                "title": "Permit-to-Work System",
                "minutes": 5,
                "summary": "Who may authorise work and how a permit protects you.",
                "points": [
                    "No work on HV equipment begins without a valid permit-to-work issued by an authorised person.",
                    "Read the permit fully: it states exactly what is isolated, where earths are applied and the limits of the work.",
                    "Never extend your work beyond the boundaries written on the permit.",
                    "Return and cancel the permit when work is complete so equipment can be safely restored.",
                ],
            },
            {
                "slug": "ppe",
                "title": "PPE & Arc-Rated Clothing",
                "minutes": 5,
                "summary": "Choosing and inspecting the right protection for the task.",
                "points": [
                    "Arc-rated clothing must meet or exceed the incident energy calculated for the task.",
                    "Inspect insulating gloves before each use with an air (roll) test; check test dates on all insulating equipment.",
                    "Face shields and arc hoods are required for switching and racking operations.",
                    "Damaged or out-of-date PPE must be tagged and removed from service.",
                ],
            },
            {
                "slug": "approach",
                "title": "Safe Approach Distances",
                "minutes": 4,
                "summary": "How close is too close at each voltage level.",
                "points": [
                    "Minimum approach distances increase with voltage - know the value for each bay you work in.",
                    "Include the reach of tools, ladders and materials when judging your distance.",
                    "Use barriers, flags and a dedicated safety observer when working near live parts.",
                    "Mobile plant (cranes, MEWPs) needs a specific lifting plan and banksman in the switchyard.",
                ],
            },
            {
                "slug": "emergency",
                "title": "Fire, Rescue & First Response",
                "minutes": 5,
                "summary": "Responding to transformer fires, SF6 releases and electrical injuries.",
                "points": [
                    "Use CO2 or dry-powder extinguishers on electrical fires - never water on live equipment.",
                    "An SF6 leak in an indoor room can displace oxygen; ventilate and leave the area immediately.",
                    "Isolate the supply before attempting rescue, or use an insulated rescue hook.",
                    "Know the location of first-aid kits, AEDs, eye-wash stations and emergency phones in every area.",
                ],
            },
        ],
        "quiz": [
            {
                "q": "Which is the correct order when proving equipment dead?",
                "options": ["Dead-live-dead", "Live-dead-live", "Just test once", "Touch it with the back of the hand"],
                "answer": 1,
            },
            {
                "q": "Who may remove a personal lock from an isolation point?",
                "options": ["Any engineer", "The supervisor", "Only the person who applied it", "The control room"],
                "answer": 2,
            },
            {
                "q": "What must be in place before work begins on HV equipment?",
                "options": ["A verbal OK", "A valid permit-to-work", "An email from a colleague", "Nothing if it looks off"],
                "answer": 1,
            },
            {
                "q": "Which extinguisher is suitable for a fire on live electrical equipment?",
                "options": ["Water", "Foam", "CO2", "Wet chemical"],
                "answer": 2,
            },
            {
                "q": "What is 'step potential'?",
                "options": ["Voltage between your feet caused by current flowing in the ground", "The height of a step ladder", "A type of relay", "The voltage on the control panel"],
                "answer": 0,
            },
            {
                "q": "An SF6 alarm sounds in the indoor GIS room. You should...",
                "options": ["Continue working", "Ventilate and leave the room immediately", "Open the equipment to look", "Turn off the lights"],
                "answer": 1,
            },
        ],
    },
    "experienced": {
        "title": "Experienced Engineer Refresher",
        "subtitle": "A focused fresher course on lessons learned and changed procedures.",
        "validity_days": 365,
        "accent": "amber",
        "modules": [
            {
                "slug": "complacency",
                "title": "Complacency Kills",
                "minutes": 4,
                "summary": "Why experienced staff are involved in a large share of serious incidents.",
                "points": [
                    "Routine tasks breed shortcuts - treat every switching operation as if it were your first.",
                    "Stop and challenge: if anything differs from the plan, halt work and re-assess.",
                    "Fatigue, time pressure and distraction are the top contributors to human error.",
                    "Use point-and-call and three-way communication for every switching instruction.",
                ],
            },
            {
                "slug": "lessons",
                "title": "Lessons From Recent Incidents",
                "minutes": 5,
                "summary": "Real-world case studies and what went wrong.",
                "points": [
                    "Wrong-bay entry remains a leading cause of HV contact - always verify bay labels against the permit.",
                    "Portable earths removed out of sequence have caused back-feed injuries.",
                    "Arc flash during racking of breakers: always use remote racking where available.",
                    "Unreported near misses often precede serious incidents - report every one.",
                ],
            },
            {
                "slug": "updates",
                "title": "Procedure & Standard Updates",
                "minutes": 4,
                "summary": "What has changed in the rules since your last course.",
                "points": [
                    "Review the latest revision of the site safety rules and permit procedures.",
                    "Check that your authorisation level matches the equipment you will operate.",
                    "Confirm calibration and test dates for detectors, gloves and earthing equipment.",
                    "Digital permits and electronic lock-boxes must be used where they are installed.",
                ],
            },
            {
                "slug": "mentoring",
                "title": "Leading & Mentoring Safely",
                "minutes": 3,
                "summary": "Your role in keeping new engineers and visitors safe.",
                "points": [
                    "When escorting visitors, keep them within sight and arm's reach at all times.",
                    "Brief new engineers on the specific hazards of each area before entering it.",
                    "Model the behaviour you expect: full PPE, permits, and no shortcuts.",
                    "Encourage questions - a new engineer who speaks up prevents accidents.",
                ],
            },
        ],
        "quiz": [
            {
                "q": "What is a leading cause of HV contact incidents?",
                "options": ["Wrong-bay entry", "Wearing gloves", "Using permits", "Calibrated testers"],
                "answer": 0,
            },
            {
                "q": "Which communication method should be used for switching instructions?",
                "options": ["Text message", "Three-way communication", "Hand signals only", "None needed"],
                "answer": 1,
            },
            {
                "q": "When escorting a visitor you should keep them...",
                "options": ["In the car park", "Within sight and arm's reach", "In any area they like", "Ahead of you by 20 m"],
                "answer": 1,
            },
            {
                "q": "Where available, breakers should be racked...",
                "options": ["Quickly by hand", "Remotely", "While energised and unprotected", "By a visitor"],
                "answer": 1,
            },
            {
                "q": "A task differs from what the permit describes. What do you do?",
                "options": ["Carry on carefully", "Stop work and re-assess", "Ask a visitor", "Finish then report"],
                "answer": 1,
            },
        ],
    },
}

# ---------------------------------------------------------------------------
# Power-substation layout. ``x``/``y``/``w``/``h`` place each zone on the SVG
# site map (viewBox 0 0 1000 600). ``allowed`` lists the roles that may check
# in to the area; visitors must always be escorted.
# ---------------------------------------------------------------------------
AREAS = [
    {
        "code": "GATE",
        "name": "Security Gate & Reception",
        "short": "Gate & Reception",
        "risk": "low",
        "x": 40, "y": 470, "w": 200, "h": 100,
        "allowed": ["visitor", "new", "experienced"],
        "hazards": ["Vehicle movements", "Uneven ground"],
        "ppe": ["High-visibility vest"],
    },
    {
        "code": "CTRL",
        "name": "Control Room",
        "risk": "low",
        "x": 40, "y": 300, "w": 200, "h": 140,
        "allowed": ["visitor", "new", "experienced"],
        "hazards": ["Accidental operation of controls", "Trip hazards from cables"],
        "ppe": ["None beyond site minimum"],
    },
    {
        "code": "RELAY",
        "name": "Relay & Protection Room",
        "risk": "medium",
        "x": 40, "y": 140, "w": 200, "h": 130,
        "allowed": ["new", "experienced"],
        "hazards": ["CT secondary open-circuit", "Live LV terminals", "Unintended tripping"],
        "ppe": ["Safety glasses", "Insulated tools"],
    },
    {
        "code": "BATT",
        "name": "Battery Room",
        "risk": "medium",
        "x": 40, "y": 30, "w": 200, "h": 80,
        "allowed": ["new", "experienced"],
        "hazards": ["Hydrogen gas", "Acid / electrolyte burns", "DC short circuit"],
        "ppe": ["Face shield", "Acid-resistant gloves", "Apron"],
    },
    {
        "code": "HVYARD",
        "name": "HV Switchyard",
        "risk": "high",
        "x": 280, "y": 30, "w": 420, "h": 230,
        "allowed": ["visitor", "new", "experienced"],
        "hazards": ["Live HV conductors", "Arc flash", "Step & touch potential", "Induced voltage"],
        "ppe": ["Helmet", "Arc-rated clothing", "Safety boots", "Safety glasses"],
    },
    {
        "code": "BUS",
        "name": "Busbar Gantry",
        "risk": "high",
        "x": 280, "y": 290, "w": 420, "h": 70,
        "allowed": ["experienced"],
        "hazards": ["Overhead live busbars", "Working at height", "Falling objects"],
        "ppe": ["Helmet with chin strap", "Harness", "Arc-rated clothing"],
    },
    {
        "code": "TX",
        "name": "Power Transformer Bay",
        "risk": "high",
        "x": 280, "y": 390, "w": 260, "h": 180,
        "allowed": ["visitor", "new", "experienced"],
        "hazards": ["Oil fire", "Live bushings", "Noise", "Hot surfaces"],
        "ppe": ["Helmet", "Hearing protection", "Arc-rated clothing"],
    },
    {
        "code": "CAP",
        "name": "Capacitor Bank",
        "risk": "high",
        "x": 570, "y": 390, "w": 130, "h": 180,
        "allowed": ["experienced"],
        "hazards": ["Stored charge after isolation", "Live HV", "Arc flash"],
        "ppe": ["Arc-rated clothing", "Insulating gloves", "Face shield"],
    },
    {
        "code": "GIS",
        "name": "Indoor GIS / Switchgear Hall",
        "short": "GIS / Switchgear Hall",
        "risk": "high",
        "x": 740, "y": 30, "w": 220, "h": 230,
        "allowed": ["new", "experienced"],
        "hazards": ["SF6 gas leaks", "Arc flash during switching", "Confined space"],
        "ppe": ["Arc hood", "Arc-rated clothing", "Gas detector"],
    },
    {
        "code": "CABLE",
        "name": "Cable Basement & Trenches",
        "short": "Cable Basement",
        "risk": "medium",
        "x": 740, "y": 290, "w": 220, "h": 130,
        "allowed": ["new", "experienced"],
        "hazards": ["Confined space", "Low oxygen", "Damaged cable insulation", "Flooding"],
        "ppe": ["Gas detector", "Helmet", "Torch"],
    },
    {
        "code": "MUSTER",
        "name": "Emergency Muster Point",
        "risk": "low",
        "x": 740, "y": 450, "w": 220, "h": 120,
        "allowed": ["visitor", "new", "experienced"],
        "hazards": ["None - safe assembly area"],
        "ppe": ["High-visibility vest"],
    },
]

AREAS_BY_CODE = {a["code"]: a for a in AREAS}
