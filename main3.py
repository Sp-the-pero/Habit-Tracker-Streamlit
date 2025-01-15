# Version 3 || Improving  one by one 

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta
import os

# File to store habit data
DATA_FILE = "habits.csv"

# Load data from file
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Habit", "Date", "Status"])

# Save data to file
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Initialize data
if "data" not in st.session_state:
    st.session_state["data"] = load_data()

if "goals" not in st.session_state:
    st.session_state["goals"] = {}  # Stores multiple goals for each habit

st.title("Habit Tracker")

# Function to add a habit
def add_habit():
    st.session_state["data"] = pd.concat(
        [
            st.session_state["data"],
            pd.DataFrame({"Habit": [habit_name], "Date": [start_date], "Status": ["Pending"]}),
        ],
        ignore_index=True,
    )
    st.session_state["goals"][habit_name] = goals
    save_data(st.session_state["data"])  # Save changes to file
    st.success(f"Habit '{habit_name}' added with goals: {goals}!")

# Sidebar: Add habits and goals
st.sidebar.header("Add a New Habit")
habit_name = st.sidebar.text_input("Habit Name")
start_date = st.sidebar.date_input("Start Date", date.today())
goals_input = st.sidebar.text_input("Goals (comma-separated, e.g., 7, 14, 21 days)")
if st.sidebar.button("Add Habit"):
    if habit_name and start_date and goals_input:
        goals = [int(g.strip()) for g in goals_input.split(",") if g.strip().isdigit()]
        if goals:
            add_habit()
        else:
            st.sidebar.error("Please provide valid goals as numbers!")
    else:
        st.sidebar.error("Please fill in all fields!")

# Display current habits
st.header("Your Habits")
habits = st.session_state["data"]["Habit"].unique()
if len(habits) > 0:
    selected_habit = st.selectbox("Select a Habit", habits)
    habit_data = st.session_state["data"][st.session_state["data"]["Habit"] == selected_habit]
    st.dataframe(habit_data)

    # Update habit status
    st.subheader("Update Status")
    update_date = st.date_input("Date to Update", date.today())
    status = st.radio("Status", ["Done", "Missed", "Pending"])
    if st.button("Update Habit Status"):
        if not habit_data[habit_data["Date"] == update_date].empty:
            st.session_state["data"].loc[
                (st.session_state["data"]["Habit"] == selected_habit) &
                (st.session_state["data"]["Date"] == update_date), "Status"
            ] = status
        else:
            st.session_state["data"] = pd.concat(
                [
                    st.session_state["data"],
                    pd.DataFrame({"Habit": [selected_habit], "Date": [update_date], "Status": [status]}),
                ],
                ignore_index=True,
            )
        save_data(st.session_state["data"])  # Save changes to file
        st.success("Status updated!")

    # Progress visualization
    st.subheader("Progress")
    habit_data["Date"] = pd.to_datetime(habit_data["Date"])
    habit_data = habit_data.sort_values(by="Date")
    habit_data["Completion"] = habit_data["Status"].apply(lambda x: 1 if x == "Done" else 0)
    
    fig, ax = plt.subplots()
    ax.plot(habit_data["Date"], habit_data["Completion"], marker="o", label="Completion")
    ax.set_title(f"Daily Progress for {selected_habit}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Completion (1=Done, 0=Not Done)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # Display goals and completion
    goals = st.session_state["goals"].get(selected_habit, [])
    days_completed = habit_data[habit_data["Completion"] == 1].shape[0]
    st.write(f"Days Completed: {days_completed}")
    st.write(f"Goals: {goals}")

    if goals:
        for goal in goals:
            if days_completed >= goal:
                st.success(f"🎉 Goal of {goal} days achieved!")
            else:
                st.info(f"📈 Next Goal: {goal} days")

    # Extend or end habit tracking
    if st.button("Extend Goals"):
        new_goals = st.text_input("New Goals (comma-separated)", key="extend_goals")
        if new_goals:
            new_goals_list = [int(g.strip()) for g in new_goals.split(",") if g.strip().isdigit()]
            st.session_state["goals"][selected_habit].extend(new_goals_list)
            st.success("Goals extended!")
    if st.button("End Habit"):
        st.session_state["data"] = st.session_state["data"][st.session_state["data"]["Habit"] != selected_habit]
        del st.session_state["goals"][selected_habit]
        save_data(st.session_state["data"])  # Save changes to file
        st.success(f"Habit '{selected_habit}' ended!")
else:
    st.info("No habits found. Add a new habit to start tracking!")

# View all habits and data
if st.checkbox("Show All Habits Data"):
    st.dataframe(st.session_state["data"])
