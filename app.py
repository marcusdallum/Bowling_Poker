from dotenv import load_dotenv
load_dotenv()
import os
import csv
import database
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.secret_key = os.environ['FLASK_SECRET_KEY']

class User(UserMixin):
    def __init__(self, id):
        self.id = id

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Use env var for the admin username
    if user_id == os.environ.get('ADMIN_USER_ID', 'admin'):
        return User(user_id)
    return None

STATIC_DIR = os.path.dirname(os.path.abspath(__file__))

def get_roster():
    """Reads the roster.txt file and returns a list of dictionaries with date status."""
    roster = []
    try:
        file_path = os.path.join(STATIC_DIR, "roster.txt")
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            today = datetime.now().date()
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

def calculate_averages():
    """Calculates the average bowling score for each player."""
    averages = {}
    try:
        with database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT player_name, AVG(score) as average FROM scores GROUP BY player_name')
            rows = cursor.fetchall()
            for row in rows:
                averages[row['player_name']] = round(row['average'], 1)
    except Exception as e:
        print(f"Error calculating averages: {e}")
    return averages

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
    roster_data = database.get_all_rosters()
    today = datetime.now().date()
    days_to_wednesday = (2 - today.weekday()) % 7
    this_wednesday = today + timedelta(days=days_to_wednesday)
    processed_roster = []
    for row in roster_data:
        entry = dict(row)
        game_date = datetime.strptime(entry['date'], "%Y-%m-%d").date()
        if game_date < this_wednesday:
            status = 'past'
        elif game_date == this_wednesday:
            status = 'current'
        else:
            status = 'future'
        entry['status'] = status
        scores = database.get_scores_for_roster(entry['id'])
        entry['scores'] = {s['player_name']: s['score'] for s in scores}
        winners = database.get_winners_for_roster(entry['id'])
        card_winner = next((w['winner_name'] for w in winners if w['game_type'] == 'Card Game'), None)
        entry['card_winner'] = card_winner
        processed_roster.append(entry)
    current = [r for r in processed_roster if r['status'] == 'current']
    future = [r for r in processed_roster if r['status'] == 'future']
    past = [r for r in processed_roster if r['status'] == 'past']
    future.sort(key=lambda x: x['date'])
    past.sort(key=lambda x: x['date'], reverse=True)
    ordered_roster = current + future + past
    return render_template("schedule.html", roster=ordered_roster)

@app.route("/meet-the-team")
def serve_meet_the_team():
    players_list = get_unique_players()
    averages = calculate_averages()
    return render_template("meet_the_team.html", players=players_list, averages=averages)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin_id = os.environ.get('ADMIN_USER_ID', 'admin')
        admin_hash = os.environ.get('ADMIN_PASSWORD_HASH')
        if username == admin_id and admin_hash and check_password_hash(admin_hash, password):
            user = User(username)
            login_user(user)
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("serve_index"))

@app.route("/admin")
@login_required
def admin_dashboard():
    return render_template("admin.html")

@app.route("/admin/edit-roster", methods=["GET", "POST"])
@login_required
def edit_roster():
    if request.method == "POST":
        entry_id = request.form.get("id")
        date = request.form.get("date")
        p1 = request.form.get("p1")
        p2 = request.form.get("p2")
        p3 = request.form.get("p3")
        p4 = request.form.get("p4")
        off = request.form.get("off")

        try:
            if entry_id:
                success = database.update_roster_entry(int(entry_id), date=date, p1=p1, p2=p2, p3=p3, p4=p4, off=off)
                msg = "Entry updated successfully!" if success else "Failed to update entry."
            else:
                database.add_roster_entry(date, p1, p2, p3, p4, off)
                msg = "New entry added successfully!"
            
            flash(msg, "success" if "successfully" in msg else "error")
        except Exception as e:
            flash(f"Error saving entry: {str(e)}", "error")
        
        return redirect(url_for("edit_roster"))

    entry_id = request.args.get("entry_id")
    editing_entry = None
    if entry_id:
        editing_entry = database.get_roster_by_id(int(entry_id))
    
    roster = database.get_all_rosters()
    return render_template("admin_roster.html", roster=roster, entry=editing_entry)

@app.route("/admin/enter-scores", methods=["GET", "POST"])
@login_required
def enter_scores():
    if request.method == "POST":
        roster_id = request.form.get("roster_id")
        if not roster_id:
            flash("Please select a week.", "error")
            return redirect(url_for("enter_scores"))
        try:
            roster_id = int(roster_id)
            entry = database.get_roster_by_id(roster_id)
            if not entry:
                flash("Roster entry not found.", "error")
                return redirect(url_for("enter_scores"))
            players = [entry['p1'], entry['p2'], entry['p3'], entry['p4']]
            for g in range(1, 4):
                for i in range(4):
                    score_val = request.form.get(f"score_{g}_{i}")
                    if score_val is not None and score_val != '':
                        database.save_score(roster_id, players[i], int(score_val), g)
                card_winner = request.form.get(f"card_winner_{g}")
                if card_winner:
                    database.save_winner(roster_id, card_winner, "Card Game", g)
            flash("Results for all 3 games saved successfully!", "success")
        except Exception as e:
            flash(f"Error saving results: {str(e)}", "error")
        return redirect(url_for("enter_scores"))

    selected_id = request.args.get("roster_id")
    entry = None
    if selected_id:
        entry = database.get_roster_by_id(int(selected_id))
    roster = database.get_all_rosters()
    return render_template("admin_results.html", roster=roster, entry=entry, selected_id=selected_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
