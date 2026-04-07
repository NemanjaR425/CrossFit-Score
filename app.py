import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="HN CrossFit Live", layout="centered")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOAD ATHLETES ---
try:
    athlete_df = conn.read(worksheet="Athletes")
    athlete_list = [f"{row['Athlete_ID']} - {row['Name']}" for index, row in athlete_df.iterrows()]
except:
    athlete_list = ["No athletes found - Check your 'Athletes' tab"]

st.title("🏆 Judge Score Entry")

# --- JUDGE INPUT FORM ---
with st.form("score_entry_form", clear_on_submit=True):
    selected_athlete = st.selectbox("Select Athlete", athlete_list)
    workout = st.selectbox("Select Workout", ["WOD 1", "WOD 2", "WOD 3"])
    score = st.number_input("Result (Reps or Seconds)", min_value=0, step=1)
    password = st.text_input("Staff Password", type="password")
    submit_button = st.form_submit_button("SAVE SCORE")

if submit_button:
    if password == "HN2026":
        try:
            a_id = selected_athlete.split(" - ")[0]
            a_name = selected_athlete.split(" - ")[1]
            
            new_entry = pd.DataFrame([{
                "Athlete_ID": str(a_id),
                "Name": str(a_name),
                "Workout": str(workout),
                "Score": int(score),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            existing_scores = conn.read(worksheet="Scores", ttl=0)
            updated_scores = pd.concat([existing_scores, new_entry], ignore_index=True)
            conn.update(worksheet="Scores", data=updated_scores)
            
            st.success(f"Score for {a_name} saved!")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Wrong Password")

# --- THE DYNAMIC LEADERBOARD ---
st.write("---")
st.subheader("📊 Live Leaderboard")

# Let the user choose how to sort the big screen
sort_type = st.radio("Scoring Type:", ["Highest Score Wins (Reps/KG)", "Lowest Score Wins (Time)"], horizontal=True)

try:
    # Pull fresh data
    live_data = conn.read(worksheet="Scores", ttl=0)
    
    if not live_data.empty:
        # Filter by workout if you want to see specific WOD standings
        selected_wod = st.selectbox("Filter by Workout:", ["All Workouts"] + list(live_data['Workout'].unique()))
        
        display_df = live_data.copy()
        if selected_wod != "All Workouts":
            display_df = display_df[display_df['Workout'] == selected_wod]

        # Apply Sorting Logic
        if sort_type == "Highest Score Wins (Reps/KG)":
            sorted_df = display_df.sort_values(by="Score", ascending=False)
        else:
            sorted_df = display_df.sort_values(by="Score", ascending=True)

        # Show the board
        st.table(sorted_df[["Athlete_ID", "Name", "Workout", "Score"]])
    else:
        st.info("No scores recorded yet.")
except:
    st.info("Waiting for data...")
