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
except Exception as e:
    athlete_list = ["No athletes found - Check your 'Athletes' tab"]

st.title("🏆 Judge Score Entry")

with st.form("score_entry_form", clear_on_submit=True):
    selected_athlete = st.selectbox("Select Athlete", athlete_list)
    workout = st.selectbox("Select Workout", ["WOD 1", "WOD 2", "WOD 3"])
    score = st.number_input("Result", min_value=0, step=1)
    password = st.text_input("Staff Password", type="password")
    submit_button = st.form_submit_button("SAVE SCORE")

if submit_button:
    if password == "HN2026":
        try:
            # 1. Prepare New Data
            a_id = selected_athlete.split(" - ")[0]
            a_name = selected_athlete.split(" - ")[1]
            
            new_entry = pd.DataFrame([{
                "Athlete_ID": str(a_id),
                "Name": str(a_name),
                "Workout": str(workout),
                "Score": int(score),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # 2. Read Existing Scores with Safety Check
            try:
                existing_scores = conn.read(worksheet="Scores")
                # If existing_scores is empty or not a dataframe, create a clean one
                if existing_scores is None or existing_scores.empty:
                    updated_scores = new_entry
                else:
                    # GLUE THEM TOGETHER (This keeps the history)
                    updated_scores = pd.concat([existing_scores, new_entry], ignore_index=True)
            except:
                # If the 'Scores' tab is totally blank, just use the new entry
                updated_scores = new_entry
            
            # 3. Clear the old data and upload the NEW FULL LIST
            conn.update(worksheet="Scores", data=updated_scores)
            
            st.success(f"Score for {a_name} added to the list!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Wrong Password")

# --- THE LIVE BOARD ---
st.write("---")
st.subheader("📊 All Recorded Scores")
try:
    # Always pull the freshest data from the sheet
    live_data = conn.read(worksheet="Scores", ttl=0) # ttl=0 means 'don't use cache, show me live'
    if not live_data.empty:
        # Show newest scores at the top
        st.dataframe(live_data.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    else:
        st.info("No scores recorded yet.")
except:
    st.info("Waiting for data...")
