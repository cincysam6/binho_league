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
    """Calculate league standings - simplified columns"""
    teams = st.session_state.teams
    games = st.session_state.games
    
    if phase_filter:
        games = [g for g in games if g.get("phase") == phase_filter]
    
    stats = {
        name: {"W": 0, "L": 0, "GF": 0, "GA": 0}
        for name in teams
    }
    
    for g in games:
        h, a = g["home"], g["away"]
        hs, as_ = g["home_score"], g["away_score"]
        
        if h not in stats or a not in stats:
            continue
            
        # Home team
        stats[h]["GF"] += hs
        stats[h]["GA"] += as_
        if hs > as_:
            stats[h]["W"] += 1
        else:
            stats[h]["L"] += 1
        
        # Away team
        stats[a]["GF"] += as_
        stats[a]["GA"] += hs
        if as_ > hs:
            stats[a]["W"] += 1
        else:
            stats[a]["L"] += 1
    
    rows = []
    for name, s in stats.items():
        rows.append({
            "Team": name,
            "W": s["W"],
            "L": s["L"],
            "GF": s["GF"],
            "GA": s["GA"],
        })
    
    df = pd.DataFrame(rows)
    if not df.empty:
        # Sort by wins (desc), then goal diff (desc)
        df['GD'] = df['GF'] - df['GA']
        df = df.sort_values(["W", "GD", "GF"], ascending=False).reset_index(drop=True)
        df = df.drop('GD', axis=1)  # Remove temp column
    
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
    
    /* Streamlit dataframe styling */
    .stDataFrame {
        width: 100%;
    }
    
    .stDataFrame > div {
        width: 100% !important;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        width: 100% !important;
    }
    
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
    
    h3 {
        color: #0a0a0a;
        font-weight: 800;
        font-size: 1.8rem;
        margin-bottom: 2rem;
        letter-spacing: -1px;
    }
    
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
    
    .charter-content {
        background: white;
        border-radius: 12px;
        padding: 3rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        line-height: 1.8;
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
    
    with col1:
        st.markdown("### Current Standings")
    
    with col2:
        view_phase = st.selectbox(
            "View Phase",
            ["Overall", "Apertura", "Clausura"],
            label_visibility="collapsed"
        )
    
    if view_phase == "Overall":
        df = compute_standings()
    else:
        df = compute_standings(phase_filter=view_phase)
    
    if df.empty:
        st.info("No matches recorded yet. Record your first match to see the table.")
    else:
        # Display using Streamlit's dataframe with custom config
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Team": st.column_config.TextColumn("Team", width="large"),
                "W": st.column_config.NumberColumn("Wins", width="small"),
                "L": st.column_config.NumberColumn("Losses", width="small"),
                "GF": st.column_config.NumberColumn("Goals For", width="small"),
                "GA": st.column_config.NumberColumn("Goals Against", width="small"),
            }
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RECORD RESULT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Record Match Result")
    
    teams = list(st.session_state.teams.keys())
    
    if len(teams) < 2:
        st.warning("Insufficient teams in the league.")
    else:
        st.markdown('<div class="record-card">', unsafe_allow_html=True)
        
        with st.form("record_match", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="score-input-label">Home Team</div>', unsafe_allow_html=True)
                home_team = st.selectbox("Home", teams, label_visibility="collapsed", key="home_sel")
                home_score = st.number_input("Home Score", 0, 7, 7, key="home_score")
            
            with col2:
                st.markdown('<div class="score-input-label">Away Team</div>', unsafe_allow_html=True)
                away_team = st.selectbox("Away", [t for t in teams if t != home_team], label_visibility="collapsed", key="away_sel")
                away_score = st.number_input("Away Score", 0, 7, 0, key="away_score")
            
            st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)
            
            col3, col4 = st.columns(2)
            with col3:
                match_date = st.date_input("Match Date", value=datetime.today())
            with col4:
                phase = st.selectbox("Phase", ["Apertura", "Clausura"])
            
            st.markdown("<br>", unsafe_allow_html=True)
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
        
        st.markdown('</div>', unsafe_allow_html=True)

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
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            if team_games:
                st.markdown("#### Recent Results")
                for g in reversed(team_games[-5:]):
                    winner = g["home"] if g["home_score"] > g["away_score"] else g["away"]
                    
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
# TAB 5 — COASTER CUPS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### Monthly Coaster Cups")
    
    st.markdown("""
    The Coaster Cup is a monthly knockout tournament. The winner of the most cups over the year 
    earns one beverage of their choice from every other founding member.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("➕ Record Coaster Cup Winner", expanded=len(st.session_state.coaster_cups) == 0):
        with st.form("add_coaster_cup"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                cup_month = st.selectbox("Month", [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ])
            
            with col2:
                cup_winner = st.selectbox("Winner", list(st.session_state.teams.keys()))
            
            with col3:
                cup_location = st.selectbox("Location", [
                    "13 Below Brewery",
                    "West Side Brewery",
                    "Other"
                ])
            
            if st.form_submit_button("Record Coaster Cup", use_container_width=True):
                cup = {
                    "month": cup_month,
                    "winner": cup_winner,
                    "location": cup_location,
                    "date": str(datetime.today().date())
                }
                st.session_state.coaster_cups.append(cup)
                save_state()
                st.success(f"✓ {cup_month} Coaster Cup recorded: **{cup_winner}** wins!")
                st.rerun()
    
    if st.session_state.coaster_cups:
        cup_wins = {}
        for cup in st.session_state.coaster_cups:
            winner = cup["winner"]
            cup_wins[winner] = cup_wins.get(winner, 0) + 1
        
        st.markdown("#### Coaster Cup Leaderboard")
        sorted_winners = sorted(cup_wins.items(), key=lambda x: x[1], reverse=True)
        
        for i, (winner, wins) in enumerate(sorted_winners, 1):
            badge = "🏆" if i == 1 else f"{i}."
            st.markdown(f"""
            <div class="coaster-card {'winner' if i == 1 else ''}">
                <h4>{badge} {winner} — {wins} Cup{"s" if wins != 1 else ""}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        st.markdown("#### All Coaster Cups")
        for cup in reversed(st.session_state.coaster_cups):
            st.markdown(f"""
            <div class="coaster-card winner">
                <h4>{cup["month"]} — {cup["winner"]}</h4>
                <div class="location">📍 {cup["location"]} • {cup["date"]}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No Coaster Cups recorded yet.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — LEAGUE CHARTER
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("### SPBL League Charter")
    
    st.markdown(f'<div class="charter-content">{LEAGUE_CHARTER}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
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
        <div style="padding: 1rem; background: white; margin-bottom: 0.5rem; 
                    border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
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