import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="MLB Deep Command Center", layout="wide", page_icon="⚾")
st.title("⚡ Live Situational Command Center")

# Connection Setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_UNIQUE_ID/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

dashboard_placeholder = st.empty()

while True:
    try:
        live_data = conn.read(spreadsheet=SHEET_URL, ttl=0).dropna(how="all")
        
        with dashboard_placeholder.container():
            if not live_data.empty:
                for index, game in live_data.iterrows():
                    match_title = f"🏟️ {game['away_team']} @ {game['home_team']}"
                    home_p = float(game['home_win_prob'])
                    
                    with st.expander(f"{match_title}  |  📊 Live Probability: Home {home_p*100:.1f}%", expanded=True):
                        # 1. Main Scoreboard row
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric(label="Current Score", value=f"{game['away_team']} {int(game['away_score'])} - {int(game['home_score'])} {game['home_team']}")
                        with c2:
                            st.metric(label="Game Frame", value=f"{game['half_inning']} of {int(game['inning'])}")
                        with c3:
                            st.metric(label="Outs", value="🔴" * int(game['outs']) if int(game['outs']) > 0 else "0 Outs")
                        with c4:
                            st.metric(label="Count", value=f"🟢 {int(game['balls'])} Balls  |  ❌ {int(game['strikes'])} Strikes")
                            
                        st.markdown(" ")
                        
                        # 2. Live Narrative Box (Play-by-Play Description)
                        st.info(f"📋 **Latest Event:** {game['last_play_desc']}")
                        
                        # 3. Deep Personnel Breakdown Row
                        col_p1, col_p2, col_p3 = st.columns(3)
                        with col_p1:
                            st.markdown(f"**⚾ Pitcher Matchup:** {game['pitcher_name']}")
                            st.caption(f"Rating Baseline Factor: `{game['pitcher_rating']}`")
                            st.markdown(f"**⚔️ Current Batter:** {game['batter_name']}")
                            st.caption(f"Franchise Offense Form: `{game['batter_rating']}`")
                        with col_p2:
                            st.markdown("**🏃 Active Base Runners:**")
                            st.write(f"🔹 **1B:** {game['runner_1b_name']}")
                            st.write(f"🔹 **2B:** {game['runner_2b_name']}")
                            st.write(f"🔹 **3B:** {game['runner_3b_name']}")
                        with col_p3:
                            st.progress(home_p, text=f"**Home Team Win Equity: {home_p*100:.1f}%**")
                        
                        st.markdown("---")
            else:
                st.info("📡 Command center online. Waiting for game-state changes to populate stream...")
                
    except Exception as e:
        with dashboard_placeholder.container():
            st.warning(f"📡 Syncing deep personnel columns with active stream... Error: {e}")
        
    time.sleep(12)
