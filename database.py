# database.py

import sqlite3
import os

DB_FILE = 'quiz_app.db'
def create_connection():
    conn = sqlite3.connect('quiz_app.db')
    return conn

import sqlite3

def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    conn = create_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS quizzes (
                 id INTEGER PRIMARY KEY,
                 title TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                 id INTEGER PRIMARY KEY,
                 quiz_id INTEGER,
                 question TEXT,
                 answer BOOLEAN,
                 FOREIGN KEY(quiz_id) REFERENCES quizzes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS scores (
                 id INTEGER PRIMARY KEY,
                 quiz_id INTEGER,
                 score INTEGER,
                 total_questions INTEGER,
                 date TEXT,
                 FOREIGN KEY(quiz_id) REFERENCES quizzes(id))''')
    conn.commit()
    conn.close()

# Optionally, add some sample data
def add_sample_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM quizzes')
    count = c.fetchone()[0]
    if count == 0:
        c.execute('INSERT INTO quizzes (title) VALUES ("Sample Quiz")')
        quiz_id = c.lastrowid
        c.execute('INSERT INTO questions (quiz_id, question, answer) VALUES (?, ?, ?)', (quiz_id, "Is the sky blue?", True))
        conn.commit()
    conn.close()

def initialize_database():
    if not os.path.exists(DB_FILE):
        create_tables()
        add_sample_data()
    else:
        create_tables()  # Ensure all tables exist