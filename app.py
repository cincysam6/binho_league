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
LOGOS_DIR = os.path.join(DATA_DIR, "logos")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGOS_DIR, exist_ok=True)

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
if "current_phase" not in st.session_state:
    st.session_state.current_phase = "Apertura"

def save_state():
    save_json(TEAMS_FILE, st.session_state.teams)
    save_json(GAMES_FILE, st.session_state.games)

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
    """Calculate league standings with Premier League rules"""
    teams = st.session_state.teams
    games = st.session_state.games
    
    # Filter by phase if specified
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
            
        # Update stats for both teams
        for team, scored, conceded in [(h, hs, as_), (a, as_, hs)]:
            stats[team]["P"] += 1
            stats[team]["GF"] += scored
            stats[team]["GA"] += conceded
            
            if scored > conceded:  # Win
                stats[team]["W"] += 1
                stats[team]["Pts"] += 3
                stats[team]["Form"].append("W")
            elif scored == conceded:  # Draw
                stats[team]["D"] += 1
                stats[team]["Pts"] += 1
                stats[team]["Form"].append("D")
            else:  # Loss
                stats[team]["L"] += 1
                stats[team]["Form"].append("L")
    
    # Calculate goal difference
    for team in stats:
        stats[team]["GD"] = stats[team]["GF"] - stats[team]["GA"]
    
    # Build DataFrame
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
        # Sort by: Points desc, Goal Difference desc, Goals For desc
        df = df.sort_values(["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        df.index += 1
        df.index.name = "Pos"
    
    return df

# ── Premier League CSS Styling ────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Encode+Sans:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Encode Sans', -apple-system, sans-serif;
    }
    
    .block-container {
        padding: 1.5rem 2rem 3rem 2rem;
        max-width: 1200px;
    }
    
    /* Header */
    .spbl-header {
        background: linear-gradient(135deg, #38003c 0%, #2b0030 100%);
        border-radius: 0;
        padding: 2rem 2.5rem;
        margin: -1.5rem -2rem 2rem -2rem;
        color: white;
        border-bottom: 4px solid #00ff85;
    }
    
    .spbl-header h1 {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.5px;
        text-transform: uppercase;
    }
    
    .spbl-header .subtitle {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.85;
        font-weight: 400;
    }
    
    .phase-badge {
        display: inline-block;
        background: #00ff85;
        color: #38003c;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-left: 1rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #f7f7f7;
        border-bottom: 2px solid #ddd;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        font-weight: 700;
        font-size: 0.9rem;
        padding: 1rem 1.5rem;
        background: transparent;
        color: #555;
        border-bottom: 3px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #38003c !important;
        border-bottom: 3px solid #00ff85 !important;
    }
    
    /* League Table */
    .league-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        font-size: 0.95rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .league-table thead {
        background: #38003c;
        color: white;
    }
    
    .league-table th {
        padding: 1rem 0.75rem;
        text-align: center;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .league-table th:first-child {
        text-align: left;
        padding-left: 1.5rem;
    }
    
    .league-table td {
        padding: 1rem 0.75rem;
        text-align: center;
        border-bottom: 1px solid #f0f0f0;
        font-weight: 500;
    }
    
    .league-table td:first-child {
        text-align: left;
        padding-left: 1.5rem;
        font-weight: 600;
    }
    
    .league-table tbody tr:hover {
        background: #fafafa;
    }
    
    /* Position badges */
    .pos {
        display: inline-block;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        font-weight: 700;
        font-size: 0.85rem;
        margin-right: 0.75rem;
        border-radius: 2px;
    }
    
    .pos-1 { background: #FFD700; color: #000; }
    .pos-2 { background: #C0C0C0; color: #000; }
    .pos-3 { background: #CD7F32; color: #fff; }
    .pos-top4 { background: #00ff85; color: #38003c; }
    .pos-bottom { background: #ff4458; color: white; }
    .pos-normal { background: #f0f0f0; color: #333; }
    
    /* Team logo */
    .team-logo {
        width: 28px;
        height: 28px;
        vertical-align: middle;
        margin-right: 0.75rem;
    }
    
    /* Form indicators */
    .form-w {
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        background: #00ff85;
        color: #38003c;
        font-weight: 700;
        font-size: 0.75rem;
        margin: 0 2px;
        border-radius: 2px;
    }
    
    .form-l {
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        text-align: center;
        background: #ff4458;
        color: white;
        font-weight: 700;
        font-size: 0.75rem;
        margin: 0 2px;
        border-radius: 2px;
    }
    
    /* Match Cards */
    .match-card {
        background: white;
        border-left: 4px solid #38003c;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 1.5rem;
    }
    
    .match-card .team {
        font-weight: 600;
        font-size: 1rem;
    }
    
    .match-card .home { text-align: right; }
    .match-card .away { text-align: left; }
    
    .match-card .score {
        background: #38003c;
        color: white;
        font-weight: 900;
        font-size: 1.5rem;
        padding: 0.5rem 1.25rem;
        border-radius: 4px;
        min-width: 90px;
        text-align: center;
        letter-spacing: 2px;
    }
    
    .match-card .winner {
        color: #38003c;
    }
    
    .match-date {
        font-size: 0.8rem;
        color: #999;
        margin-bottom: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        border-radius: 4px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-top: 3px solid #00ff85;
    }
    
    .stat-card .value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #38003c;
        line-height: 1;
    }
    
    .stat-card .label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: #38003c;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 700;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        background: #2b0030;
    }
    
    /* Section Headers */
    h3 {
        color: #38003c;
        font-weight: 900;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        text-transform: uppercase;
        letter-spacing: -0.5px;
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "League Table",
    "Record Result",
    "Fixtures & Results",
    "Team Stats",
    "League Management"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEAGUE TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Current Standings")
    
    with col2:
        view_phase = st.selectbox(
            "View Phase",
            ["Overall", "Apertura", "Clausura"],
            label_visibility="collapsed"
        )
    
    # Calculate standings
    if view_phase == "Overall":
        df = compute_standings()
    else:
        df = compute_standings(phase_filter=view_phase)
    
    if df.empty:
        st.info("No matches recorded yet. Record your first match to see the table.")
    else:
        # Build HTML table
        rows_html = ""
        for pos, row in df.iterrows():
            # Position badge styling
            if pos == 1:
                pos_class = "pos-1"
            elif pos == 2:
                pos_class = "pos-2"
            elif pos == 3:
                pos_class = "pos-3"
            elif pos <= 4:
                pos_class = "pos-top4"
            elif pos == len(df):
                pos_class = "pos-bottom"
            else:
                pos_class = "pos-normal"
            
            logo = get_soccer_ball_svg()
            
            rows_html += f"""
            <tr>
                <td>
                    <span class="pos {pos_class}">{pos}</span>
                    <img src="{logo}" class="team-logo">
                    {row["Team"]}
                </td>
                <td>{row["P"]}</td>
                <td>{row["W"]}</td>
                <td>{row["D"]}</td>
                <td>{row["L"]}</td>
                <td>{row["GF"]}</td>
                <td>{row["GA"]}</td>
                <td><strong>{row["GD"]:+d}</strong></td>
                <td><strong>{row["Pts"]}</strong></td>
                <td>{row["Form"]}</td>
            </tr>
            """
        
        st.markdown(f"""
        <table class="league-table">
            <thead>
                <tr>
                    <th>Club</th>
                    <th>P</th>
                    <th>W</th>
                    <th>D</th>
                    <th>L</th>
                    <th>GF</th>
                    <th>GA</th>
                    <th>GD</th>
                    <th>Pts</th>
                    <th>Form</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Legend
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("🥇 Champion Position")
        with col2:
            st.caption("🟢 Top 4 (World Cup Qualification)")
        with col3:
            st.caption("🔴 Last Place (Hat of Shame)")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RECORD RESULT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Record Match Result")
    
    teams = list(st.session_state.teams.keys())
    
    if len(teams) < 2:
        st.warning("Insufficient teams in the league.")
    else:
        with st.form("record_match"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Home Team**")
                home_team = st.selectbox("Home", teams, label_visibility="collapsed")
                home_score = st.number_input("Home Score", 0, 7, 7, key="home_score")
            
            with col2:
                st.markdown("**Away Team**")
                away_team = st.selectbox("Away", [t for t in teams if t != home_team], label_visibility="collapsed")
                away_score = st.number_input("Away Score", 0, 7, 0, key="away_score")
            
            col3, col4 = st.columns(2)
            with col3:
                match_date = st.date_input("Match Date", value=datetime.today())
            with col4:
                phase = st.selectbox("Phase", ["Apertura", "Clausura"])
            
            submit = st.form_submit_button("Record Match", use_container_width=True)
            
            if submit:
                if home_score == away_score:
                    st.error("Binho matches cannot end in a draw. One team must reach 7.")
                elif home_score != 7 and away_score != 7:
                    st.error("Match must be played to 7 points.")
                elif home_team == away_team:
                    st.error("Home and away teams must be different.")
                else:
                    match = {
                        "id": len(st.session_state.games) + 1,
                        "home": home_team,
                        "away": away_team,
                        "home_score": int(home_score),
                        "away_score": int(away_score),
                        "date": str(match_date),
                        "phase": phase
                    }
                    st.session_state.games.append(match)
                    save_state()
                    
                    winner = home_team if home_score > away_score else away_team
                    st.success(f"✓ Match recorded: **{winner}** wins {home_score}–{away_score}")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FIXTURES & RESULTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Match Results")
    
    filter_phase = st.selectbox("Filter by Phase", ["All Matches", "Apertura", "Clausura"])
    
    games = st.session_state.games
    if filter_phase != "All Matches":
        games = [g for g in games if g.get("phase") == filter_phase]
    
    if not games:
        st.info("No matches recorded yet.")
    else:
        for g in reversed(games):
            winner = g["home"] if g["home_score"] > g["away_score"] else g["away"]
            
            home_class = "winner" if g["home"] == winner else ""
            away_class = "winner" if g["away"] == winner else ""
            
            st.markdown(f"""
            <div class="match-date">{g["date"]} • {g.get("phase", "N/A")}</div>
            <div class="match-card">
                <div class="team home {home_class}">{g["home"]}</div>
                <div class="score">{g["home_score"]} – {g["away_score"]}</div>
                <div class="team away {away_class}">{g["away"]}</div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TEAM STATS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Team Statistics")
    
    teams = st.session_state.teams
    if not teams:
        st.info("No teams in the league.")
    else:
        selected = st.selectbox("Select Team", list(teams.keys()))
        
        if selected:
            # Calculate team stats
            team_games = [g for g in st.session_state.games 
                         if g["home"] == selected or g["away"] == selected]
            
            wins = sum(1 for g in team_games if 
                      (g["home"] == selected and g["home_score"] > g["away_score"]) or
                      (g["away"] == selected and g["away_score"] > g["home_score"]))
            
            losses = len(team_games) - wins
            
            gf = sum(g["home_score"] if g["home"] == selected else g["away_score"] 
                    for g in team_games)
            ga = sum(g["away_score"] if g["home"] == selected else g["home_score"] 
                    for g in team_games)
            
            win_pct = round(wins / len(team_games) * 100) if team_games else 0
            
            # Display stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="value">{len(team_games)}</div>
                    <div class="label">Played</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="value">{wins}</div>
                    <div class="label">Wins</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="value">{gf}</div>
                    <div class="label">Goals For</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="value">{win_pct}%</div>
                    <div class="label">Win Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if team_games:
                st.markdown("#### Recent Results")
                for g in reversed(team_games[-5:]):
                    opp = g["away"] if g["home"] == selected else g["home"]
                    ts = g["home_score"] if g["home"] == selected else g["away_score"]
                    os = g["away_score"] if g["home"] == selected else g["home_score"]
                    result = "W" if ts > os else "L"
                    winner = selected if result == "W" else opp
                    
                    home_class = "winner" if g["home"] == winner else ""
                    away_class = "winner" if g["away"] == winner else ""
                    
                    st.markdown(f"""
                    <div class="match-date">{g["date"]}</div>
                    <div class="match-card">
                        <div class="team home {home_class}">{g["home"]}</div>
                        <div class="score">{g["home_score"]} – {g["away_score"]}</div>
                        <div class="team away {away_class}">{g["away"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — LEAGUE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### League Administration")
    
    st.markdown("#### Current Phase")
    new_phase = st.radio(
        "Select Active Phase",
        ["Apertura", "Clausura"],
        index=0 if st.session_state.current_phase == "Apertura" else 1
    )
    
    if new_phase != st.session_state.current_phase:
        st.session_state.current_phase = new_phase
        save_state()
        st.success(f"Phase changed to {new_phase}")
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### Founding Members")
    
    for member in FOUNDING_MEMBERS:
        st.markdown(f"""
        <div style="padding: 0.75rem; background: white; margin-bottom: 0.5rem; 
                    border-left: 3px solid #38003c; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
            <img src="{get_soccer_ball_svg()}" style="width: 24px; height: 24px; 
                 vertical-align: middle; margin-right: 0.75rem;">
            <strong>{member}</strong>
            <span style="color: #666; margin-left: 1rem; font-size: 0.85rem;">Founding Member</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("#### Danger Zone")
    
    with st.expander("⚠ Reset League Data"):
        st.warning("This will permanently delete all match results. Teams will be preserved.")
        if st.button("Reset All Matches", type="secondary"):
            st.session_state.games = []
            save_state()
            st.success("All match data has been cleared.")
            st.rerun()
