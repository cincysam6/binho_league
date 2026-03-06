import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import base64

# ══════════════════════════════════════════════════════════════════════════════
# SLAYER PARK BINHO LEAGUE (SPBL) - Official League Management System
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SPBL - Slayer Park Binho League",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Storage Configuration ─────────────────────────────────────────────────────
DATA_DIR = "spbl_data"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
GAMES_FILE = os.path.join(DATA_DIR, "games.json")
COASTER_FILE = os.path.join(DATA_DIR, "coaster_cups.json")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

ensure_dirs()

# ── Initialize League with Founding Members ───────────────────────────────────
FOUNDING_MEMBERS = [
    "Skullcore", "Baby", "Sam", "Luken", 
    "Adam", "Dope", "Rick", "Doug"
]

LEAGUE_CHARTER = """
**Article I – Establishment**

The Slayer Park Binho League (SPBL) is hereby established as a competitive, organized Binho league founded on principles of being a Big Dirty. The SPBL shall operate under this Charter for all league matches, standings, and championship determinations.

**Article II – Founding Members**

The founding members are: Skullcore, Baby, Sam, Luken, Adam, Dope, Rick, and Doug.

**Article III – League Structure**

*Section 1 – Seasonal Format*

Each SPBL season shall be divided into two equal competitive phases: the Apertura (Opening Phase) and the Clausura (Closing Phase). Each Phase will last 5 months. Each phase will consist of scheduled league matches.

*Section 2 – Match Schedule*

Each competitor will play four (4) matches against every other competitor: two (2) home matches and two (2) away matches. With eight (8) competitors, each player has seven (7) opponents, resulting in twenty-eight (28) total league matches per competitor. Each phase will have 14 games total across the 5 month duration.

**Article IV – Match Regulations**

*Section 1 – Match Announcement*

A league match must be announced prior to kickoff to each other and at least one other league member. Failure to declare a match as an official league match before kickoff renders it ineligible for league standings.

*Section 2 – Home Team Privileges*

For all officially declared league matches, the Home Team shall have the right to select the Binho board and select the ball. Home and away designation shall follow the official schedule.

*Section 3 – Recording Results*

Final scores must be recorded immediately upon match completion and must include: winner, loser, final score, and goal differential. The League shall maintain official standings tracking wins, losses, and goal differential.

**Article V – Standings and Tiebreakers**

Standings shall be determined first by overall record (wins–losses). The first tiebreaker shall be goal differential. If overall record and goal differential do not resolve a league winner, the tied competitors shall compete in a best-of-three (3) playoff series. The winner of this playoff shall be declared the official phase champion. The last place team in each phase will be awarded a hat which they must wear to the following phase of play or face a fine of $10 dollars to the league coffers to be used for the end of the season celebration OR purchase of the one true big dirty cup.

**Article VI – Phase Champions (Slayer Park Cup)**

The competitor finishing first in the Apertura shall be crowned Apertura Champion. The competitor finishing first in the Clausura shall be crowned Clausura Champion. The best record across both will receive the Slayer Park Cup.

**Article VII – Year-End Binho Cup (Big Dirty Cup)**

At the conclusion of both league phases, a postseason tournament known as the Slayer Park Binho World Cup shall be held. The Apertura Champion and Clausura Champion shall each receive automatic byes into later rounds of the Binho Cup. If the same competitor wins both phases, bye allocation shall be determined by the winner of most monthly cups.

A 3 team, 2 group knockout phase will start the tournament with a double elimination format. Game cadence will be determined by league standings. Based on overall standings across both league phases the third-place team gets the 8th and 6th place teams, and the 4th place team will be placed with the 5th and 7th place teams.

**Article VIII – Coaster Cups**

In addition to league play, a tournament will take place each month between all competitors for a coaster cup. The coaster cup is the best of three knockout tournaments between all teams available that evening. The coaster cup wins will be aggregated at the end of the year with any tiebreakers being determined by a single elimination game. Seeding will be determined by random number draw prior to the start of the cup. A number between 1 and 10 will be drawn for each competitor with the highest and lowest numbers paired first and so on and so forth until all teams have been paired. The winner of the most coaster cups over the course of the year will earn one beverage of their choice from every other founding member to be delivered within 2 months of the competition's conclusion.

**Article IX – The One True Big Dirty**

If a member wins both the Slayer Park Cup and the Big Dirty Cup, they will be crowned the One True Big Dirty until another member repeats the feat. A Trophy shall be presented to the One True Big Dirty upon completion of this feat.

**Article X – Governance**

Any amendments to this Charter require approval by a majority (5 of 8) vote of the founding members. Disputes shall be resolved by majority vote of non-involved members. The spirit of the league shall prioritize competition, sportsmanship, and recorded history.
"""

