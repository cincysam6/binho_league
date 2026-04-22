import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import base64
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# SLAYER PARK BINHO LEAGUE (SPBL) - Official League Management System
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SPBL - Slayer Park Binho League",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Supabase Configuration ────────────────────────────────────────────────────
ADMIN_PASSWORD = "jodabean417"

@st.cache_resource
def init_supabase() -> Client:
    """Initialize Supabase client"""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# ── Logo Helper Functions ─────────────────────────────────────────────────────
def get_logo_path(owner_name):
    """Get the path to a team's logo - checks both .png and .jpeg"""
    logo_name = owner_name.lower().replace(" ", "_")
    
    # Try .png first
    png_path = Path(f"assets/logos/{logo_name}.png")
    if png_path.exists():
        return png_path
    
    # Try .jpeg
    jpeg_path = Path(f"assets/logos/{logo_name}.jpeg")
    if jpeg_path.exists():
        return jpeg_path
    
    # Try .jpg
    jpg_path = Path(f"assets/logos/{logo_name}.jpg")
    if jpg_path.exists():
        return jpg_path
    
    return None

@st.cache_data
def encode_logo(owner_name):
    """Encode logo to base64 for display"""
    logo_path = get_logo_path(owner_name)
    if logo_path and logo_path.exists():
        try:
            with open(logo_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                # Determine mime type
                ext = logo_path.suffix.lower()
                if ext == '.png':
                    mime = 'image/png'
                else:
                    mime = 'image/jpeg'
                return f"data:{mime};base64,{encoded}"
        except Exception as e:
            print(f"Error loading logo for {owner_name}: {e}")
    return None

def get_team_logo_img(owner_name, size=40):
    """Get team logo as img tag or emoji fallback"""
    logo_data = encode_logo(owner_name)
    if logo_data:
        return f'<img src="{logo_data}" width="{size}" height="{size}" style="border-radius: 50%; object-fit: cover; border: 2px solid #333;">'
    return f'<span style="font-size: {size}px;">⚽</span>'

# ── Data Loading Functions ────────────────────────────────────────────────────
def load_teams():
    """Load teams from Supabase"""
    response = supabase.table("teams").select("*").execute()
    teams = {}
    for team in response.data:
        teams[team["name"]] = {
            "joined": team["joined"],
            "founding_member": team["founding_member"],
            "club_name": team.get("club_name", "TBD"),
            "logo": team.get("logo")
        }
    return teams

def load_games():
    """Load games from Supabase"""
    response = supabase.table("games").select("*").order("id").execute()
    return response.data

def load_coaster_cups():
    """Load coaster cups from Supabase"""
    response = supabase.table("coaster_cups").select("*").order("id").execute()
    return response.data

def add_game(home, away, home_score, away_score, date, phase):
    """Add a game to Supabase"""
    data = {
        "home": home,
        "away": away,
        "home_score": home_score,
        "away_score": away_score,
        "date": str(date),
        "phase": phase
    }
    supabase.table("games").insert(data).execute()

def delete_game(game_id):
    """Delete a game from Supabase"""
    supabase.table("games").delete().eq("id", game_id).execute()

def add_coaster_cup(month, winner, location, date, cup_name=""):
    """Add a coaster cup to Supabase"""
    data = {
        "month": month,
        "winner": winner,
        "location": location,
        "date": str(date),
        "cup_name": cup_name
    }
    supabase.table("coaster_cups").insert(data).execute()

def reset_all_games():
    """Delete all games from Supabase"""
    supabase.table("games").delete().neq("id", 0).execute()

# ── League Charter ────────────────────────────────────────────────────────────
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

# ── Session State ─────────────────────────────────────────────────────────────
if "current_phase" not in st.session_state:
    st.session_state.current_phase = "Apertura"

# ── Standings Calculator ──────────────────────────────────────────────────────
def compute_standings(games, teams, phase_filter=None):
    """Calculate league standings"""
    if phase_filter:
        games = [g for g in games if g.get("phase") == phase_filter]
    
    stats = {
        name: {"MP": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Form": [], "club_name": data["club_name"]}
        for name, data in teams.items()
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
            "Owner": name,
            "Club": s['club_name'],
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
    
    return df

# ── Modern Slate/Indigo Theme CSS ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main { background-color: #0c111d; }

    .block-container {
        padding: 0.5rem 1rem 1rem 1rem !important;
        max-width: 1100px !important;
    }

    /* ── Header ── */
    .spbl-header {
        background: linear-gradient(160deg, #0f1f4e 0%, #0c1635 50%, #080d1a 100%);
        border-radius: 0;
        padding: 0;
        margin: -0.5rem -1rem 2rem -1rem;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 40px rgba(67, 97, 238, 0.25);
    }

    .spbl-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4361ee, #06b6d4, #818cf8, #4361ee);
        background-size: 200% 100%;
        animation: gradientShift 4s linear infinite;
    }

    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }

    .header-content {
        padding: 2.5rem 2rem;
        position: relative;
        text-align: center;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        letter-spacing: 4px;
        color: #ffffff;
        text-transform: uppercase;
    }

    .header-subtitle {
        font-size: 0.78rem;
        font-weight: 600;
        color: #7b8ff7;
        margin-top: 0.5rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    @media (max-width: 768px) {
        .header-title { font-size: 1.5rem; letter-spacing: 2px; }
        .header-content { padding: 1.5rem 1rem; }
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background: transparent;
        border-bottom: 1px solid #1e2a3a;
        padding-bottom: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #4a5568;
        border-radius: 4px 4px 0 0;
        padding: 0.75rem 1.25rem;
        font-weight: 600;
        font-size: 0.85rem;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        background: rgba(67, 97, 238, 0.08);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(67, 97, 238, 0.1) !important;
        color: #818cf8 !important;
        border-bottom-color: #4361ee !important;
    }

    /* ── Standings Table ── */
    .pl-table-wrapper {
        background: #131929;
        border-radius: 12px;
        overflow-x: auto;
        margin: 1rem 0;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }

    .pl-table {
        width: 100%;
        min-width: 800px;
        border-collapse: collapse;
    }

    .pl-table thead { background: #0c111d; }

    .pl-table th {
        padding: 0.875rem 0.75rem;
        text-align: center;
        font-weight: 700;
        font-size: 0.68rem;
        color: #8b96b0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 1px solid #1e2a3a;
    }

    .pl-table th:first-child { text-align: center; width: 50px; }
    .pl-table th:nth-child(2) { width: 60px; }
    .pl-table th:nth-child(3) { text-align: left; padding-left: 1rem; }

    .pl-table tbody tr {
        border-bottom: 1px solid #1e2a3a;
        transition: background 0.15s;
    }

    .pl-table tbody tr:hover { background: rgba(67, 97, 238, 0.06); }

    .pl-table tbody tr.rank-1  { border-left: 3px solid #10b981; }
    .pl-table tbody tr.rank-last { border-left: 3px solid #f43f5e; }

    .pl-table td {
        padding: 1rem 0.75rem;
        text-align: center;
        font-size: 0.9rem;
        color: #e2e8f0;
        font-weight: 500;
        background: #131929;
    }

    .pl-table td:first-child { color: #4a5568; font-weight: 700; font-size: 0.85rem; }
    .pl-table td:nth-child(2) { text-align: center; }
    .pl-table td:nth-child(3) { text-align: left; padding-left: 1rem; font-weight: 700; color: #f0f4ff; }
    .pl-table td:nth-child(4) { text-align: left; color: #4a5568; font-size: 0.82rem; }

    .pl-table .pts-col { font-weight: 800; color: #f0f4ff; font-size: 1rem; }

    .gd-positive { color: #10b981; font-weight: 700; }
    .gd-negative { color: #f43f5e; font-weight: 700; }
    .gd-neutral  { color: #4a5568; font-weight: 600; }

    /* ── Form Badges ── */
    .form-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 800;
        margin: 0 1px;
        color: #fff;
    }
    .form-w { background: #10b981; }
    .form-d { background: #f59e0b; }
    .form-l { background: #f43f5e; }

    /* ── Section headings ── */
    h3 {
        color: #f0f4ff;
        font-weight: 800;
        margin-bottom: 1.5rem;
        font-size: 1.4rem;
        letter-spacing: 0.5px;
    }

    /* ── Form inputs ── */
    .stSelectbox label, .stNumberInput label, .stDateInput label {
        color: #8b96b0 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    .stSelectbox > div > div, .stNumberInput > div > div, .stDateInput > div > div {
        background: #131929;
        color: #e2e8f0;
        border: 1px solid #2d3748;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: #4361ee;
        color: #ffffff;
        font-weight: 700;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        border: none;
        box-shadow: 0 4px 15px rgba(67, 97, 238, 0.35);
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: #5a75f0;
        box-shadow: 0 6px 22px rgba(67, 97, 238, 0.5);
        transform: translateY(-2px);
    }

    /* ── Match Cards ── */
    .match-card {
        background: #131929;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        border-left: 3px solid #4361ee;
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        gap: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
        transition: all 0.2s;
    }

    .match-card:hover {
        transform: translateX(4px);
        background: #1a2237;
        box-shadow: 0 4px 16px rgba(67, 97, 238, 0.15);
    }

    .match-team {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        font-size: 0.95rem;
        color: #e2e8f0;
    }

    .match-team.home { justify-content: flex-end; }
    .match-team.away { justify-content: flex-start; }

    .match-card .score {
        background: #1e2a3a;
        color: #f0f4ff;
        font-weight: 900;
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        letter-spacing: 3px;
        border: 1px solid #2d3748;
        min-width: 80px;
        text-align: center;
    }

    .match-card .winner { color: #10b981; }

    .match-date {
        font-size: 0.72rem;
        color: #4a5568;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    /* ── Team logo display ── */
    .team-logo-display {
        margin-top: 0.5rem;
        text-align: center;
    }

    /* ── Stat Cards ── */
    .stat-card {
        background: #131929;
        border-radius: 12px;
        padding: 1.5rem 1rem;
        text-align: center;
        border-top: 2px solid #4361ee;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .stat-card .value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #7b8ff7;
        line-height: 1;
    }

    .stat-card .label {
        font-size: 0.72rem;
        color: #4a5568;
        margin-top: 0.75rem;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1.5px;
    }

    /* ── Coaster Cards ── */
    .coaster-card {
        background: #131929;
        border-radius: 10px;
        padding: 1.1rem 1.5rem;
        margin-bottom: 0.625rem;
        border-left: 3px solid #2d3748;
        transition: all 0.2s;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .coaster-card:hover { transform: translateX(4px); background: #1a2237; }

    .coaster-card.winner {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, rgba(245,158,11,0.08), #131929);
    }

    .coaster-card h4 {
        margin: 0 0 0.4rem 0;
        font-size: 1rem;
        font-weight: 700;
        color: #f0f4ff;
    }

    .coaster-card .location { color: #4a5568; font-size: 0.82rem; }

    /* ── Charter ── */
    .charter-content {
        background: #131929;
        border-radius: 12px;
        padding: 2rem;
        line-height: 1.8;
        color: #8b96b0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* ── Record Card ── */
    .record-card {
        background: #131929;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }

    .vs-divider {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 900;
        color: #2d3748;
        margin: 1rem 0;
        letter-spacing: 4px;
    }

    /* ── H2H Table ── */
    .h2h-wrapper {
        background: #131929;
        border-radius: 12px;
        overflow-x: auto;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }

    .h2h-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
    }

    .h2h-table thead { background: #0c111d; }

    .h2h-table th {
        padding: 0.875rem 1rem;
        text-align: left;
        font-weight: 700;
        font-size: 0.68rem;
        color: #8b96b0;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 1px solid #1e2a3a;
    }

    .h2h-table th:nth-child(2) { text-align: center; }
    .h2h-table th:nth-child(3),
    .h2h-table th:nth-child(4),
    .h2h-table th:nth-child(5) { text-align: center; width: 60px; }

    .h2h-table tbody tr { border-bottom: 1px solid #1e2a3a; }
    .h2h-table tbody tr:hover { background: rgba(67, 97, 238, 0.06); }

    .h2h-table td {
        padding: 0.875rem 1rem;
        font-size: 0.9rem;
        color: #e2e8f0;
        font-weight: 500;
    }

    .h2h-table td:nth-child(2) { text-align: center; }
    .h2h-table td:nth-child(3),
    .h2h-table td:nth-child(4),
    .h2h-table td:nth-child(5) { text-align: center; font-weight: 700; }

    .h2h-w { color: #10b981; }
    .h2h-l { color: #f43f5e; }
    .h2h-none { color: #4a5568; font-style: italic; font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)

# ── Modern Header (No subtitle) ───────────────────────────────────────────────
st.markdown("""
<div class="spbl-header">
    <div class="header-content">
        <div class="header-title">Slayer Park Binho League</div>
        <div class="header-subtitle">Official League Management System</div>
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

# Load data from Supabase
teams = load_teams()
games = load_games()
coaster_cups = load_coaster_cups()

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
        df = compute_standings(games, teams)
    else:
        df = compute_standings(games, teams, phase_filter=view_phase)
    
    if df.empty:
        st.info("No matches recorded yet. Record your first match to see the table.")
    else:
        # Build Premier League style table with logos using st.components.v1.html
        def form_badges_html(form_str):
            badges = ""
            for ch in form_str:
                if ch == "W":
                    badges += '<span class="fb fb-w">W</span>'
                elif ch == "L":
                    badges += '<span class="fb fb-l">L</span>'
                elif ch == "D":
                    badges += '<span class="fb fb-d">D</span>'
            return badges or "—"

        rows_html = ""
        for idx, row in df.iterrows():
            rank = idx + 1
            rank_class = ""
            if rank == 1:
                rank_class = "rank-1"
            elif rank == len(df):
                rank_class = "rank-last"

            gd = row['GD']
            if gd > 0:
                gd_class = "gd-positive"
                gd_text = f"+{gd}"
            elif gd < 0:
                gd_class = "gd-negative"
                gd_text = str(gd)
            else:
                gd_class = "gd-neutral"
                gd_text = "0"

            logo_html = get_team_logo_img(row['Owner'], 40)
            form_html = form_badges_html(row['Last 5'])

            rows_html += f"""
            <tr class="{rank_class}">
                <td>{rank}</td>
                <td>{logo_html}</td>
                <td>{row['Club']}</td>
                <td>{row['Owner']}</td>
                <td>{row['MP']}</td>
                <td>{row['W']}</td>
                <td>{row['D']}</td>
                <td>{row['L']}</td>
                <td>{row['GF']}</td>
                <td>{row['GA']}</td>
                <td><span class="{gd_class}">{gd_text}</span></td>
                <td class="pts-col">{row['Pts']}</td>
                <td>{form_html}</td>
            </tr>
            """

        table_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; }}
                .pl-table-wrapper {{
                    background: #131929;
                    border-radius: 12px;
                    overflow-x: auto;
                    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
                }}
                .pl-table {{
                    width: 100%;
                    min-width: 800px;
                    border-collapse: collapse;
                }}
                .pl-table thead {{ background: #0c111d; }}
                .pl-table th {{
                    padding: 0.875rem 0.75rem;
                    text-align: center;
                    font-weight: 700;
                    font-size: 0.68rem;
                    color: #8b96b0;
                    text-transform: uppercase;
                    letter-spacing: 1.5px;
                    border-bottom: 1px solid #1e2a3a;
                }}
                .pl-table th:first-child {{ text-align: center; width: 50px; }}
                .pl-table th:nth-child(2) {{ width: 60px; }}
                .pl-table th:nth-child(3) {{ text-align: left; padding-left: 1rem; }}
                .pl-table tbody tr {{ border-bottom: 1px solid #1e2a3a; }}
                .pl-table tbody tr:hover {{ background: rgba(67,97,238,0.06); }}
                .pl-table tbody tr.rank-1  {{ border-left: 3px solid #10b981; }}
                .pl-table tbody tr.rank-last {{ border-left: 3px solid #f43f5e; }}
                .pl-table td {{
                    padding: 1rem 0.75rem;
                    text-align: center;
                    font-size: 0.9rem;
                    color: #e2e8f0;
                    font-weight: 500;
                    background: #131929;
                }}
                .pl-table td:first-child {{ color: #4a5568; font-weight: 700; font-size: 0.85rem; }}
                .pl-table td:nth-child(2) {{ text-align: center; }}
                .pl-table td:nth-child(3) {{ text-align: left; padding-left: 1rem; font-weight: 700; color: #f0f4ff; }}
                .pl-table td:nth-child(4) {{ text-align: left; color: #4a5568; font-size: 0.82rem; }}
                .pl-table .pts-col {{ font-weight: 800; color: #f0f4ff; font-size: 1rem; }}
                .gd-positive {{ color: #10b981; font-weight: 700; }}
                .gd-negative {{ color: #f43f5e; font-weight: 700; }}
                .gd-neutral  {{ color: #4a5568; font-weight: 600; }}
                .fb {{
                    display: inline-flex; align-items: center; justify-content: center;
                    width: 22px; height: 22px; border-radius: 4px;
                    font-size: 0.65rem; font-weight: 800; margin: 0 1px; color: #fff;
                }}
                .fb-w {{ background: #10b981; }}
                .fb-d {{ background: #f59e0b; }}
                .fb-l {{ background: #f43f5e; }}
            </style>
        </head>
        <body>
            <div class="pl-table-wrapper">
                <table class="pl-table">
                    <thead>
                        <tr>
                            <th></th>
                            <th></th>
                            <th>Club</th>
                            <th>Owner</th>
                            <th>MP</th>
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
            </div>
        </body>
        </html>
        """
        
        # Use components to render HTML properly
        st.components.v1.html(table_html, height=min(700, 150 + len(df) * 60), scrolling=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RECORD RESULT
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Record Match Result")
    
    team_names = list(teams.keys())
    
    if len(team_names) < 2:
        st.warning("Insufficient teams in the league.")
    else:
        st.markdown('<div class="record-card">', unsafe_allow_html=True)
        
        # Team selection with logos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Home Team**")
            home_team = st.selectbox(
                "Home", 
                team_names,
                format_func=lambda x: f"{teams[x]['club_name']} ({x})",
                label_visibility="collapsed", 
                key="home_sel"
            )
            # Display logo
            st.markdown(f'<div class="team-logo-display">{get_team_logo_img(home_team, 60)}</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Away Team**")
            away_team = st.selectbox(
                "Away", 
                [t for t in team_names if t != home_team],
                format_func=lambda x: f"{teams[x]['club_name']} ({x})",
                label_visibility="collapsed", 
                key="away_sel"
            )
            # Display logo
            st.markdown(f'<div class="team-logo-display">{get_team_logo_img(away_team, 60)}</div>', unsafe_allow_html=True)
        
        with st.form("record_match", clear_on_submit=True):
            col3, col4 = st.columns(2)
            
            with col3:
                home_score = st.number_input("Home Score", 0, 7, 7, key="home_score")
            
            with col4:
                away_score = st.number_input("Away Score", 0, 7, 0, key="away_score")
            
            st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)
            
            col5, col6 = st.columns(2)
            with col5:
                match_date = st.date_input("Match Date", value=datetime.today())
            with col6:
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
                    add_game(home_team, away_team, int(home_score), int(away_score), match_date, phase)
                    winner_name = home_team if home_score > away_score else away_team
                    winner_club = teams[winner_name]["club_name"]
                    st.success(f"✓ Match recorded: **{winner_club}** wins {home_score}–{away_score}")
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FIXTURES & RESULTS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Match Results")

    filter_phase = st.selectbox("Filter by Phase", ["All Matches", "Apertura", "Clausura"])

    # Pending delete confirmation — shown at top before the game list
    if st.session_state.get("pending_delete_id"):
        gid = st.session_state.pending_delete_id
        g_del = next((g for g in games if g["id"] == gid), None)
        if g_del:
            home_club = teams[g_del["home"]]["club_name"]
            away_club = teams[g_del["away"]]["club_name"]
            with st.form("confirm_delete_form"):
                st.warning(
                    f"Delete: **{home_club}** {g_del['home_score']}–{g_del['away_score']} "
                    f"**{away_club}** ({g_del['date']})"
                )
                passcode = st.text_input("Enter admin passcode", type="password")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Confirm Delete", use_container_width=True):
                        if passcode == ADMIN_PASSWORD:
                            delete_game(gid)
                            st.session_state.pending_delete_id = None
                            st.success("Match deleted!")
                            st.rerun()
                        else:
                            st.error("Incorrect passcode!")
                with col_b:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.pending_delete_id = None
                        st.rerun()

    filtered_games = games
    if filter_phase != "All Matches":
        filtered_games = [g for g in games if g.get("phase") == filter_phase]

    if not filtered_games:
        st.info("No matches recorded yet.")
    else:
        for g in reversed(filtered_games):
            home_owner = g["home"]
            away_owner = g["away"]
            home_club = teams[home_owner]["club_name"]
            away_club = teams[away_owner]["club_name"]

            winner = home_owner if g["home_score"] > g["away_score"] else away_owner

            home_class = "winner" if home_owner == winner else ""
            away_class = "winner" if away_owner == winner else ""

            home_logo = get_team_logo_img(home_owner, 44)
            away_logo = get_team_logo_img(away_owner, 44)

            col_card, col_del = st.columns([11, 1])
            with col_card:
                st.markdown(f"""
                <div class="match-date">{g["date"]} • {g.get("phase", "N/A")}</div>
                <div class="match-card">
                    <div class="match-team home {home_class}">
                        <span>{home_club}</span>
                        {home_logo}
                    </div>
                    <div class="score">{g["home_score"]} – {g["away_score"]}</div>
                    <div class="match-team away {away_class}">
                        {away_logo}
                        <span>{away_club}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                st.markdown("<div style='padding-top:1.6rem;'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{g['id']}", help="Delete this match"):
                    st.session_state.pending_delete_id = g["id"]
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TEAM STATS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Team Statistics")
    
    if not teams:
        st.info("No teams in the league.")
    else:
        selected = st.selectbox("Select Team", list(teams.keys()),
            format_func=lambda x: f"{teams[x]['club_name']} ({x})")
        
        st.markdown(
            f"""
            <div class="team-logo-display">
                {get_team_logo_img(selected, 90)}
                <div style="margin-top: 0.5rem; color: #fff; font-weight: 700; font-size: 1.1rem;">
                    {teams[selected]['club_name']}
                </div>
                <div style="color: #888; font-size: 0.9rem;">
                    Owner: {selected}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if selected:
            team_games = [g for g in games if g["home"] == selected or g["away"] == selected]
            
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
            
            # ── Cup Trophies ──────────────────────────────────────────────────
            team_cups = [c for c in coaster_cups if c["winner"] == selected]
            if team_cups:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Cup Trophies")
                trophy_cards = ""
                for cup in team_cups:
                    cup_label = cup.get("cup_name") or f"{cup['month']} Cup"
                    trophy_cards += f"""
                    <div style="
                        text-align:center;
                        background:#131929;
                        border-radius:10px;
                        padding:1rem 0.875rem;
                        min-width:90px;
                        max-width:120px;
                        border-top:2px solid #f59e0b;
                        box-shadow:0 2px 8px rgba(0,0,0,0.25);
                        font-family:'Inter',sans-serif;
                    ">
                        <div style="font-size:1.8rem;">&#127942;</div>
                        <div style="
                            font-size:0.68rem;
                            color:#f59e0b;
                            font-weight:700;
                            margin-top:0.4rem;
                            line-height:1.3;
                            word-break:break-word;
                        ">{cup_label}</div>
                    </div>
                    """
                cups_component = f"""
                <!DOCTYPE html><html><head>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@700&display=swap" rel="stylesheet">
                </head><body style="margin:0;padding:0;background:transparent;">
                <div style="display:flex;flex-wrap:wrap;gap:0.875rem;padding:0.25rem 0;">
                    {trophy_cards}
                </div>
                </body></html>
                """
                trophy_rows = max(1, -(-len(team_cups) // 6))
                st.components.v1.html(cups_component, height=trophy_rows * 110, scrolling=False)

            st.markdown("<br>", unsafe_allow_html=True)

            if team_games:
                st.markdown("#### Recent Results")
                for g in reversed(team_games[-5:]):
                    home_owner = g["home"]
                    away_owner = g["away"]
                    home_club = teams[home_owner]["club_name"]
                    away_club = teams[away_owner]["club_name"]

                    winner = home_owner if g["home_score"] > g["away_score"] else away_owner

                    home_class = "winner" if home_owner == winner else ""
                    away_class = "winner" if away_owner == winner else ""

                    home_logo = get_team_logo_img(home_owner, 44)
                    away_logo = get_team_logo_img(away_owner, 44)

                    st.markdown(f"""
                    <div class="match-date">{g["date"]}</div>
                    <div class="match-card">
                        <div class="match-team home {home_class}">
                            <span>{home_club}</span>
                            {home_logo}
                        </div>
                        <div class="score">{g["home_score"]} – {g["away_score"]}</div>
                        <div class="match-team away {away_class}">
                            {away_logo}
                            <span>{away_club}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Head-to-Head Table ────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### Head-to-Head Record")

            opponents = sorted(
                [t for t in teams.keys() if t != selected],
                key=lambda x: teams[x]['club_name']
            )

            h2h_rows = ""
            for opp in opponents:
                h2h_games = [
                    g for g in games if
                    (g["home"] == selected and g["away"] == opp) or
                    (g["away"] == selected and g["home"] == opp)
                ]

                opp_logo = get_team_logo_img(opp, 28)
                opp_club = teams[opp]['club_name']

                if not h2h_games:
                    results_html = '<span class="h2h-none">No matches yet</span>'
                    w_text = "–"
                    l_text = "–"
                    gd_text = "–"
                    gd_class = ""
                else:
                    results_html = ""
                    w_count = 0
                    l_count = 0
                    gd = 0

                    for g in h2h_games:
                        if g["home"] == selected:
                            scored, conceded = g["home_score"], g["away_score"]
                        else:
                            scored, conceded = g["away_score"], g["home_score"]

                        gd += scored - conceded
                        if scored > conceded:
                            results_html += '<span class="fb fb-w">W</span>'
                            w_count += 1
                        else:
                            results_html += '<span class="fb fb-l">L</span>'
                            l_count += 1

                    w_text = str(w_count)
                    l_text = str(l_count)
                    if gd > 0:
                        gd_text = f"+{gd}"
                        gd_class = "h2h-w"
                    elif gd < 0:
                        gd_text = str(gd)
                        gd_class = "h2h-l"
                    else:
                        gd_text = "0"
                        gd_class = ""

                h2h_rows += f"""
                <tr>
                    <td>
                        <span style="display:flex;align-items:center;gap:0.6rem;">
                            {opp_logo}
                            <span style="font-weight:600;color:#f0f4ff;">{opp_club}</span>
                        </span>
                    </td>
                    <td>{results_html}</td>
                    <td class="h2h-w">{w_text}</td>
                    <td class="h2h-l">{l_text}</td>
                    <td class="{gd_class}">{gd_text}</td>
                </tr>
                """

            h2h_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; }}
                    .h2h-wrapper {{
                        background: #131929;
                        border-radius: 12px;
                        overflow-x: auto;
                        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
                    }}
                    .h2h-table {{ width: 100%; border-collapse: collapse; }}
                    .h2h-table thead {{ background: #0c111d; }}
                    .h2h-table th {{
                        padding: 0.75rem 1rem;
                        text-align: left;
                        font-weight: 700;
                        font-size: 0.68rem;
                        color: #8b96b0;
                        text-transform: uppercase;
                        letter-spacing: 1.5px;
                        border-bottom: 1px solid #1e2a3a;
                    }}
                    .h2h-table th:nth-child(2) {{ text-align: center; }}
                    .h2h-table th:nth-child(3),
                    .h2h-table th:nth-child(4),
                    .h2h-table th:nth-child(5) {{ text-align: center; width: 55px; }}
                    .h2h-table tbody tr {{ border-bottom: 1px solid #1e2a3a; }}
                    .h2h-table tbody tr:hover {{ background: rgba(67,97,238,0.06); }}
                    .h2h-table td {{
                        padding: 0.75rem 1rem;
                        font-size: 0.88rem;
                        color: #e2e8f0;
                        font-weight: 500;
                        background: #131929;
                    }}
                    .h2h-table td:nth-child(2) {{ text-align: center; }}
                    .h2h-table td:nth-child(3),
                    .h2h-table td:nth-child(4),
                    .h2h-table td:nth-child(5) {{ text-align: center; font-weight: 700; }}
                    .fb {{
                        display: inline-flex; align-items: center; justify-content: center;
                        width: 24px; height: 24px; border-radius: 4px;
                        font-size: 0.68rem; font-weight: 800; margin: 0 2px; color: #fff;
                    }}
                    .fb-w {{ background: #10b981; }}
                    .fb-l {{ background: #f43f5e; }}
                    .h2h-w {{ color: #10b981; }}
                    .h2h-l {{ color: #f43f5e; }}
                    .h2h-none {{ color: #4a5568; font-style: italic; font-size: 0.82rem; }}
                </style>
            </head>
            <body>
                <div class="h2h-wrapper">
                    <table class="h2h-table">
                        <thead>
                            <tr>
                                <th>Opponent</th>
                                <th>Results</th>
                                <th>W</th>
                                <th>L</th>
                                <th>GD</th>
                            </tr>
                        </thead>
                        <tbody>
                            {h2h_rows}
                        </tbody>
                    </table>
                </div>
            </body>
            </html>
            """

            h2h_height = max(220, 55 + len(opponents) * 55)
            st.components.v1.html(h2h_html, height=h2h_height, scrolling=False)

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
    
    with st.expander("➕ Record Coaster Cup Winner", expanded=len(coaster_cups) == 0):
        with st.form("add_coaster_cup"):
            cup_name = st.text_input("Cup Name", placeholder="e.g. The Golden Pint Cup")

            cup_month = st.selectbox("Month", [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ])

            cup_winner = st.selectbox("Winner", list(teams.keys()),
                format_func=lambda x: f"{teams[x]['club_name']} ({x})")

            cup_location = st.selectbox("Location", [
                "13 Below Brewery",
                "West Side Brewery",
                "Other"
            ])

            if st.form_submit_button("Record Coaster Cup", use_container_width=True):
                add_coaster_cup(cup_month, cup_winner, cup_location, datetime.today().date(), cup_name.strip())
                label = cup_name.strip() or f"{cup_month} Cup"
                st.success(f"✓ **{label}** recorded: **{teams[cup_winner]['club_name']}** wins!")
                st.rerun()

    if coaster_cups:
        cup_wins = {}
        for cup in coaster_cups:
            winner = cup["winner"]
            cup_wins[winner] = cup_wins.get(winner, 0) + 1

        st.markdown("#### Coaster Cup Leaderboard")
        sorted_winners = sorted(cup_wins.items(), key=lambda x: x[1], reverse=True)

        for i, (winner, wins) in enumerate(sorted_winners, 1):
            badge = "🏆" if i == 1 else f"{i}."
            club_name = teams[winner]["club_name"]
            logo_html = get_team_logo_img(winner, 40)
            st.markdown(f"""
            <div class="coaster-card {'winner' if i == 1 else ''}">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                    {logo_html}
                    <h4 style="margin:0;">{badge} {club_name} — {wins} Cup{"s" if wins != 1 else ""}</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("#### All Coaster Cups")
        for cup in reversed(coaster_cups):
            club_name = teams[cup["winner"]]["club_name"]
            logo_html = get_team_logo_img(cup["winner"], 40)
            cup_label = cup.get("cup_name") or f"{cup['month']} Cup"
            st.markdown(f"""
            <div class="coaster-card winner">
                <div style="display:flex;align-items:center;gap:0.75rem;">
                    {logo_html}
                    <div>
                        <h4 style="margin:0 0 0.25rem 0;">🏆 {cup_label}</h4>
                        <div class="location">📍 {cup["location"]} • {cup["date"]}</div>
                    </div>
                </div>
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
        st.success(f"Phase changed to {new_phase}")
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### Danger Zone")
    
    with st.expander("⚠ Reset All League Data"):
        st.warning("This requires admin passcode and will permanently delete ALL match results from Supabase.")
        with st.form("reset_form"):
            reset_passcode = st.text_input("Enter passcode", type="password")
            if st.form_submit_button("Reset All Matches", type="secondary"):
                if reset_passcode == ADMIN_PASSWORD:
                    reset_all_games()
                    st.success("All match data has been cleared from Supabase.")
                    st.rerun()
                else:
                    st.error("Incorrect passcode!")