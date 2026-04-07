import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Page config for a clean mobile look
st.set_page_config(page_title="HN CrossFit Live", layout="centered")

# Custom CSS to make the SAVE button big and green
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 4em;
        width: 100%;
        background-color: #28a745;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOAD ATHLETES ---
try:
    athlete_df = conn.read(worksheet="Athletes", ttl=3600) # Cache names for 1 hour to stay fast
    athlete_list = [f"{row['Athlete_ID']} - {row['Name']}" for index, row in athlete_df.iterrows()]
except:
    athlete_list = ["No athletes found - Check your 'Athletes' tab"]

st.title("⏱️ Judge Entry")

# --- FAST INPUT FORM ---
with st.form("score_entry_form", clear_on_submit=True):
    
    selected_athlete = st.selectbox("Who is competing?", athlete_list)
    
    workout = st.selectbox("Which Workout?", ["WOD 1", "WOD 2", "WOD 3"])
    
    score = st.number_input("Result (Reps or Seconds)", min_value=0, step=1, value=0)
    
    is_time_based = st.toggle("Is this a TIME workout? (Lowest wins)", value=False)
    
    st.write("---")
    
    # Big, easy-to-hit button
    submit_button = st.form_submit_button("🚀 SAVE SCORE")

if submit_button:
    try:
        # Prepare Data
        a_id = selected_athlete.split(" - ")[0]
        a_name = selected_athlete.split(" - ")[1]
        
        new_entry = pd.DataFrame([{
            "Athlete_ID": str(a_id),
            "Name": str(a_name),
            "Workout": str(workout),
            "Score": int(score),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        
        # Read, Append, Sort, and Save
        existing_scores = conn.read(worksheet="Scores", ttl=0)
        all_scores = pd.concat([existing_scores, new_entry], ignore_index=True)
        
        # Sorting logic: Group by WOD, then by Score
        if is_time_based:
            sorted_all = all_scores.sort_values(by=["Workout", "Score"], ascending=[True, True])
        else:
            sorted_all = all_scores.sort_values(by=["Workout", "Score"], ascending=[True, False])
        
        conn.update(worksheet="Scores", data=sorted_all)
        
        st.success(f"SAVED: {a_name} | {score}")
        st.balloons()
        
    except Exception as e:
        st.error(f"Error: {e}")

# --- THE LEADERBOARD ---
st.write("---")
st.subheader("📊 Live Leaderboard")
try:
    live_data = conn.read(worksheet="Scores", ttl=0)
    if not live_data.empty:
        # We only show the essential columns for the leaderboard
        st.table(live_data[["Name", "Workout", "Score"]])
    else:
        st.info("Waiting for the first score...")
except:
    st.info("Connecting to sheet...")