def initialize_league():
    """Initialize the league with the 8 founding members"""
    if not os.path.exists(TEAMS_FILE) or not load_json(TEAMS_FILE, {}):
        teams = {}
        for member in FOUNDING_MEMBERS:
            teams[member] = {
                "joined": "2025-01-01",
                "founding_member": True
            }
        save_json(TEAMS_FILE, teams)
        return teams
    return load_json(TEAMS_FILE, {})

# ── Session State ─────────────────────────────────────────────────────────────
if "teams" not in st.session_state:
    st.session_state.teams = initialize_league()
if "games" not in st.session_state:
    st.session_state.games = load_json(GAMES_FILE, [])
if "coaster_cups" not in st.session_state:
    st.session_state.coaster_cups = load_json(COASTER_FILE, [])
if "current_phase" not in st.session_state:
    st.session_state.current_phase = "Apertura"

def save_state():
    save_json(TEAMS_FILE, st.session_state.teams)
    save_json(GAMES_FILE, st.session_state.games)
    save_json(COASTER_FILE, st.session_state.coaster_cups)

# ── Logo Management ───────────────────────────────────────────────────────────
def get_soccer_ball_svg():
    """Return base64 encoded soccer ball SVG"""
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">
  <defs>
    <radialGradient id="ballGrad" cx="40%" cy="40%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e0e0e0;stop-opacity:1" />
    </radialGradient>
  </defs>
  <circle cx="100" cy="100" r="95" fill="url(#ballGrad)" stroke="#333" stroke-width="2"/>
  <g fill="#1a1a1a">
    <polygon points="100,20 85,45 100,55 115,45"/>
    <polygon points="70,50 55,65 60,85 80,80"/>
    <polygon points="130,50 120,80 140,85 145,65"/>
    <polygon points="40,95 50,115 70,110 65,90"/>
    <polygon points="160,95 135,90 130,110 150,115"/>
    <polygon points="85,135 100,145 115,135 110,115 90,115"/>
    <polygon points="60,155 75,170 90,160 85,140"/>
    <polygon points="110,140 115,160 130,170 140,155"/>
  </g>
