import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from gui import QuizApp
from database import initialize_database

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def setup_logging():
    log_file = os.path.join(os.path.expanduser('~'), 'quiz_app.log')
    logging.basicConfig(filename=log_file, level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    initialize_database()
    app = QApplication(sys.argv)
    
    # Load and apply the QSS stylesheet
    qss_path = resource_path("assets/windows11_style.qss")
    try:
        with open(qss_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        logging.error(f"Stylesheet not found at {qss_path}")
        print("Stylesheet not found, continuing without it.")
    
    quiz_app = QuizApp()
    quiz_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    setup_logging()
    try:
        main()
    except Exception as e:
        logging.exception("An unhandled exception occurred:")
        print(f"An error occurred: {e}")
        print("Please check the log file for more details.")