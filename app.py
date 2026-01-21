import streamlit as st
import re

# ---------------- PAGE ----------------
st.set_page_config(page_title="Seeded Knockout Fixtures", layout="centered")
st.title("🏏 Seeded Knockout Fixture Generator (Leaderboard Based)")

st.write("Enter teams and times in seconds (fastest = Rank 1)")
st.write("Format:  TEAM NAME , 12.56s")

team_text = st.text_area(
    "Enter Teams & Times (one per line)",
    height=350,
    placeholder="TEAM 1 , 10.2s\nTEAM 2 , 11s\nTEAM 3 , 9.8s\nTEAM 4 , 13s"
)

# ---------------- UTIL ----------------

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

        match = re.search(r"(\d+(\.\d+)?)", time_part)
        if not match:
            st.warning(f"Invalid time for team: {name}")
            continue

        time = float(match.group(1))
        teams.append((name, time))

    return teams

def seeded_pairs(team_list):
    """1 vs N, 2 vs N-1, ..."""
    pairs = []
    i = 0
    j = len(team_list) - 1
    while i < j:
        pairs.append((team_list[i], team_list[j]))
        i += 1
        j -= 1
    return pairs

# ---------------- FIXTURE LOGIC ----------------

def generate_knockout(teams_with_time):

    # sort leaderboard (fastest first)
    teams_with_time.sort(key=lambda x: x[1])

    st.subheader("🏁 Leaderboard (Fastest First)")
    for i, (n, t) in enumerate(teams_with_time, start=1):
        st.write(f"{i}. {n} — {t}s")

    teams = [t[0] for t in teams_with_time]
    match_no = 1

    total = len(teams)
    power2 = next_power_of_two(total)

    # -------- ROUND 1 : BYE ROUND IF NEEDED --------
    if total != power2:
        byes = power2 - total
        st.subheader("ROUND 1 — BYE ROUND (Top Seeds Advance)")

        bye_teams = teams[:byes]
        play_teams = teams[byes:]

        st.success(f"Top {byes} teams get BYE:")
        st.write(", ".join(bye_teams))

        next_round = bye_teams.copy()

        i = 0
        while i < len(play_teams):
            st.write(f"Match {match_no}: {play_teams[i]} vs {play_teams[i+1]}")
            next_round.append(f"Winner of Match {match_no}")
            match_no += 1
            i += 2

        teams = next_round

    # -------- SEEDED POWER-OF-2 ROUNDS --------
    round_no = 2

    while len(teams) > 1:

        if len(teams) == 2:
            round_name = "🏆 FINAL"
        elif len(teams) == 4:
            round_name = "🔥 SEMIFINAL"
        elif len(teams) == 8:
            round_name = "⚡ QUARTERFINAL"
        elif len(teams) == 16:
            round_name = "ROUND OF 16"
        else:
            round_name = f"ROUND {round_no}"

        st.subheader(round_name)

        pairs = seeded_pairs(teams)
        next_round = []

        for a, b in pairs:
            st.write(f"Match {match_no}: {a} vs {b}")
            next_round.append(f"Winner of Match {match_no}")
            match_no += 1

        teams = next_round
        round_no += 1

    st.success(f"🏆 Champion: {teams[0]}")

# ---------------- MAIN ----------------

if st.button("Generate Fixtures"):
    team_lines = team_text.split("\n")
    teams_with_time = parse_teams_with_time(team_lines)

    if len(teams_with_time) < 2:
        st.error("Enter at least 2 teams with valid times")
    else:
        generate_knockout(teams_with_time)
        st.info("👉 Press Ctrl + P to Print or Save as PDF")
