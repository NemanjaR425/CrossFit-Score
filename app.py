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
    
    # ADDED: Tell the app how to sort THIS specific WOD
    is_time_based = st.checkbox("Is this a TIME workout? (Lowest score wins)")
    
    password = st.text_input("Staff Password", type="password")
    submit_button = st.form_submit_button("SAVE & SORT LEADERBOARD")

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
            
            # 1. Pull the current sheet
            existing_scores = conn.read(worksheet="Scores", ttl=0)
            
            # 2. Combine with new score
            all_scores = pd.concat([existing_scores, new_entry], ignore_index=True)
            
            # 3. SORT THE DATA BEFORE SENDING TO GOOGLE
            # If it's time-based, 10 is better than 20 (Ascending). 
            # If it's reps, 20 is better than 10 (Descending).
            if is_time_based:
                sorted_all = all_scores.sort_values(by=["Workout", "Score"], ascending=[True, True])
            else:
                sorted_all = all_scores.sort_values(by=["Workout", "Score"], ascending=[True, False])
            
            # 4. OVERWRITE THE SHEET WITH THE SORTED LIST
            conn.update(worksheet="Scores", data=sorted_all)
            
            st.success(f"Score for {a_name} saved and Sheet re-sorted!")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Wrong Password")

# --- THE BIG SCREEN DISPLAY ---
st.write("---")
st.subheader("📊 Live Sorted Leaderboard")
try:
    live_data = conn.read(worksheet="Scores", ttl=0)
    if not live_data.empty:
        st.table(live_data[["Athlete_ID", "Name", "Workout", "Score"]])
    else:
        st.info("No scores yet.")
except:
    st.info("Waiting for data...")
