import os, sys, tempfile, io, pytest
from werkzeug.security import generate_password_hash

# Ensure the project root (Bowling_Poker) is on sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set a dummy secret key for Flask app configuration
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

from app import app, database

@pytest.fixture
def client():
    # Use a temporary SQLite file for isolation
    fd, temp_path = tempfile.mkstemp()
    os.close(fd)
    # Patch the DB_PATH to point to the temporary file
    original_path = database.DB_PATH
    database.DB_PATH = temp_path
    # Initialize schema
    database.init_db()
    # Configure Flask testing client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Cleanup
    database.DB_PATH = original_path
    os.remove(temp_path)

def login_admin(client):
    # Set required env vars for admin login
    os.environ['ADMIN_USER_ID'] = 'admin'
    os.environ['ADMIN_PASSWORD_HASH'] = generate_password_hash('')  # Valid hash for empty password
    # Log in via POST to /login (no password needed because hash is empty)
    return client.post('/login', data={'username': 'admin', 'password': ''}, follow_redirects=True)

def test_import_csv_success(client):
    # Ensure admin is logged in
    login_admin(client)
    # Prepare a minimal CSV payload
    csv_data = "date,p1,p2,p3,p4,off\n2023-10-19,Jerry,Marc,Kevin,Mark,Brandon\n"
    data = {'file': (io.BytesIO(csv_data.encode()), 'roster.csv')}
    # Post to the import route
    client.post('/admin/import-roster', data=data, content_type='multipart/form-data', follow_redirects=True)
    # Verify the roster was inserted
    rosters = database.get_all_rosters()
    assert len(rosters) == 1
    assert rosters[0]['date'] == '2023-10-19'
    assert rosters[0]['p1'] == 'Jerry'

def test_import_csv_duplicate(client):
    login_admin(client)
    # Insert a roster entry directly
    database.add_roster_entry('2023-10-19', 'Jerry', 'Marc', 'Kevin', 'Mark', 'Brandon')
    # Try to import the same row again
    csv_data = "date,p1,p2,p3,p4,off\n2023-10-19,Jerry,Marc,Kevin,Mark,Brandon\n"
    data = {'file': (io.BytesIO(csv_data.encode()), 'roster.csv')}
    client.post('/admin/import-roster', data=data, content_type='multipart/form-data', follow_redirects=True)
    # Ensure only one entry exists
    rosters = database.get_all_rosters()
    assert len(rosters) == 1
