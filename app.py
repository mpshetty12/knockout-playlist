import streamlit as st
import math
import re

st.set_page_config(page_title="Knockout Fixtures", layout="centered")
st.title("🏏 Leaderboard Knockout Fixture Generator (Sorted by Time)")

st.write("Enter teams and their times in seconds, one per line, in the format: `TEAM NAME , 20s` or `TEAM NAME , 12.56s`")

team_text = st.text_area(
    "Enter Teams & Times",
    height=350,
    placeholder="TEAM A , 20s\nTEAM B , 10.55s\nTEAM C , 25s\n..."
)

# ------------------ UTIL FUNCTIONS ------------------

def next_power_of_two(n):
    return 1 << (n - 1).bit_length()

def parse_teams_with_time(team_lines):
    teams = []
    for line in team_lines:
        line = line.strip()
        if not line:
            continue

        if ',' not in line:
            st.warning(f"Invalid format: {line}")
            continue

        name, time_part = line.split(',', 1)
        name = name.strip()

        # extract number from time (supports decimals)
        match = re.search(r"(\d+(\.\d+)?)", time_part)
        if not match:
            st.warning(f"Invalid time for team: {name}")
            continue

        time = float(match.group(1))
        teams.append((name, time))

    return teams

# ------------------ FIXTURE GENERATOR ------------------

def generate_knockout(teams_with_time):
    # Sort by fastest time
    teams_with_time.sort(key=lambda x: x[1])

    # ---------- SHOW SORTED LIST ----------
    sorted_text = "\n".join(
        [f"{i+1}. {name} , {time}s" for i, (name, time) in enumerate(teams_with_time)]
    )

    st.subheader("✅ Sorted Teams (Fastest First)")

    line_count = len(teams_with_time)
    auto_height = min(1200, line_count * 28 + 60)

    st.text_area(
        "You can copy this sorted list",
        value=sorted_text,
        height=auto_height,
        disabled=True
    )

    teams = [t[0] for t in teams_with_time]

    total_teams = len(teams)
    next_power2 = next_power_of_two(total_teams)
    total_byes = next_power2 - total_teams

    st.subheader("🏁 Round 1")

    round_teams = []
    match_no = 1

    # -------- GROUP BYES --------
    bye_teams = teams[:total_byes]
    play_teams = teams[total_byes:]

    if total_byes > 0:
        bye_list = ", ".join(bye_teams)
        st.success(f"✅ Top {total_byes} teams directly qualified to Round 2:\n{bye_list}")

    round_teams.extend(bye_teams)

    # -------- MATCHES --------
    i = 0
    while i < len(play_teams):
        if i + 1 < len(play_teams):
            st.write(f"Match {match_no}: {play_teams[i]} vs {play_teams[i+1]}")
            round_teams.append(f"Winner of Match {match_no}")
            match_no += 1
            i += 2
        else:
            round_teams.append(play_teams[i])
            i += 1

    teams = round_teams
    round_no = 2

    # -------- NEXT ROUNDS --------
    while len(teams) > 1:
        if len(teams) == 2:
            round_name = "🏆 FINAL"
        elif len(teams) == 4:
            round_name = "🔥 SEMIFINAL"
        elif len(teams) == 8:
            round_name = "⚡ QUARTERFINAL"
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
                next_round.append(teams[i])
                i += 1

        teams = next_round
        round_no += 1

    st.success(f"🏆 Champion: {teams[0]}")

# ------------------ MAIN ------------------

if st.button("Generate Fixtures"):
    team_lines = team_text.split("\n")
    teams_with_time = parse_teams_with_time(team_lines)

    if len(teams_with_time) < 2:
        st.error("Enter at least 2 teams with valid times")
    else:
        generate_knockout(teams_with_time)
        st.info("👉 Use browser Print (Ctrl + P) to Print or Save as PDF")
