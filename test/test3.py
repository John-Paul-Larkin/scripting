import sqlite3;

conn = sqlite3.connect("test.db");

cursor = conn.cursor();

cursor.execute("CREATE TABLE IF NOT EXISTS myTable(name TEXT, age INT)");

cursor.fetchall
cursor.fetchone
cursor.execute # execute a query

