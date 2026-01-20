import streamlit as st
import math

st.set_page_config(page_title="Knockout Fixtures", layout="centered")
st.title("🏏 Leaderboard Knockout Fixture Generator (Sorted by Time)")

st.write("Enter teams and their times in seconds, one per line, in the format: `TEAM 1 , 20s`")

team_text = st.text_area(
    "Enter Teams & Times",
    height=400,
    placeholder="TEAM 1 , 20s\nTEAM 2 , 10s\nTEAM 3 , 25s\n..."
)

def next_power_of_two(n):
    """Return the next power of two >= n"""
    return 1 << (n - 1).bit_length()

def parse_teams_with_time(team_lines):
    teams = []
    for line in team_lines:
        line = line.strip()
        if not line:
            continue
        if ',' in line:
            name, time = line.split(',', 1)
            name = name.strip()
            time = time.strip().rstrip('s')
            try:
                time = int(time)
                teams.append((name, time))
            except ValueError:
                st.warning(f"Invalid time for team: {name}")
        else:
            st.warning(f"Invalid format: {line}")
    return teams

def generate_knockout(teams_with_time):
    # Sort teams by time ascending (fastest first)
    teams_with_time.sort(key=lambda x: x[1])
    teams = [t[0] for t in teams_with_time]

    total_teams = len(teams)
    next_power2 = next_power_of_two(total_teams)
    total_byes = next_power2 - total_teams

    st.subheader("🏁 Round 1")
    round_teams = []
    match_no = 1
    i = 0

    # Assign BYEs to top teams first
    while i < total_teams:
        if total_byes > 0:
            st.write(f"{teams[i]} gets BYE")
            round_teams.append(teams[i])
            total_byes -= 1
            i += 1
        else:
            if i + 1 < total_teams:
                st.write(f"Match {match_no}: {teams[i]} vs {teams[i+1]}")
                round_teams.append(f"Winner of Match {match_no}")
                match_no += 1
                i += 2
            else:
                st.write(f"{teams[i]} gets BYE")
                round_teams.append(teams[i])
                i += 1

    teams = round_teams
    round_no = 2

    # Next rounds
    while len(teams) > 1:
        if len(teams) == 2:
            round_name = "FINAL"
        elif len(teams) == 4:
            round_name = "SEMIFINAL"
        elif len(teams) == 8:
            round_name = "QUARTERFINAL"
        else:
            round_name = f"ROUND {round_no}"

        st.subheader(round_name)
        next_round = []
        i = 0

        while i < len(teams):
            if i + 1 < len(teams):
                st.write(f"Match {match_no}: {teams[i]} vs {teams[i+1]}")
                next_round.append(f"Winner of Match {match_no}")
                match_no += 1
                i += 2
            else:
                st.write(f"{teams[i]} gets BYE")
                next_round.append(teams[i])
                i += 1

        teams = next_round
        round_no += 1

    st.success(f"🏆 Champion: {teams[0]}")

if st.button("Generate Fixtures"):
    team_lines = team_text.split("\n")
    teams_with_time = parse_teams_with_time(team_lines)
    if len(teams_with_time) < 2:
        st.error("Enter at least 2 teams with valid times")
    else:
        generate_knockout(teams_with_time)
        st.info("👉 Use browser Print (Ctrl + P) to Print or Save as PDF")
