import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS places (
    city TEXT,
    name TEXT,
    type TEXT,
    cost INTEGER
)
""")

# Sample data
data = [
    ("Goa", "Baga Beach", "beach", 0),
    ("Goa", "Fort Aguada", "historical", 50),
    ("Goa", "Calangute Beach", "beach", 0),
    ("Goa", "Casino", "entertainment", 2000)
]

cursor.executemany("INSERT INTO places VALUES (?,?,?,?)", data)

conn.commit()
cursor.execute("SELECT * FROM places")
rows = cursor.fetchall()

for row in rows:
    print(row)
conn.close()