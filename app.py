import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="MLB Command Center", layout="wide", page_icon="⚾")
st.title("⚡ Live Situational Command Center")

# Connection Setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_UNIQUE_ID/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

dashboard_placeholder = st.empty()

while True:
    try:
        # Pull the multi-game table matrix
        live_data = conn.read(spreadsheet=SHEET_URL, ttl=0).dropna(how="all")
        
        with dashboard_placeholder.container():
            if not live_data.empty:
                # Loop through every active row in the Google Sheet and render independently
                for index, game in live_data.iterrows():
                    match_title = f"🏟️ {game['away_team']} @ {game['home_team']}"
                    
                    with st.expander(f"{match_title}  |  📊 Live Probability: Home {float(game['home_win_prob'])*100:.1f}%", expanded=True):
                        # 1. Main Scoreboard Row
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric(label="Current Score", value=f"{game['away_team']} {int(game['away_score'])} - {int(game['home_score'])} {game['home_team']}")
                        with c2:
                            st.metric(label="Game Frame", value=f"{game['half_inning']} of {int(game['inning'])}")
                        with c3:
                            st.metric(label="Outs", value="🔴" * int(game['outs']) if int(game['outs']) > 0 else "0 Outs")
                        with c4:
                            # Base Runners UI Visualizer
                            b1 = "❶" if int(game['runner_1b']) == 1 else "○"
                            b2 = "❷" if int(game['runner_2b']) == 1 else "○"
                            b3 = "❸" if int(game['runner_3b']) == 1 else "○"
                            st.metric(label="Base paths Matrix", value=f"{b3}   {b2}   {b1}")
                            
                        st.markdown(" ")
                        
                        # 2. Live Personnel Matchup & Ratings Row
                        col_p1, col_p2, col_p3 = st.columns(3)
                        with col_p1:
                            st.markdown(f"**⚾ Active Pitcher:** {game['pitcher_name']}")
                            st.caption(f"FanGraphs Prior K-Metric Baseline: `{game['pitcher_rating']}`")
                        with col_p2:
                            st.markdown(f"**⚔️ At-Bat Franchise:** {game['batting_team']}")
                            st.caption(f"Team Recent Offense Form Tracker: `{game['batter_rating']}`")
                        with col_p3:
                            # Clear predictive target metric outputs
                            st.progress(float(game['home_win_prob']), text=f"**Home Team Win Equity: {float(game['home_win_prob'])*100:.1f}%**")
                        
                        st.markdown("---")
            else:
                st.info("📡 Command center online. Waiting for game-state changes to populate stream...")
                
    except Exception as e:
        st.warning("📡 Waiting for active game state frames to populate...")
        
    time.sleep(15)
