
import streamlit as st
import pandas as pd
from itertools import combinations
import random

def generate_seating(people, table_sizes, workplaces, previous_pairings):
    coworkers = {}
    for workplace in set(workplaces.values()):
        if workplace != "None":
            coworkers[workplace] = {name for name, wp in workplaces.items() if wp == workplace}

    max_attempts = 1000  # Prevent infinite loops
    attempts = 0
    while attempts < max_attempts:
        random.shuffle(people)
        seating = []
        idx = 0
        valid = True
        for size in table_sizes:
            table = people[idx:idx + size]
            idx += size

            # Check coworker constraint
            table_workplaces = [workplaces[person] for person in table]
            if len(set(table_workplaces)) < len(table):
                valid = False
                break

            seating.append(table)

        if not valid:
            attempts += 1
            continue

        # Check for unique pairings
        current_pairings = set()
        for table in seating:
            current_pairings.update(combinations(table, 2))

        if current_pairings.isdisjoint(previous_pairings):
            previous_pairings.update(current_pairings)
            return seating

        attempts += 1

    raise Exception("Unable to generate seating arrangement without repeating pairings.")

def generate_arrangements(people, table_sizes, num_days, workplaces):
    previous_pairings = set()
    daily_arrangements = []
    for day in range(num_days):
        seating = generate_seating(people, table_sizes, workplaces, previous_pairings)
        daily_arrangements.append(seating)
    return daily_arrangements

st.title("Seating Chart Generator")

uploaded_file = st.file_uploader("Upload a CSV file with 'Name' and 'Workplace' columns", type="csv")

if uploaded_file is not None:
    students_df = pd.read_csv(uploaded_file)
    students = list(students_df["Name"])
    workplaces = dict(zip(students_df["Name"], students_df["Workplace"]))

    num_days = st.number_input("Enter number of days", min_value=1, max_value=10, value=5)
    table_sizes_input = st.text_input(
        "Enter table sizes separated by commas (e.g., 4,4,4,4,4,4,4,4,3,3)", "4,4,4,4,4,4,4,4,3,3"
    )
    table_sizes = [int(size.strip()) for size in table_sizes_input.split(",")]

    if st.button("Generate Seating Chart"):
        try:
            seating_arrangements = generate_arrangements(students, table_sizes, num_days, workplaces)
            st.success("Seating chart generated successfully!")
            
            for day_num, day in enumerate(seating_arrangements, 1):
                st.write(f"### Day {day_num}")
                for table_num, table in enumerate(day, 1):
                    st.write(f"**Table {table_num}:** {', '.join(table)}")
            
            seating_data = {}
            for day_num, day in enumerate(seating_arrangements, 1):
                for table_num, table in enumerate(day, 1):
                    seating_data.setdefault(f"Table {table_num}", {})[f"Day {day_num}"] = ", ".join(table)

            seating_df = pd.DataFrame(seating_data)
            seating_csv = seating_df.to_csv(index=False)
            st.download_button("Download Seating Chart as CSV", seating_csv, "seating_chart.csv", "text/csv")
        
        except Exception as e:
            st.error(str(e))