</svg>'''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

# ── Standings Calculator ──────────────────────────────────────────────────────
def compute_standings(phase_filter=None):
    """Calculate league standings"""
    teams = st.session_state.teams
    games = st.session_state.games
    
    if phase_filter:
        games = [g for g in games if g.get("phase") == phase_filter]
    
    stats = {
        name: {
            "P": 0, "W": 0, "D": 0, "L": 0,
            "GF": 0, "GA": 0, "GD": 0, "Pts": 0,
            "Form": []
        }
        for name in teams
    }
    
    for g in games:
        h, a = g["home"], g["away"]
        hs, as_ = g["home_score"], g["away_score"]
        
        if h not in stats or a not in stats:
            continue
            
        for team, scored, conceded in [(h, hs, as_), (a, as_, hs)]:
            stats[team]["P"] += 1
            stats[team]["GF"] += scored
            stats[team]["GA"] += conceded
            
            if scored > conceded:
                stats[team]["W"] += 1
                stats[team]["Pts"] += 3
                stats[team]["Form"].append("W")
            elif scored == conceded:
                stats[team]["D"] += 1
                stats[team]["Pts"] += 1
                stats[team]["Form"].append("D")
            else:
                stats[team]["L"] += 1
                stats[team]["Form"].append("L")
    
    for team in stats:
        stats[team]["GD"] = stats[team]["GF"] - stats[team]["GA"]
    
    rows = []
    for name, s in stats.items():
        form_str = "".join([
            '<span class="form-w">W</span>' if r == "W" else '<span class="form-l">L</span>'
            for r in s["Form"][-5:]
        ])
        rows.append({
            "Team": name,
            "P": s["P"],
            "W": s["W"],
            "D": s["D"],
            "L": s["L"],
            "GF": s["GF"],
            "GA": s["GA"],
            "GD": s["GD"],
            "Pts": s["Pts"],
            "Form": form_str,
        })
    
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        df.index += 1
        df.index.name = "Pos"
    
    return df

# ── Modern Minimalist CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Header */
    .spbl-header {
        background: #0a0a0a;
        border-radius: 16px;
        padding: 3rem 3rem 2.5rem 3rem;
        margin: -2rem -3rem 3rem -3rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .spbl-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #00ff87, #60efff);
    }
    
    .spbl-header h1 {
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1.5px;
    }
    
    .spbl-header .subtitle {
        font-size: 1.1rem;
        margin: 0.75rem 0 0 0;
        opacity: 0.6;
        font-weight: 400;
        letter-spacing: 0.3px;
    }
    
    .phase-badge {
        display: inline-block;
        background: linear-gradient(135deg, #00ff87, #60efff);
        color: #0a0a0a;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-left: 1rem;
        letter-spacing: 0.5px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border: none;
        padding: 0 0 1.5rem 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 0.8rem 1.5rem;
        background: #f5f5f5;
        color: #666;
        border: none;
        transition: all 0.2s;
    }
    
    .stTabs [aria-selected="true"] {
        background: #0a0a0a !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* League Table */
    .league-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .league-table thead {
        background: #0a0a0a;
        color: white;
    }
    
    .league-table th {
        padding: 1.2rem 1rem;
        text-align: center;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .league-table th:first-child {
        text-align: left;
        padding-left: 2rem;
    }
    
    .league-table td {
        padding: 1.2rem 1rem;
        text-align: center;
        border-bottom: 1px solid #f5f5f5;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .league-table td:first-child {
        text-align: left;
        padding-left: 2rem;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .league-table tbody tr:hover {
        background: #fafafa;
    }
    
    .league-table tbody tr:last-child td {
        border-bottom: none;
    }
    
    /* Position badges */
    .pos {
        display: inline-block;
        width: 32px;
        height: 32px;
        line-height: 32px;
        text-align: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 1rem;
        border-radius: 6px;
    }
    
    .pos-1 { background: linear-gradient(135deg, #FFD700, #FFA500); color: #000; }
    .pos-2 { background: linear-gradient(135deg, #C0C0C0, #808080); color: #000; }
    .pos-3 { background: linear-gradient(135deg, #CD7F32, #8B4513); color: #fff; }
    .pos-top4 { background: linear-gradient(135deg, #00ff87, #60efff); color: #0a0a0a; }
    .pos-bottom { background: linear-gradient(135deg, #ff4458, #ff0033); color: white; }
    .pos-normal { background: #f0f0f0; color: #333; }
    
    .team-logo {
        width: 32px;
        height: 32px;
        vertical-align: middle;
        margin-right: 1rem;
    }
    
    /* Form indicators */
    .form-w, .form-l {
        display: inline-block;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        font-weight: 700;
        font-size: 0.75rem;
        margin: 0 3px;
        border-radius: 6px;
    }
    
    .form-w {
        background: linear-gradient(135deg, #00ff87, #00d96e);
        color: #0a0a0a;
    }
    
    .form-l {
        background: linear-gradient(135deg, #ff4458, #ff0033);
        color: white;
    }
    
    /* Record Match Card */
    .record-card {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        max-width: 700px;
        margin: 0 auto;
    }
    
    .vs-divider {
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        color: #e0e0e0;
        margin: 1rem 0;
        letter-spacing: 2px;
    }
    
    .score-input-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #999;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    /* Match Cards */
    .match-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 2rem;
        transition: all 0.2s;
    }
    
    .match-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .match-card .team {
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    .match-card .home { text-align: right; }
    .match-card .away { text-align: left; }
    
    .match-card .score {
        background: #0a0a0a;
        color: white;
        font-weight: 800;
        font-size: 1.6rem;
        padding: 0.6rem 1.5rem;
        border-radius: 10px;
        min-width: 100px;
        text-align: center;
        letter-spacing: 3px;
    }
    
    .match-card .winner {
        color: #00ff87;
        font-weight: 700;
    }
    
    .match-date {
        font-size: 0.8rem;
        color: #999;
        margin-bottom: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 2rem 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.2s;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .stat-card .value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00ff87, #60efff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .stat-card .label {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-weight: 700;
        border-radius: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        transition: all 0.2s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ff87, #60efff);
        color: #0a0a0a;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,255,135,0.3);
    }
    
    /* Section Headers */
    h3 {
        color: #0a0a0a;
        font-weight: 800;
        font-size: 1.8rem;
        margin-bottom: 2rem;
        letter-spacing: -1px;
    }
    
    /* Coaster Cup Card */
    .coaster-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-left: 4px solid;
    }
    
    .coaster-card.winner {
        border-left-color: #00ff87;
        background: linear-gradient(90deg, rgba(0,255,135,0.05), white);
    }
    
    .coaster-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    .coaster-card .location {
        color: #666;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    
    /* Charter styling */
    .charter-content {
        background: white;
        border-radius: 12px;
        padding: 3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        line-height: 1.8;
    }
    
    .charter-content h2 {
        color: #0a0a0a;
        font-weight: 800;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .charter-content h3 {
        color: #333;
        font-weight: 700;
        font-size: 1.2rem;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="spbl-header">
    <h1>SLAYER PARK BINHO LEAGUE</h1>
    <div class="subtitle">
        Official League Management System
        <span class="phase-badge">{st.session_state.current_phase.upper()}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Navigation ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "League Table",
    "Record Result",
    "Fixtures & Results",
    "Team Stats",
    "Coaster Cups",
    "League Charter",
    "Settings"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEAGUE TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with co