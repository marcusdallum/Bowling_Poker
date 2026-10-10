import csv
import os
from database import init_db, add_roster_entry, get_connection

def migrate():
    # Initialize the database
    init_db()
    
    roster_file = 'roster.txt'
    if not os.path.exists(roster_file):
        print(f"Error: {roster_file} not found.")
        return

    count_txt = 0
    with open(roster_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header
        
        for row in reader:
            if not row or len(row) < 6:
                continue
            
            date, p1, p2, p3, p4, off = row
            add_roster_entry(date, p1, p2, p3, p4, off)
            count_txt += 1

    # Verify
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM roster')
        count_db = cursor.fetchone()[0]

    print(f"Migration completed.")
    print(f"Records in roster.txt: {count_txt}")
    print(f"Records in database: {count_db}")
    
    if count_txt == count_db:
        print("Verification successful: Record counts match.")
    else:
        print(f"Verification failed: Text file has {count_txt} records, but DB has {count_db}.")

if __name__ == "__main__":
    migrate()
