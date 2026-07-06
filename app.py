import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

st.set_page_config(page_title="MLB Deep Command Center", layout="wide", page_icon="⚾")
st.title("⚡ Live Situational Command Center")

# ==========================================================
# MODULE: LIVE IN-GAME SITUATIONAL SCORE PREDICTOR
# ==========================================================
class MLBScorePredictor:
    def __init__(self):
        # Baseline probability of scoring >= 1 run in this situation (RE24 Baseline Context)
        # State key format: (outs, base_configuration_string)
        self.base_situation_matrix = {
            (0, '000'): 0.28, (1, '000'): 0.16, (2, '000'): 0.07,
            (0, '100'): 0.44, (1, '100'): 0.29, (2, '100'): 0.13,
            (0, '010'): 0.61, (1, '010'): 0.39, (2, '010'): 0.21,
            (0, '001'): 0.85, (1, '001'): 0.52, (2, '001'): 0.22,
            (0, '110'): 0.62, (1, '110'): 0.41, (2, '110'): 0.22,
            (0, '101'): 0.85, (1, '101'): 0.63, (2, '101'): 0.25,
            (0, '011'): 0.84, (1, '011'): 0.57, (2, '011'): 0.22,
            (0, '111'): 0.84, (1, '111'): 0.64, (2, '111'): 0.32, # Bases Loaded, 2 Outs = 32%
        }

    def predict_scoring_likelihood(self, outs, bases, pitcher_live_bb_rate, batter_wrc_plus):
        base_prob = self.base_situation_matrix.get((outs, bases), 0.15)
        # MLB average walk rate is ~8.5% (0.085). Scale up if pitcher is giving up lots of walks
        pitcher_multiplier = 1.0 + (max(0, pitcher_live_bb_rate - 0.085) * 2.5)
        # Batter wRC+ baseline is 100
        batter_multiplier = batter_wrc_plus / 100.0
        
        live_scoring_prob = base_prob * pitcher_multiplier * batter_multiplier
        return min(max(live_scoring_prob, 0.01), 0.99)

# Initialize the engine once
predictor = MLBScorePredictor()

# Connection Setup
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g8Y8iPLCw2NZDH9t27bbFAYDvnlCL7RlbNqIDa1RV9o/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

dashboard_placeholder = st.empty()

while True:
    try:
        live_data = conn.read(spreadsheet=SHEET_URL, ttl=0).dropna(how="all")
        
        with dashboard_placeholder.container():
            # Check if data exists AND contains our deep situational columns
            required_columns = ['balls', 'strikes', 'last_play_desc', 'pitcher_name', 'home_win_prob']
            has_all_columns = all(col in live_data.columns for col in required_columns) if not live_data.empty else False
            
            if not live_data.empty and has_all_columns:
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
                        
                        # --------------------------------------------------------
                        # LIVE PREDICTION CALCULATION
                        # --------------------------------------------------------
                        # Build the base configuration string ('000', '100', '111', etc.) dynamically
                        b1 = '1' if str(game.get('runner_1b_name', '')).strip() and str(game.get('runner_1b_name', '')) != 'None' else '0'
                        b2 = '1' if str(game.get('runner_2b_name', '')).strip() and str(game.get('runner_2b_name', '')) != 'None' else '0'
                        b3 = '1' if str(game.get('runner_3b_name', '')).strip() and str(game.get('runner_3b_name', '')) != 'None' else '0'
                        base_config_str = f"{b1}{b2}{b3}"
                        
                        # Fetch values or fall back to baseline defaults if columns aren't appended yet
                        pitcher_live_walks = float(game.get('pitcher_live_bb_rate', 0.095)) 
                        batter_wrc_stat = float(game.get('batter_rating', 100)) # Using batter_rating as form factor
                        
                        scoring_chance = predictor.predict_scoring_likelihood(
                            outs=int(game['outs']),
                            bases=base_config_str,
                            pitcher_live_bb_rate=pitcher_live_walks,
                            batter_wrc_plus=batter_wrc_stat
                        )
                        # --------------------------------------------------------
                        
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
                            
                            # Embed the Score Prediction metrics right underneath the progress bar
                            st.markdown(" ")
                            st.metric(
                                label="🎯 Prob. of Scoring (This Inning)", 
                                value=f"{scoring_chance * 100:.1f}%",
                                delta="⚠️ HIGH RISK" if scoring_chance > 0.45 else "🟢 STABLE"
                            )
                        
                        st.markdown("---")
            else:
                st.info("📡 Command center online. Waiting for game-state change frames from Colab to sync...")
                
    except Exception as e:
        with dashboard_placeholder.container():
            st.warning(f"📡 Syncing deep personnel columns with active stream... Status info: {e}")
        
    time.sleep(12)
