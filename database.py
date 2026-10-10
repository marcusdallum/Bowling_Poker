import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'bowling_poker.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable access by column name
    return conn

def init_db():
    """Initializes the database schema."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Roster table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roster (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                p1 TEXT,
                p2 TEXT,
                p3 TEXT,
                p4 TEXT,
                off TEXT
            )
        ''')
        
        # Scores table - Added game_number
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roster_id INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                game_number INTEGER NOT NULL,
                FOREIGN KEY (roster_id) REFERENCES roster (id) ON DELETE CASCADE
            )
        ''')
        
        # Winners table - Added game_number
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roster_id INTEGER NOT NULL,
                winner_name TEXT NOT NULL,
                game_type TEXT NOT NULL,
                game_number INTEGER NOT NULL,
                FOREIGN KEY (roster_id) REFERENCES roster (id) ON DELETE CASCADE
            )
        ''')
        conn.commit()

def add_roster_entry(date, p1, p2, p3, p4, off):
    """Adds a new entry to the roster."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO roster (date, p1, p2, p3, p4, off)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, p1, p2, p3, p4, off))
        conn.commit()
        return cursor.lastrowid

def update_roster_entry(roster_id, **kwargs):
    """Updates an existing roster entry."""
    if not kwargs:
        return False
    
    columns = ', '.join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.append(roster_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'UPDATE roster SET {columns} WHERE id = ?', values)
        conn.commit()
        return cursor.rowcount > 0

def save_score(roster_id, player_name, score, game_number):
    """Saves a score for a specific player and game in a roster entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO scores (roster_id, player_name, score, game_number)
            VALUES (?, ?, ?, ?)
        ''', (roster_id, player_name, score, game_number))
        conn.commit()

def save_winner(roster_id, winner_name, game_type, game_number):
    """Records the winner of a specific game for a roster entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO winners (roster_id, winner_name, game_type, game_number)
            VALUES (?, ?, ?, ?)
        ''', (roster_id, winner_name, game_type, game_number))
        conn.commit()

def get_roster_by_id(roster_id):
    """Fetches a roster entry by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roster WHERE id = ?', (roster_id,))
        return cursor.fetchone()

def get_all_rosters():
    """Fetches all roster entries."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM roster ORDER BY date DESC')
        return cursor.fetchall()

def get_scores_for_roster(roster_id):
    """Fetches all scores for a specific roster entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scores WHERE roster_id = ?', (roster_id,))
        return cursor.fetchall()

def get_winners_for_roster(roster_id):
    """Fetches all winners for a specific roster entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM winners WHERE roster_id = ?', (roster_id,))
        return cursor.fetchall()
