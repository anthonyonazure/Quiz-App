import sys
import os
from PyQt6.QtWidgets import QApplication
from database import initialize_database
from gui import QuizApp

def resource_path(relative_path):
    print("Entering resource_path function")
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    print(f"Resource path: {os.path.join(base_path, relative_path)}")
    return os.path.join(base_path, relative_path)

def main():
    initialize_database()
    print("Starting main function")
    app = QApplication(sys.argv)
    print("QApplication created")
    
    qss_path = resource_path("assets/windows11_style.qss")
    print(f"QSS path: {qss_path}")
    try:
        with open(qss_path, "r") as style_file:
            app.setStyleSheet(style_file.read())
        print("Stylesheet applied successfully")
    except FileNotFoundError:
        print("Stylesheet not found, continuing without it.")
    
    print("Creating QuizApp instance")
    quiz_app = QuizApp()
    print("Showing QuizApp")
    quiz_app.show()
    print("Entering main event loop")
    sys.exit(app.exec())

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("Press Enter to exit...")