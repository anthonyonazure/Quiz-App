import sqlite3
from database import create_connection

def add_quiz(title):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO quizzes (title) VALUES (?)', (title,))
    conn.commit()
    quiz_id = c.lastrowid
    conn.close()
    return quiz_id

def add_question(quiz_id, question, answer):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO questions (quiz_id, question, answer) VALUES (?, ?, ?)', (quiz_id, question, answer))
    conn.commit()
    conn.close()

def get_quizzes():
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM quizzes')
    quizzes = c.fetchall()
    conn.close()
    return quizzes

def get_questions(quiz_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM questions WHERE quiz_id = ?', (quiz_id,))
    questions = c.fetchall()
    conn.close()
    return questions

def remove_quiz(quiz_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute('DELETE FROM quizzes WHERE id = ?', (quiz_id,))
    c.execute('DELETE FROM questions WHERE quiz_id = ?', (quiz_id,))
    conn.commit()
    conn.close()

def update_quiz(quiz_id, title):
    conn = create_connection()
    c = conn.cursor()
    c.execute('UPDATE quizzes SET title = ? WHERE id = ?', (title, quiz_id))
    conn.commit()
    conn.close()

def update_question(question_id, question, answer):
    conn = create_connection()
    c = conn.cursor()
    c.execute('UPDATE questions SET question = ?, answer = ? WHERE id = ?', (question, answer, question_id))
    conn.commit()
    conn.close()

def add_score(quiz_id, score, total_questions, date):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO scores (quiz_id, score, total_questions, date) VALUES (?, ?, ?, ?)', (quiz_id, score, total_questions, date))
    conn.commit()
    conn.close()

def get_scores(quiz_id):
    conn = create_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM scores WHERE quiz_id = ?', (quiz_id,))
    scores = c.fetchall()
    conn.close()
    return scores

def add_score(quiz_id, score, total_questions, date):
    conn = create_connection()
    c = conn.cursor()
    c.execute('INSERT INTO scores (quiz_id, score, total_questions, date) VALUES (?, ?, ?, ?)', (quiz_id, score, total_questions, date))
    conn.commit()
    conn.close()
