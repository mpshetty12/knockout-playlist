import streamlit as st
import re

st.set_page_config(page_title="Knockout Fixtures", layout="centered")
st.title("🏏 Leaderboard Knockout Fixture Generator (Sorted by Time)")

st.write(
    "Enter teams and their times in seconds, one per line.\n\n"
    "Examples:\n"
    "TEAM A , 12s\n"
    "ತಂಡ ಉಡುಪಿ , 10.567s\n"
    "TEAM C , 15.2\n"
)

team_text = st.text_area(
    "Enter Teams & Times",
    height=350,
    placeholder="TEAM 1 , 20s\nTEAM 2 , 10.56s\nTEAM 3 , 25\n..."
)

# ------------------ UTIL FUNCTIONS ------------------

def next_power_of_two(n):
    return 1 << (n - 1).bit_length()

def parse_teams_with_time(team_lines):
    teams = []

    for line in team_lines:
        line = line.replace("\u200b", "").replace("\ufeff", "").strip()

        if not line:
            continue

        if "," not in line:
            st.warning(f"Invalid format: {line}")
            continue

        name, time_part = line.split(",", 1)
        name = name.strip()

        match = re.search(r"(\d+(\.\d+)?)", time_part)

        if not match:
            st.warning(f"Invalid time for team: {name}")
            continue

        try:
            time_val = float(match.group(1))
            teams.append((name, time_val))
        except:
            st.warning(f"Invalid time for team: {name}")

    return teams

# ------------------ FIXTURE GENERATION ------------------

def generate_knockout(teams_with_time):

    # sort by time
    teams_with_time.sort(key=lambda x: x[1])

    # ---------- SHOW SORTED TEAMS IN TEXT BOX ----------
    sorted_text = "\n".join([f"{name} , {time:.5f}s" for name, time in teams_with_time])

    st.subheader("✅ Sorted Teams (Fastest First)")

    line_count = len(teams_with_time)
    auto_height = min(800, line_count * 28 + 50)  # adjust max if needed

    st.text_area(
        "You can copy or verify this list",
        value=sorted_text,
        height=auto_height,
        disabled=True
    )

    st.divider()

    # ---------- FIXTURES ----------
    teams = [t[0] for t in teams_with_time]

    total_teams = len(teams)
    next_power2 = next_power_of_two(total_teams)
    total_byes = next_power2 - total_teams

    st.subheader("🏁 ROUND 1")
    round_teams = []
    match_no = 1
    i = 0

    while i < total_teams:
        if total_byes > 0:
            st.write(f"{teams[i]} ➜ BYE")
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
                st.write(f"{teams[i]} ➜ BYE")
                round_teams.append(teams[i])
                i += 1

    teams = round_teams
    round_no = 2

    while len(teams) > 1:

        if len(teams) == 2:
            round_name = "🏆 FINAL"
        elif len(teams) == 4:
            round_name = "🥉 SEMI FINAL"
        elif len(teams) == 8:
            round_name = "🏏 QUARTER FINAL"
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
                st.write(f"{teams[i]} ➜ BYE")
                next_round.append(teams[i])
                i += 1

        teams = next_round
        round_no += 1

    st.success(f"🏆 CHAMPION: {teams[0]}")

# ------------------ MAIN BUTTON ------------------

if st.button("Generate Fixtures"):
    team_lines = team_text.split("\n")
    teams_with_time = parse_teams_with_time(team_lines)

    if len(teams_with_time) < 2:
        st.error("Enter at least 2 teams with valid times")
    else:
        generate_knockout(teams_with_time)
        st.info("👉 Use browser Print (Ctrl + P) to Print or Save as PDF")
