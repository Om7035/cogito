import sqlite3
import json
import os

DB_PATH = "audits/cogito.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            claim TEXT,
            parsed_json TEXT,
            results_json TEXT,
            verdict TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_audit(claim, parsed_json, results_json, verdict="Unknown"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO audits (claim, parsed_json, results_json, verdict)
        VALUES (?, ?, ?, ?)
    ''', (claim, json.dumps(parsed_json), json.dumps(results_json), verdict))
    conn.commit()
    conn.close()
