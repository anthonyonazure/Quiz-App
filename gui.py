from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QInputDialog, QListWidget, QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox
from PyQt6.QtCore import Qt
import sys
import random
import datetime
from quiz_manager import add_quiz, add_question, get_quizzes, get_questions, remove_quiz, update_quiz, update_question, add_score, get_scores

class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QListWidget {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #555555;
            }
        """)
        
        self.setWindowTitle('Quiz App')
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()

        self.quiz_list = QListWidget()
        quizzes = get_quizzes()
        self.quiz_list.addItems([quiz[1] for quiz in quizzes])
        layout.addWidget(self.quiz_list)

        self.start_button = QPushButton('Start Quiz')
        self.start_button.clicked.connect(self.start_quiz)
        layout.addWidget(self.start_button)

        self.create_button = QPushButton('Create Quiz')
        self.create_button.clicked.connect(self.create_quiz)
        layout.addWidget(self.create_button)

        self.edit_button = QPushButton('Edit Quiz')
        self.edit_button.clicked.connect(self.edit_quiz)
        layout.addWidget(self.edit_button)

        self.remove_button = QPushButton('Remove Quiz')
        self.remove_button.clicked.connect(self.remove_quiz)
        layout.addWidget(self.remove_button)

        self.view_scores_button = QPushButton('View Scores')
        self.view_scores_button.clicked.connect(self.view_scores)
        layout.addWidget(self.view_scores_button)

        self.setLayout(layout)

    def start_quiz(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz[0] for quiz in get_quizzes() if quiz[1] == quiz_title][0]
            self.quiz_window = QuizWindow(quiz_id)
            self.quiz_window.show()
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to start.')

    def create_quiz(self):
        text, ok = QInputDialog.getText(self, 'Create Quiz', 'Enter quiz title:')
        if ok and text:
            try:
                quiz_id = add_quiz(text)
                self.quiz_list.addItem(text)
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
            quiz_id = [quiz[0] for quiz in get_quizzes() if quiz[1] == quiz_title][0]
            self.edit_quiz_dialog = EditQuizDialog(quiz_id)
            self.edit_quiz_dialog.exec()
            self.quiz_list.clear()
            self.quiz_list.addItems([quiz[1] for quiz in get_quizzes()])
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to edit.')

    def remove_quiz(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz[0] for quiz in get_quizzes() if quiz[1] == quiz_title][0]
            remove_quiz(quiz_id)
            self.quiz_list.takeItem(self.quiz_list.row(selected_quiz))
            QMessageBox.information(self, 'Quiz Removed', f'Quiz "{quiz_title}" has been removed.')
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to remove.')

    def view_scores(self):
        selected_quiz = self.quiz_list.currentItem()
        if selected_quiz:
            quiz_title = selected_quiz.text()
            quiz_id = [quiz[0] for quiz in get_quizzes() if quiz[1] == quiz_title][0]
            self.score_window = ScoreWindow(quiz_id)
            self.score_window.show()
        else:
            QMessageBox.warning(self, 'No Quiz Selected', 'Please select a quiz to view scores.')

class QuizWindow(QWidget):
    def __init__(self, quiz_id):
        super().__init__()
        self.quiz_id = quiz_id
        self.questions = get_questions(quiz_id)
        random.shuffle(self.questions)
        self.current_index = 0
        self.score = 0
        self.questions_answered = 0
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Take Quiz')
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()
        self.question_label = QLabel(f'Question {self.current_index + 1}')
        self.layout.addWidget(self.question_label)
        self.true_button = QPushButton('True')
        self.true_button.clicked.connect(lambda: self.answer_question(True))
        self.layout.addWidget(self.true_button)
        self.false_button = QPushButton('False')
        self.false_button.clicked.connect(lambda: self.answer_question(False))
        self.layout.addWidget(self.false_button)
        self.submit_button = QPushButton('Submit Quiz')
        self.submit_button.clicked.connect(self.finish_quiz)
        self.layout.addWidget(self.submit_button)
        self.setLayout(self.layout)
        self.update_question()

    def update_question(self):
        if self.current_index < len(self.questions):
            self.question_label.setText(self.questions[self.current_index][2])
        else:
            self.finish_quiz()

    def answer_question(self, answer):
        if self.current_index < len(self.questions):
            correct_answer = self.questions[self.current_index][3]
            if answer == correct_answer:
                self.score += 1
            self.questions_answered += 1
            self.current_index += 1
            self.update_question()

    def finish_quiz(self):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_score(self.quiz_id, self.score, self.questions_answered, date)
        QMessageBox.information(self, 'Quiz Finished', f'Your score: {self.score}/{self.questions_answered}')
        self.close()

class EditQuizDialog(QDialog):
    def __init__(self, quiz_id):
        super().__init__()
        self.quiz_id = quiz_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Edit Quiz')
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        self.quiz_title_edit = QLineEdit()
        quiz_title = [quiz[1] for quiz in get_quizzes() if quiz[0] == self.quiz_id][0]
        self.quiz_title_edit.setText(quiz_title)
        layout.addWidget(QLabel('Quiz Title'))
        layout.addWidget(self.quiz_title_edit)

        self.questions_layout = QVBoxLayout()
        self.questions = get_questions(self.quiz_id)
        self.question_widgets = []

        for question in self.questions:
            question_layout = QFormLayout()
            question_text = QLineEdit(question[2])
            answer_combo = QComboBox()
            answer_combo.addItems(['True', 'False'])
            answer_combo.setCurrentText('True' if question[3] else 'False')
            question_layout.addRow(QLabel('Question'), question_text)
            question_layout.addRow(QLabel('Answer'), answer_combo)
            self.questions_layout.addLayout(question_layout)
            self.question_widgets.append((question[0], question_text, answer_combo))

        layout.addLayout(self.questions_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save_changes)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_changes(self):
        new_title = self.quiz_title_edit.text()
        update_quiz(self.quiz_id, new_title)

        for question_id, question_text, answer_combo in self.question_widgets:
            new_question_text = question_text.text()
            new_answer = answer_combo.currentText() == 'True'
            update_question(question_id, new_question_text, new_answer)

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
        for score in scores:
            score_text = f"Score: {score[2]}/{score[3]}, Date: {score[4]}"
            self.score_list.addItem(score_text)

        layout.addWidget(self.score_list)
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    quiz_app = QuizApp()
    quiz_app.show()
    sys.exit(app.exec())