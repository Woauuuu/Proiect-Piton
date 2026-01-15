import sqlite3

# =========================
# FOODS DATABASE
# =========================
def connect_foods():
    return sqlite3.connect("foods.db")

def create_foods_table():
    conn = connect_foods()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            calories_per_100g INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_food(name, calories_per_100g):
    conn = connect_foods()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO foods (name, calories_per_100g) VALUES (?, ?)",
            (name, calories_per_100g)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def get_calories_per_100g(food_name):
    conn = connect_foods()
    c = conn.cursor()
    c.execute("SELECT calories_per_100g FROM foods WHERE name = ?", (food_name,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_foods():
    conn = connect_foods()
    c = conn.cursor()
    c.execute("SELECT name, calories_per_100g FROM foods")
    foods = c.fetchall()
    conn.close()
    return foods

def populate_default_foods():
    foods = {
        "Paine alba feliata": 265,
        "Paine integrala": 247,
        "Chifla": 280,
        "Croissant": 406,
        "Fulgi de ovaz": 389,
        "Orez alb": 130,
        "Paste": 131,
        "Cereale porumb": 365,

        "Lapte 1.5%": 46,
        "Lapte 3.5%": 64,
        "Iaurt simplu": 59,
        "Iaurt grecesc": 133,
        "Branza telemea": 270,
        "Cascaval": 356,
        "Smantana 12%": 136,
        "Unt": 717,

        "Piept de pui": 165,
        "Pulpe de pui": 209,
        "Carne tocata porc/vita": 250,
        "Cotlet porc": 242,
        "Salam": 330,
        "Sunca presata": 145,
        "Crenvursti": 270,
        "Pate": 320,

        "Ou": 155,
        "Ton conserva in apa": 116,
        "Ton in ulei": 198,
        "Fasole conserva": 90,
        "Porumb conserva": 86,

        "Cartofi": 77,
        "Rosii": 18,
        "Castraveti": 16,
        "Ceapa": 40,
        "Morcovi": 41,
        "Banana": 89,
        "Mar": 52,

        "Ciocolata": 546,
        "Biscuiti": 480,
        "Chipsuri": 536,
        "Inghetata": 207,

        "Ulei": 884,
        "Miere": 304,
        "Zahar": 387,
        "Ketchup": 112
    }

    for food, calories in foods.items():
        add_food(food, calories)

# =========================
# USER CALORIES DATABASE
# =========================
def connect_user():
    return sqlite3.connect("user_calories.db")

def create_eaten_table():
    conn = connect_user()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS eaten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food TEXT,
            grams REAL,
            calories REAL
        )
    """)
    conn.commit()
    conn.close()

def add_eaten(food, grams, calories):
    conn = connect_user()
    c = conn.cursor()
    c.execute(
        "INSERT INTO eaten (food, grams, calories) VALUES (?, ?, ?)",
        (food, grams, calories)
    )
    conn.commit()
    conn.close()

def get_all_eaten():
    conn = connect_user()
    c = conn.cursor()
    c.execute("SELECT id, food, grams, calories FROM eaten")
    data = c.fetchall()
    conn.close()
    return data

# NEW: delete by id and tell if it actually deleted something
def delete_eaten_by_id_safe(eaten_id) -> bool:
    conn = connect_user()
    c = conn.cursor()
    c.execute("DELETE FROM eaten WHERE id = ?", (eaten_id,))
    deleted = (c.rowcount > 0)
    conn.commit()
    conn.close()
    return deleted

def total_calories():
    conn = connect_user()
    c = conn.cursor()
    c.execute("SELECT SUM(calories) FROM eaten")
    total = c.fetchone()[0]
    conn.close()
    return total if total else 0
