import sqlite3
import datetime
import random


# Connect to database (creates it if it doesn't exist)
conn = sqlite3.connect('chat.db')
cursor = conn.cursor()

# Enable foreign key support
cursor.execute('PRAGMA foreign_keys = ON')

# First, drop existing tables if they exist
cursor.execute('DROP TABLE IF EXISTS messages')
cursor.execute('DROP TABLE IF EXISTS users')

# Create users table first (referenced table must exist before foreign key)
cursor.execute('''
CREATE TABLE users (
    user_name TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

# Create messages table with correct foreign key reference
cursor.execute('''
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    content TEXT NOT NULL,
    room_name TEXT NOT NULL,
    FOREIGN KEY (user_name) REFERENCES users(user_name)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)
''')

# Add sample users first
sample_users = [
    ("Tom", "tom"),
    ("Patrizio", "patrizio"),
    ("John", "john"),
    ("Colm", "colm"),
    ("Kate", "kate")
]

cursor.executemany('''
INSERT OR IGNORE INTO users (user_name, password)
VALUES (?, ?)
''', sample_users)

# Add some dummy messages
rooms = ["General", "Cats", "Tech talk", "Foodies"]
users = ["Tom", "Patrizio", "John", "Colm", "Kate"]
sample_messages = [
    "Hello everyone!",
    "How's it going?", 
    "Nice weather today",
    "Anyone working on something interesting?",
    "I'm learning Python",
    "This chat app is cool",
    "Who's up for coffee?",
    "Did you see the game last night?",
    "Happy Friday!",
    "What's new?"
]

# Generate random timestamps within last 24 hours
base = datetime.datetime.now() - datetime.timedelta(days=1)

for room in rooms:
    # Random number of messages between 5-10 for each room
    num_messages = random.randint(5, 10)
    
    for _ in range(num_messages):
        user = random.choice(users)
        message = random.choice(sample_messages)
        timestamp = base + datetime.timedelta(
            seconds=random.randint(0, 24*60*60)
        )
        
        cursor.execute('''
        INSERT INTO messages (user_name, timestamp, content, room_name)
        VALUES (?, ?, ?, ?)
        ''', (user, timestamp, message, room))



# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully!")


