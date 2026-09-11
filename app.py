import os
import csv
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

def get_roster():
    """Reads the roster.txt file and returns a list of dictionaries with date status."""
    roster = []
    try:
        file_path = os.path.join(STATIC_DIR, "roster.txt")
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Calculate current window
            today = datetime.now().date()
            # Find the Wednesday of the current week
            # weekday(): Monday=0, ..., Wednesday=2, ..., Sunday=6
            days_to_wednesday = (2 - today.weekday()) % 7
            this_wednesday = today + timedelta(days=days_to_wednesday)
            
            for row in reader:
                game_date = datetime.strptime(row['Date'], "%Y-%m-%d").date()
                
                if game_date < this_wednesday:
                    status = 'past'
                elif game_date == this_wednesday:
                    status = 'current'
                else:
                    status = 'future'
                
                row['status'] = status
                roster.append(row)
    except FileNotFoundError:
        print("roster.txt not found!")
    return roster

def get_unique_players():
    """Extracts the unique list of players from the roster.txt file."""
    roster = get_roster()
    if not roster:
        return ["Jerry", "Marc", "Kevin", "Mark", "Brandon"]
    
    players = set()
    for row in roster:
        players.add(row['Player 1'])
        players.add(row['Player 2'])
        players.add(row['Player 3'])
        players.add(row['Player 4'])
        players.add(row['Off'])
    
    return sorted(list(players))

@app.route("/")
def serve_index():
    return send_from_directory(STATIC_DIR, "index.html")

@app.route("/rules")
def serve_rules():
    return send_from_directory(STATIC_DIR, "rules.md")

@app.route("/poker-rules")
def serve_poker_rules():
    return send_from_directory(STATIC_DIR, "poker_rules.html")

@app.route("/schedule")
def serve_schedule():
    roster_data = get_roster()
    
    # Reorder: Current first, then Future, then Past
    current = [r for r in roster_data if r['status'] == 'current']
    future = [r for r in roster_data if r['status'] == 'future']
    past = [r for r in roster_data if r['status'] == 'past']
    
    # Sort future and past chronologically
    future.sort(key=lambda x: x['Date'])
    past.sort(key=lambda x: x['Date'], reverse=True) # Newest past first
    
    ordered_roster = current + future + past
    
    return render_template("schedule.html", roster=ordered_roster)

@app.route("/meet-the-team")
def serve_meet_the_team():
    players_list = get_unique_players()
    return render_template("meet_the_team.html", players=players_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
