import os
import csv
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

def get_roster():
    """Reads the roster.txt file and returns a list of dictionaries."""
    roster = []
    try:
        file_path = os.path.join(STATIC_DIR, "roster.txt")
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                roster.append(row)
    except FileNotFoundError:
        print("roster.txt not found!")
    return roster

def get_unique_players():
    """Extracts the unique list of players from the roster.txt file."""
    roster = get_roster()
    if not roster:
        return ["Jerry", "Marc", "Kevin", "Mark", "Brandon"] # Fallback
    
    players = set()
    for row in roster:
        # Add players 1-4 and the off person
        players.add(row['Player 1'])
        players.add(row['Player 2'])
        players.add(row['Player 3'])
        players.add(row['Player 4'])
        players.add(row['Off'])
    
    # Return as a sorted list for consistency
    return sorted(list(players))

@app.route("/")
def serve_index():
    """Serves the index.html file at the root URL."""
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/rules")
def serve_rules():
    """Serves the rules.md file for reference."""
    return send_from_directory(STATIC_DIR, "rules.md")

@app.route("/poker-rules")
def serve_poker_rules():
    """Serves the poker_rules.html file."""
    return send_from_directory(STATIC_DIR, "poker_rules.html")

@app.route("/schedule")
def serve_schedule():
    """Renders the schedule page with data from roster.txt."""
    roster_data = get_roster()
    return render_template("schedule.html", roster=roster_data)

@app.route("/meet-the-team")
def serve_meet_the_team():
    """Renders the team page with the player list."""
    players_list = get_unique_players()
    return render_template("meet_the_team.html", players=players_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
