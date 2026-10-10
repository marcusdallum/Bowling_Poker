
from database import init_db
import os
try:
    init_db()
    print('DB initialized successfully')
    if os.path.exists('bowling_poker.db'):
        print('Database file created: bowling_poker.db')
except Exception as e:
    print(f'Error: {e}')
