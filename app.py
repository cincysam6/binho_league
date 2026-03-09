import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ══════════════════════════════════════════════════════════════════════════════
# SLAYER PARK BINHO LEAGUE (SPBL) - Official League Management System
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SPBL - Slayer Park Binho League",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Storage Configuration ─────────────────────────────────────────────────────
DATA_DIR = "spbl_data"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
GAMES_FILE = os.path.join(DATA_DIR, "games.json")
COASTER_FILE = os.path.join(DATA_DIR, "coaster_cups.json")
ADMIN_PASSWORD = "jodabean417"

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

# ── Standings Calculator ──────────────────────────────────────────────────────
def compute_standings(phase_filter=None):
    """Calculate league standings"""
    teams = st.session_state.teams
    games = st.session_state.games
    
    if phase_filter:
        games = [g for g in games if g.get("phase") == phase_filter]
    
    stats = {
        name: {"MP": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Form": []}
        for name in teams
    }
    
    for g in games:
        h, a = g["home"], g["away"]
        hs, as_ = g["home_score"], g["away_score"]
        
        if h not in stats or a not in stats:
            continue
            
        for team, scored, conceded in [(h, hs, as_), (a, as_, hs)]:
            stats[team]["MP"] += 1
            stats[team]["GF"] += scored
            stats[team]["GA"] += conceded
            
            if scored > conceded:
                stats[team]["W"] += 1
                stats[team]["Form"].append("W")
            elif scored == conceded:
                stats[team]["D"] += 1
                stats[team]["Form"].append("D")
            else:
                stats[team]["L"] += 1
                stats[team]["Form"].append("L")
    
    rows = []
    for name, s in stats.items():
        gd = s["GF"] - s["GA"]
        pts = (s["W"] * 3) + s["D"]
        form = "".join(s["Form"][-5:])
        rows.append({
            "Club": f"⚽ {name}",
            "MP": s["MP"],
            "W": s["W"],
            "D": s["D"],
            "L": s["L"],
            "GF": s["GF"],
            "GA": s["GA"],
            "GD": gd,
            "Pts": pts,
            "Last 5": form
        })
    
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.index.name = "Rank"
    
    return df

# ── Dark Theme CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #1a1a1a; }
    
    .block-container {
        padding: 1rem !important;
        max-width: 1100px !important;
    }
    
    /* Header */
    .spbl-header {
        background: linear-gradient(135deg, #38003c, #2b0030);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        color: white;
        border-bottom: 3px solid #00ff85;
    }
    
    .spbl-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 900;
        letter-spacing: -0.5px;
    }
    
    .spbl-header .subtitle {
        margin-top: 0.5rem;
        font-size: 0.85rem;
        opacity: 0.8;
    }
    
    .phase-badge {
        display: inline-block;
        background: #00ff85;
        color: #38003c;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.7rem;
        margin-left: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2a2a2a;
        color: #999;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: #38003c !important;
        color: #00ff85 !important;
    }
    
    /* Table Styling */
    .stDataFrame {
        background: #1e1e1e;
        border-radius: 12px;
        overflow: hidden;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: #1e1e1e;
    }
    
    .stDataFrame thead tr th {
        background-color: #2a2a2a !important;
        color: #999 !important;
        font-weight: 700 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 1rem 0.75rem !important;
        border-bottom: 1px solid #333 !important;
    }
    
    .stDataFrame tbody tr td {
        background-color: #1e1e1e !important;
        color: #fff !important;
        font-size: 0.9rem !important;
        padding: 1rem 0.75rem !important;
        border-bottom: 1px solid #2a2a2a !important;
    }
    
    .stDataFrame tbody tr:hover td {
        background-color: #252525 !important;
    }
    
    .stDataFrame tbody tr:first-child td {
        border-left: 3px solid #00ff85;
    }
    
    .stDataFrame tbody tr:last-child td {
        border-left: 3px solid #ff4458;
    }
    
    h3 {
        color: #fff;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .stSelectbox label, .stNumberInput label, .stDateInput label {
        color: #999 !important;
    }
    
    .stSelectbox > div > div, .stNumberInput > div > div, .stDateInput > div > div {
        background: #2a2a2a;
        color: #fff;
        border: 1px solid #444;
    }
    
    .stButton > button {
        background: #38003c;
        color: #00ff85;
        font-weight: 700;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
    }
    
    .stButton > button:hover {
        background: #2b0030;
    }
    
    /* Match Cards */
    .match-card {
        background: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #38003c;
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 1rem;
    }
    
    .match-card .team {
        font-weight: 600;
        font-size: 0.9rem;
        color: #fff;
    }
    
    .match-card .home { text-align: right; }
    .match-card .away { text-align: left; }
    
    .match-card .score {
        background: #38003c;
        color: #00ff85;
        font-weight: 800;
        font-size: 1.2rem;
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        letter-spacing: 2px;
    }
    
    .match-card .winner {
        color: #00ff85;
    }
    
    .match-date {
        font-size: 0.7rem;
        color: #999;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Stat Cards */
    .stat-card {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 1.25rem 1rem;
        text-align: center;
        border-top: 3px solid #00ff85;
    }
    
    .stat-card .value {
        font-size: 2rem;
        font-weight: 800;
        color: #00ff85;
        line-height: 1;
    }
    
    .stat-card .label {
        font-size: 0.7rem;
        color: #999;
        margin-top: 0.5rem;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    /* Coaster Cards */
    .coaster-card {
        background: #1e1e1e;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid #444;
    }
    
    .coaster-card.winner {
        border-left-color: #00ff85;
        background: linear-gradient(90deg, rgba(0,255,135,0.1), #1e1e1e);
    }
    
    .coaster-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 700;
        color: #fff;
    }
    
    .coaster-card .location {
        color: #999;
        font-size: 0.85rem;
    }
    
    /* Charter */
    .charter-content {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 1.5rem;
        line-height: 1.7;
        color: #ddd;
    }
    
    .record-card {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    .vs-divider {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 800;
        color: #444;
        margin: 0.75rem 0;
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
    "Table",
    "Record",
    "Results",
    "Stats",
    "Cups",
    "Charter",
    "Settings"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — LEAGUE TABLE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### League Standings")
    
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
        st.dataframe(
            df,
            use_container_width=True,
            height=min(600, 100 + len(df) * 50),
            column_config={
                "Club": st.column_config.TextColumn("Club", width="large"),
                "MP": st.column_config.NumberColumn("MP", width="small"),
                "W": st.column_config.NumberColumn("W", width="small"),
                "D": st.column_config.NumberColumn("D", width="small"),
                "L": st.column_config.NumberColumn("L", width="small"),
                "GF": st.column_config.NumberColumn("GF", width="small"),
                "GA": st.column_config.NumberColumn("GA", width="small"),
                "GD": st.column_config.NumberColumn("GD", width="small"),
                "Pts": st.column_config.NumberColumn("Pts", width="small"),
                "Last 5": st.column_config.TextColumn("Last 5", width="medium"),
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
                st.markdown("**Home Team**")
                home_team = st.selectbox("Home", teams, label_visibility="collapsed", key="home_sel")
                home_score = st.number_input("Home Score", 0, 7, 7, key="home_score")
            
            with col2:
                st.markdown("**Away Team**")
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
    
    col1, col2 = st.columns([3, 1])
    with col1:
        filter_phase = st.selectbox("Filter by Phase", ["All Matches", "Apertura", "Clausura"])
    with col2:
        if st.session_state.games:
            if st.button("🗑️ Delete", use_container_width=True):
                st.session_state.show_delete_confirm = True
    
    if "show_delete_confirm" in st.session_state and st.session_state.show_delete_confirm:
        with st.form("delete_match_form"):
            st.warning("⚠️ Enter passcode to delete a match")
            passcode = st.text_input("Passcode", type="password")
            match_to_delete = st.selectbox("Select match to delete", 
                [f"{g['date']} - {g['home']} {g['home_score']}-{g['away_score']} {g['away']}" 
                 for g in reversed(st.session_state.games)])
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.form_submit_button("Confirm Delete", use_container_width=True):
                    if passcode == ADMIN_PASSWORD:
                        match_idx = len(st.session_state.games) - 1 - [f"{g['date']} - {g['home']} {g['home_score']}-{g['away_score']} {g['away']}" 
                         for g in reversed(st.session_state.games)].index(match_to_delete)
                        del st.session_state.games[match_idx]
                        save_state()
                        st.session_state.show_delete_confirm = False
                        st.success("Match deleted!")
                        st.rerun()
                    else:
                        st.error("Incorrect passcode!")
            with col_b:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_delete_confirm = False
                    st.rerun()
    
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
            
            st.markdown("<br>", unsafe_allow_html=True)
            
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
            cup_month = st.selectbox("Month", [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ])
            
            cup_winner = st.selectbox("Winner", list(st.session_state.teams.keys()))
            
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
    st.markdown("#### Danger Zone")
    
    with st.expander("⚠ Reset All League Data"):
        st.warning("This requires admin passcode and will permanently delete ALL match results.")
        with st.form("reset_form"):
            reset_passcode = st.text_input("Enter passcode", type="password")
            if st.form_submit_button("Reset All Matches", type="secondary"):
                if reset_passcode == ADMIN_PASSWORD:
                    st.session_state.games = []
                    save_state()
                    st.success("All match data has been cleared.")
                    st.rerun()
                else:
                    st.error("Incorrect passcode!")