import os
import csv
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# The directory where static HTML files are located
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

def get_roster():
    """Reads the roster.txt file and returns a list of dictionaries."""
    roster = []
    try:
        # Using absolute path to be safe
        file_path = os.path.join(STATIC_DIR, "roster.txt")
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                roster.append(row)
    except FileNotFoundError:
        print("roster.txt not found!")
    return roster

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
    """Serves the meet_the_team.html file."""
    return send_from_directory(STATIC_DIR, "meet_the_team.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
