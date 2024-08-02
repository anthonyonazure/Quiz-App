import sys
import random
import datetime
import winreg
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QRadioButton, QButtonGroup, QScrollArea, 
                             QMessageBox, QListWidget, QDialog, QLineEdit, QFormLayout, 
                             QDialogButtonBox, QComboBox, QInputDialog, QListWidgetItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from database import (get_quizzes, get_all_questions, get_random_questions, 
                      add_score, get_scores, initialize_database, add_quiz,
                      update_quiz, remove_quiz, add_question, update_question,
                      get_questions, delete_question)

def is_dark_mode():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except:
        return False

def set_dark_mode_palette(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

class QuizApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quiz App")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.quiz_list = QListWidget()
        self.layout.addWidget(self.quiz_list)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Quiz")
        self.create_button = QPushButton("Create Quiz")
        self.edit_button = QPushButton("Edit Quiz")
        self.remove_button = QPushButton("Remove Quiz")
        self.scores_button = QPushButton("View Scores")

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.scores_button)

        self.layout.addLayout(button_layout)

        self.start_button.clicked.connect(self.start_quiz)
        self.create_button.clicked.connect(self.create_quiz)
        self.edit_button.clicked.connect(self.edit_quiz)
        self.remove_button.clicked.connect(self.remove_quiz)
        self.scores_button.clicked.connect(self.view_scores)

        self.load_quizzes()

    def load_quizzes(self):
        self.quiz_list.clear()
        quizzes = get_quizzes()
        for quiz in quizzes:
            self.quiz_list.addItem(quiz['title'])

    def start_quiz(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz['id'] for quiz in get_quizzes() if quiz['title'] == quiz_title][0]
            self.quiz_window = QuizWindow(quiz_id)
            self.quiz_window.show()
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to start.')

    def create_quiz(self):
        text, ok = QInputDialog.getText(self, 'Create Quiz', 'Enter quiz title:')
        if ok and text:
            try:
                quiz_id = add_quiz(text)
                self.load_quizzes()
                self.create_questions(quiz_id)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to create quiz: {str(e)}')

    def create_questions(self, quiz_id):
        while True:
            question, ok = QInputDialog.getText(self, 'Create Question', 'Enter question text:')
            if not ok or not question:
                break
            answer, ok = QInputDialog.getItem(self, 'Create Question', 'Select the correct answer:', ['True', 'False'], 0, False)
            if not ok:
                break
            add_question(quiz_id, question, answer == 'True')

    def edit_quiz(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz['id'] for quiz in get_quizzes() if quiz['title'] == quiz_title][0]
            self.edit_quiz_dialog = EditQuizDialog(quiz_id)
            self.edit_quiz_dialog.exec()
            self.load_quizzes()
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to edit.')

    def remove_quiz(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz['id'] for quiz in get_quizzes() if quiz['title'] == quiz_title][0]
            confirm = QMessageBox.question(self, 'Confirm Deletion', 
                                           f'Are you sure you want to delete "{quiz_title}"?',
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                remove_quiz(quiz_id)
                self.load_quizzes()
                QMessageBox.information(self, 'Quiz Removed', f'Quiz "{quiz_title}" has been removed.')
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to remove.')

    def view_scores(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz['id'] for quiz in get_quizzes() if quiz['title'] == quiz_title][0]
            self.score_window = ScoreWindow(quiz_id)
            self.score_window.show()
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to view scores.')

class QuizWindow(QWidget):
    def __init__(self, quiz_id):
        super().__init__()
        self.quiz_id = quiz_id
        self.questions = get_questions(quiz_id)
        random.shuffle(self.questions)  # Randomize the order of questions
        self.current_index = 0
        self.score = 0
        self.user_answers = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Take Quiz')
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.question_label = QLabel()
        layout.addWidget(self.question_label)

        self.answer_group = QButtonGroup(self)
        self.true_button = QRadioButton('True')
        self.false_button = QRadioButton('False')
        self.answer_group.addButton(self.true_button)
        self.answer_group.addButton(self.false_button)

        layout.addWidget(self.true_button)
        layout.addWidget(self.false_button)

        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_question)
        layout.addWidget(self.next_button)

        self.setLayout(layout)
        self.update_question()

    def update_question(self):
        if self.current_index < len(self.questions):
            self.question_label.setText(f"Question {self.current_index + 1}")
            self.true_button.setChecked(False)
            self.false_button.setChecked(False)
        else:
            self.finish_quiz()

    def next_question(self):
        if self.answer_group.checkedButton():
            user_answer = self.true_button.isChecked()
            self.user_answers.append(user_answer)
            correct_answer = self.questions[self.current_index]['answer']
            if user_answer == correct_answer:
                self.score += 1
            self.current_index += 1
            self.update_question()
        else:
            QMessageBox.warning(self, 'No Answer', 'Please select an answer before proceeding.')

    def finish_quiz(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_score(self.quiz_id, self.score, len(self.questions), date)
        
        result_message = f'Your score: {self.score}/{len(self.questions)}\n\n'
        for i, (question, user_answer) in enumerate(zip(self.questions, self.user_answers)):
            result_message += f"Q{i+1}: {'Correct' if user_answer == question['answer'] else 'Incorrect'}\n"
            result_message += f"Your answer: {'True' if user_answer else 'False'}\n"
            result_message += f"Correct answer: {'True' if question['answer'] else 'False'}\n"
            result_message += f"Question: {question['question']}\n\n"
        
        QMessageBox.information(self, 'Quiz Finished', result_message)
        self.close()

class EditQuizDialog(QDialog):
    def __init__(self, quiz_id):
        super().__init__()
        self.quiz_id = quiz_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Edit Quiz')
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.quiz_title_edit = QLineEdit()
        quiz_title = [quiz['title'] for quiz in get_quizzes() if quiz['id'] == self.quiz_id][0]
        self.quiz_title_edit.setText(quiz_title)
        layout.addWidget(QLabel('Quiz Title'))
        layout.addWidget(self.quiz_title_edit)

        self.questions_list = QListWidget()
        layout.addWidget(self.questions_list)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add Question")
        add_button.clicked.connect(self.add_question)
        buttons_layout.addWidget(add_button)

        edit_button = QPushButton("Edit Question")
        edit_button.clicked.connect(self.edit_question)
        buttons_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete Question")
        delete_button.clicked.connect(self.delete_question)
        buttons_layout.addWidget(delete_button)

        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.update_questions_list()

    def update_questions_list(self):
        self.questions_list.clear()
        self.questions = get_questions(self.quiz_id)
        for question in self.questions:
            item_text = f"{question['question']} - Answer: {'True' if question['answer'] else 'False'}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, question['id'])
            self.questions_list.addItem(item)

    def add_question(self):
        question, ok = QInputDialog.getText(self, 'Add Question', 'Enter question text:')
        if ok and question:
            answer, ok = QInputDialog.getItem(self, 'Add Question', 'Select the correct answer:', ['True', 'False'], 0, False)
            if ok:
                add_question(self.quiz_id, question, answer == 'True')
                self.update_questions_list()

    def edit_question(self):
        current_item = self.questions_list.currentItem()
        if current_item:
            question_id = current_item.data(Qt.ItemDataRole.UserRole)
            question = next((q for q in self.questions if q['id'] == question_id), None)
            if question:
                new_text, ok = QInputDialog.getText(self, 'Edit Question', 'Enter new question text:', text=question['question'])
                if ok and new_text:
                    new_answer, ok = QInputDialog.getItem(self, 'Edit Question', 'Select the correct answer:', 
                                                          ['True', 'False'], 0 if question['answer'] else 1, False)
                    if ok:
                        update_question(question_id, new_text, new_answer == 'True')
                        self.update_questions_list()

    def delete_question(self):
        current_item = self.questions_list.currentItem()
        if current_item:
            question_id = current_item.data(Qt.ItemDataRole.UserRole)
            confirm = QMessageBox.question(self, 'Confirm Deletion', 
                                           'Are you sure you want to delete this question?',
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                delete_question(question_id)
                self.update_questions_list()

    def save_changes(self):
        new_title = self.quiz_title_edit.text()
        update_quiz(self.quiz_id, new_title)
        self.accept()

class EditQuizDialog(QDialog):
    def __init__(self, quiz_id):
        super().__init__()
        self.quiz_id = quiz_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Edit Quiz')
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.quiz_title_edit = QLineEdit()
        quiz_title = [quiz['title'] for quiz in get_quizzes() if quiz['id'] == self.quiz_id][0]
        self.quiz_title_edit.setText(quiz_title)
        layout.addWidget(QLabel('Quiz Title'))
        layout.addWidget(self.quiz_title_edit)

        self.questions_list = QListWidget()
        layout.addWidget(self.questions_list)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add Question")
        add_button.clicked.connect(self.add_question)
        buttons_layout.addWidget(add_button)

        edit_button = QPushButton("Edit Question")
        edit_button.clicked.connect(self.edit_question)
        buttons_layout.addWidget(edit_button)

        delete_button = QPushButton("Delete Question")
        delete_button.clicked.connect(self.delete_question)
        buttons_layout.addWidget(delete_button)

        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        self.update_questions_list()

    def update_questions_list(self):
        self.questions_list.clear()
        self.questions = get_questions(self.quiz_id)
        for question in self.questions:
            item_text = f"{question['question']} - Answer: {'True' if question['answer'] else 'False'}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, question['id'])
            self.questions_list.addItem(item)

    def add_question(self):
        question, ok = QInputDialog.getText(self, 'Add Question', 'Enter question text:')
        if ok and question:
            answer, ok = QInputDialog.getItem(self, 'Add Question', 'Select the correct answer:', ['True', 'False'], 0, False)
            if ok:
                add_question(self.quiz_id, question, answer == 'True')
                self.update_questions_list()

    def edit_question(self):
        current_item = self.questions_list.currentItem()
        if current_item:
            question_id = current_item.data(Qt.ItemDataRole.UserRole)
            question = next((q for q in self.questions if q['id'] == question_id), None)
            if question:
                new_text, ok = QInputDialog.getText(self, 'Edit Question', 'Enter new question text:', text=question['question'])
                if ok and new_text:
                    new_answer, ok = QInputDialog.getItem(self, 'Edit Question', 'Select the correct answer:', 
                                                          ['True', 'False'], 0 if question['answer'] else 1, False)
                    if ok:
                        update_question(question_id, new_text, new_answer == 'True')
                        self.update_questions_list()

    def delete_question(self):
        current_item = self.questions_list.currentItem()
        if current_item:
            question_id = current_item.data(Qt.ItemDataRole.UserRole)
            confirm = QMessageBox.question(self, 'Confirm Deletion', 
                                           'Are you sure you want to delete this question?',
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                delete_question(question_id)
                self.update_questions_list()

    def save_changes(self):
        new_title = self.quiz_title_edit.text()
        update_quiz(self.quiz_id, new_title)
        
        # We don't need to save questions here as they are saved immediately when edited
        self.accept()

class ScoreWindow(QWidget):
    def __init__(self, quiz_id):
        super().__init__()
        self.quiz_id = quiz_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Quiz Scores')
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.score_list = QListWidget()
        scores = get_scores(self.quiz_id)
        if not scores:
            self.score_list.addItem("No scores available for this quiz.")
        else:
            for score in scores:
                score_text = f"Score: {score.get('score', 'N/A')}/{score.get('total_questions', 'N/A')}, Date: {score.get('date', 'N/A')}"
                self.score_list.addItem(score_text)

        layout.addWidget(self.score_list)
        self.setLayout(layout)

if __name__ == '__main__':
    print("Starting the application...")
    app = QApplication(sys.argv)
    print("QApplication created")
    
    if is_dark_mode():
        print("Dark mode detected, setting dark palette")
        set_dark_mode_palette(app)
    else:
        print("Light mode detected")
    
    print("Initializing database...")
    initialize_database()
    print("Database initialized")
    
    print("Creating QuizApp instance...")
    quiz_app = QuizApp()
    print("QuizApp instance created")
    
    print("Showing QuizApp window...")
    quiz_app.show()
    print("QuizApp window should be visible now")
    
    print("Entering Qt event loop...")
    sys.exit(app.exec())