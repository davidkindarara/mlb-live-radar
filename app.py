import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="MLB Command Center", layout="wide", page_icon="⚾")
st.title("⚡ Live Situational Command Center")

# Connection Setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g8Y8iPLCw2NZDH9t27bbFAYDvnlCL7RlbNqIDa1RV9o/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

dashboard_placeholder = st.empty()

while True:
    try:
        # Pull the multi-game table matrix matrix cleanly
        live_data = conn.read(spreadsheet=SHEET_URL, ttl=0).dropna(how="all")
        
        with dashboard_placeholder.container():
            if not live_data.empty:
                # Loop through every active row in the Google Sheet and render independently
                for index, game in live_data.iterrows():
                    match_title = f"🏟️ {game['away_team']} @ {game['home_team']}"
                    home_p = float(game['home_win_prob'])
                    
                    with st.expander(f"{match_title}  |  📊 Live Probability: Home {home_p*100:.1f}%", expanded=True):
                        # 1. Main Scoreboard Row
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric(label="Current Score", value=f"{game['away_team']} {int(game['away_score'])} - {int(game['home_score'])} {game['home_team']}")
                        with c2:
                            st.metric(label="Game Frame", value=f"{game['half_inning']} of {int(game['inning'])}")
                        with c3:
                            st.metric(label="Outs", value="🔴" * int(game['outs']) if int(game['outs']) > 0 else "0 Outs")
                        with c4:
                            # Base paths Matrix Visualizer
                            b1 = "❶" if int(game['runner_1b']) == 1 else "○"
                            b2 = "❷" if int(game['runner_2b']) == 1 else "○"
                            b3 = "❸" if int(game['runner_3b']) == 1 else "○"
                            st.metric(label="Base Paths Matrix", value=f"{b3}   {b2}   {b1}")
                            
                        st.markdown(" ")
                        
                        # 2. Live Personnel Matchup & Ratings Row
                        col_p1, col_p2, col_p3 = st.columns(3)
                        with col_p1:
                            st.markdown(f"**⚾ Active Pitcher:** {game['pitcher_name']}")
                            st.caption(f"FanGraphs Strikeout Factor: `{game['pitcher_rating']}`")
                        with col_p2:
                            st.markdown(f"**⚔️ At-Bat Franchise:** {game['batting_team']}")
                            st.caption(f"Team Recent Offense Form Tracker: `{game['batter_rating']}`")
                        with col_p3:
                            # Clear predictive target metric outputs
                            st.progress(home_p, text=f"**Home Team Win Equity: {home_p*100:.1f}%**")
                        
                        st.markdown("---")
            else:
                st.info("📡 Command center online. Waiting for game-state changes to populate stream...")
                
    except Exception as e:
        # Crucial fix: Keeps the error handling neatly locked inside the placeholder box
        with dashboard_placeholder.container():
            st.warning(f"📡 Syncing columns with your active Colab stream... Error info: {e}")
        
    time.sleep(15)
