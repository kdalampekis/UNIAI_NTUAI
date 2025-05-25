
import sqlite3
import os

DB_PATH = 'data/wardrobe.db'

def init_db():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Wardrobe items table
    c.execute("""
        CREATE TABLE IF NOT EXISTS wardrobe_items (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            image_url TEXT,
            type TEXT,
            sub_type TEXT,
            color TEXT,
            color_hex TEXT,
            material TEXT,
            pattern TEXT,
            size TEXT,
            brand TEXT,
            style TEXT,
            season TEXT,
            mood TEXT,
            tags TEXT,
            favorite INTEGER DEFAULT 0,
            date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_worn DATETIME,
            wear_count INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def insert_user(user: dict):
    import bcrypt

    raw_password = user['password']
    password_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT OR IGNORE INTO users (id, username, email, password_hash)
                 VALUES (?, ?, ?, ?)""", (
        user['id'], user['username'], user['email'], password_hash
    ))
    conn.commit()
    conn.close()

def insert_item(item: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO wardrobe_items
                 (id, user_id, filename, image_url, type, sub_type, color, color_hex,
                  material, pattern, size, brand, style, season, mood,
                  favorite, date_added, last_worn, wear_count)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              """, (
        item['id'], item['user_id'], item['filename'], item.get('image_url'),
        item.get('type'), item.get('sub_type'), item.get('color'),
        item.get('color_hex'), item.get('material'), item.get('pattern'),
        item.get('size'), item.get('brand'), item.get('style'),
        item.get('season'), item.get('mood'), item.get('favorite', 0),
        item.get('date_added'), item.get('last_worn'), item.get('wear_count', 0)
    ))
    conn.commit()
    conn.close()

def insert_tag(name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    conn.commit()
    c.execute("SELECT id FROM tags WHERE name = ?", (name,))
    tag_id = c.fetchone()[0]
    conn.close()
    return tag_id

def attach_tag_to_item(item_id: str, tag_name: str):
    tag_id = insert_tag(tag_name)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO item_tags (item_id, tag_id) VALUES (?, ?)", (item_id, tag_id))
    conn.commit()
    conn.close()

if __name__ =="__main__":
    init_db()
    print("Database created successfully.")