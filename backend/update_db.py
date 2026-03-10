import sqlite3

def update_db():
    conn = sqlite3.connect('/app/data/pipeline_tracker.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0;")
    except sqlite3.OperationalError as e:
        print(f"Adding column failed (might exist): {e}")

    cursor.execute("UPDATE users SET is_admin = 1 WHERE username = 'admin';")
    conn.commit()
    conn.close()
    print("Database updated successfully.")

if __name__ == '__main__':
    update_db()
