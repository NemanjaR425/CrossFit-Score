import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="HN CrossFit Live", layout="centered")

# 1. Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Load Athlete List from the 'Athletes' tab
try:
    # We pull the names you entered in the Google Sheet
    athlete_df = conn.read(worksheet="Athletes")
    # Create a list like "1 - Nemanja Ristic" for the dropdown
    athlete_list = [f"{row['Athlete_ID']} - {row['Name']}" for index, row in athlete_df.iterrows()]
except:
    athlete_list = ["No athletes found - Check your 'Athletes' tab"]

st.title("🏆 Judge Score Entry")

# 3. The Entry Form
with st.form("score_entry_form", clear_on_submit=True):
    
    # Judge selects athlete from the list you pre-loaded
    selected_athlete = st.selectbox("Select Athlete", athlete_list)
    
    # Workout Selection (You can edit this list here)
    workout = st.selectbox("Select Workout", ["WOD 1: Max Clean", "WOD 2: AMRAP 12", "WOD 3: Final"])
    
    score = st.number_input("Result (Reps or Total Seconds)", min_value=0, step=1)
    
    password = st.text_input("Staff Password", type="password")
    
    submit_button = st.form_submit_button("SAVE SCORE")

# 4. Logic to Append (Not Overwrite)
if submit_button:
    if password == "HN2026":
        try:
            # Split the "1 - Nemanja Ristic" string back into ID and Name
            a_id = selected_athlete.split(" - ")[0]
            a_name = selected_athlete.split(" - ")[1]
            
            new_entry = pd.DataFrame([{
                "Athlete_ID": a_id,
                "Name": a_name,
                "Workout": workout,
                "Score": int(score),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # CRITICAL: We read the 'Scores' tab specifically
            existing_scores = conn.read(worksheet="Scores")
            
            # Add the new score to the list of old scores
            updated_scores = pd.concat([existing_scores, new_entry], ignore_index=True)
            
            # Save it back to the 'Scores' tab
            conn.update(worksheet="Scores", data=updated_scores)
            
            st.success(f"Score for {a_name} saved!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Wrong Password")

# 5. Live Scoreboard (The "Big Screen" view)
st.write("---")
st.subheader("📊 Current Scores")
try:
    # This pulls all scores so you can see the history
    live_data = conn.read(worksheet="Scores")
    if not live_data.empty:
        st.dataframe(live_data.sort_values(by="Timestamp", ascending=False))
    else:
        st.write("Waiting for first score...")
except:
    st.write("Ready for competition.")
