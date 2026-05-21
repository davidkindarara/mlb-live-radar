!pip install streamlit st-gsheets-connection
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import time

# 1. Page Configuration
st.set_page_config(page_title="MLB Live Radar", layout="wide", page_icon="⚾")
st.title("🔥 Live Betting Radar")

# 2. Connection Setup
# Paste your exact Google Sheets share link right here:
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g8Y8iPLCw2NZDH9t27bbFAYDvnlCL7RlbNqIDa1RV9o/edit?usp=sharing"

# Establish the connection using Streamlit's built-in tool
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Create the UI Placeholder
dashboard_placeholder = st.empty()

# 4. The Live Dashboard Loop
while True:
    try:
        # Read the data from the sheet.
        # ttl=0 is CRITICAL: It tells Streamlit to never cache the data, always fetch the live numbers.
        live_data = conn.read(spreadsheet=SHEET_URL, ttl=0)

        # Clean up any blank rows Google Sheets might have added
        live_data = live_data.dropna(how="all")

        if not live_data.empty:
            # Render the UI inside the placeholder
            with dashboard_placeholder.container():
                st.subheader("🚨 Latest Live Edge Detected")

                # Display metrics cleanly across the top
                col1, col2, col3 = st.columns(3)

                with col1:
                    matchup = f"{live_data['away_team'].iloc[0]} @ {live_data['home_team'].iloc[0]}"
                    st.metric(label="Matchup", value=matchup)

                with col2:
                    home_prob = float(live_data['level3_home_win_prob'].iloc[0])
                    st.metric(label="Home Win Prob", value=f"{home_prob * 100:.1f}%")

                with col3:
                    away_prob = float(live_data['level3_away_win_prob'].iloc[0])
                    st.metric(label="Away Win Prob", value=f"{away_prob * 100:.1f}%")

                st.markdown("---")

                # Show the raw dataframe
                st.dataframe(live_data, use_container_width=True, hide_index=True)

        else:
            with dashboard_placeholder.container():
                st.info("📡 Radar is online and scanning. Waiting for the first pitching change...")

    except Exception as e:
        with dashboard_placeholder.container():
            st.warning("⚠️ Waiting for data to populate from the Colab engine...")

    # Sleep for 30 seconds to match your Colab engine's cycle
    time.sleep(30)
