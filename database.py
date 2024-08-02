import sqlite3
import os
import random

DB_FILE = os.path.join(os.path.expanduser('~'), 'quiz_app.db')

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

def add_sample_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM quizzes')
    count = c.fetchone()[0]
    if count == 0:
        c.execute('INSERT INTO quizzes (title) VALUES ("Sample Quiz")')
        quiz_id = c.lastrowid
        sample_questions = [
            ("Is the sky blue?", True),
            ("Is the Earth flat?", False),
            ("Is water wet?", True),
            ("Do pigs fly?", False),
            ("Is the sun a planet?", False)
        ]
        c.executemany('INSERT INTO questions (quiz_id, question, answer) VALUES (?, ?, ?)', 
                      [(quiz_id, q, a) for q, a in sample_questions])
        conn.commit()
    conn.close()

def initialize_database():
    if not os.path.exists(DB_FILE):
        create_tables()
        add_sample_data()
    else:
        create_tables()  # Ensure all tables exist

def get_all_questions(quiz_id=None):
    conn = create_connection()
    c = conn.cursor()
    if quiz_id:
        c.execute("SELECT id, question, answer FROM questions WHERE quiz_id = ?", (quiz_id,))
    else:
        c.execute("SELECT id, question, answer FROM questions")
    questions = c.fetchall()
    conn.close()
    return [{'id': q[0], 'question': q[1], 'answer': q[2]} for q in questions]

def get_random_questions(n, quiz_id=None):
    all_questions = get_all_questions(quiz_id)
    if len(all_questions) <= n:
        return all_questions
    return random.sample(all_questions, n)

def get_quizzes():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT id, title FROM quizzes")
    quizzes = c.fetchall()
    conn.close()
    return [{'id': q[0], 'title': q[1]} for q in quizzes]

def add_score(quiz_id, score, total_questions, date):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO scores (quiz_id, score, total_questions, date) VALUES (?, ?, ?, ?)",
              (quiz_id, score, total_questions, date))
    conn.commit()
    conn.close()

def get_scores(quiz_id=None):
    conn = create_connection()
    c = conn.cursor()
    if quiz_id:
        c.execute("SELECT id, quiz_id, score, total_questions, date FROM scores WHERE quiz_id = ?", (quiz_id,))
    else:
        c.execute("SELECT id, quiz_id, score, total_questions, date FROM scores")
    scores = c.fetchall()
    conn.close()
    return [{'id': s[0], 'quiz_id': s[1], 'score': s[2], 'total_questions': s[3], 'date': s[4]} 
            if len(s) == 5 else {'id': None, 'quiz_id': None, 'score': None, 'total_questions': None, 'date': None} 
            for s in scores]

def add_quiz(title):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO quizzes (title) VALUES (?)", (title,))
    quiz_id = c.lastrowid
    conn.commit()
    conn.close()
    return quiz_id

def update_quiz(quiz_id, new_title):
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE quizzes SET title = ? WHERE id = ?", (new_title, quiz_id))
    conn.commit()
    conn.close()

def remove_quiz(quiz_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE quiz_id = ?", (quiz_id,))
    c.execute("DELETE FROM scores WHERE quiz_id = ?", (quiz_id,))
    c.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()

def add_question(quiz_id, question, answer):
    conn = create_connection()
    c = conn.cursor()
    c.execute("INSERT INTO questions (quiz_id, question, answer) VALUES (?, ?, ?)",
              (quiz_id, question, answer))
    conn.commit()
    conn.close()

def update_question(question_id, new_question, new_answer):
    conn = create_connection()
    c = conn.cursor()
    c.execute("UPDATE questions SET question = ?, answer = ? WHERE id = ?",
              (new_question, new_answer, question_id))
    conn.commit()
    conn.close()

def get_questions(quiz_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT id, quiz_id, question, answer FROM questions WHERE quiz_id = ?", (quiz_id,))
    questions = c.fetchall()
    conn.close()
    return [{'id': q[0], 'quiz_id': q[1], 'question': q[2], 'answer': q[3]} for q in questions]

def delete_question(question_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()