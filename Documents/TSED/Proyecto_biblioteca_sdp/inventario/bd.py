import sqlite3

def get_connection():
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    return conn

def crear_tabla():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            cantidad INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
