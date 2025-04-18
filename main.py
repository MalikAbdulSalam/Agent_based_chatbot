import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent

import multi_agentic_chatbot as chat_bot  # Make sure this module exists


# Custom Clickable QLabel
class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        # Load UI
        try:
            uic.loadUi('resources/chatbot.ui', self)
        except Exception as e:
            print(f"Error loading UI file: {e}")
            sys.exit(1)

        # Flags
        self.options_visible = False

        # Hide toggleable labels on start
        self.toggle_labels = [self.label, self.label_2, self.label_3, self.label_4, self.label_5, 
                              self.label_6, self.label_7, self.label_8, self.label_9, self.label_10, self.label_11]
        for lbl in self.toggle_labels:
            lbl.setVisible(False)

        # Connect Enter key to run chatbot
        self.user_prompt_txtedit.keyPressEvent = self.handle_key_press

        # Run chatbot on label click
        self.search_lbl.mousePressEvent = lambda event: self.call_llm()

        # Toggle options on label click
        self.options_lbl.mousePressEvent = lambda event: self.toggle_options_visibility()

        # Wrap response label text
        self.response_lbl.setWordWrap(True)

        # Set initial model name
        self.current_model_lbl.setText("🟢 Gemma2-9b-It")

        # Update model on label clicks
        self.label.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Qwen-Qwq-32b")
        self.label_2.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Deepseek-R1-Distill-Llama-70b")
        self.label_3.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Gemma2-9b-It")
        self.label_4.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Compund-Beta-Mini")
        self.label_5.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Compound-Beta")
        self.label_6.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Llama-3.3-70b-Versatile")
        self.label_7.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Llama-3.1-8b-instant")
        self.label_8.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Llama3-70b-8192")
        self.label_9.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Llama3-8b-8192")
        self.label_10.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Meta-Llama/Llama-4-Scout-17b-16e-instruct")
        self.label_11.mousePressEvent = lambda event: self.current_model_lbl.setText("🟢 Meta-Llama/Llama-4-Maverick-17b-128e-insturct")

        self.show()

    def handle_key_press(self, event: QKeyEvent):
        """Handles key press events to trigger chatbot when Enter is pressed or insert new line with Shift+Enter"""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() == Qt.ShiftModifier:
                # Allow Shift+Enter to insert a new line in QTextEdit
                QtWidgets.QTextEdit.keyPressEvent(self.user_prompt_txtedit, event)
            else:
                # Run chatbot on Enter without Shift
                self.call_llm()
        else:
            # Allow other key presses (like typing)
            QtWidgets.QTextEdit.keyPressEvent(self.user_prompt_txtedit, event)

    def call_llm(self):
        """Runs the chatbot with the user input"""
        # Show buffering message while waiting
        # self.response_lbl.setText("Thinking... Please wait.")
        self.response_lbl.setText("🔍 Thinking Please wait..")

        QtWidgets.QApplication.processEvents()  # Force UI update

        # Get the user input
        user_prompt = self.user_prompt_txtedit.toPlainText().strip()

        if not user_prompt:
            return

        # Call chatbot function to get the response
        response_of_llm, tool_used  = chat_bot.run_chatbot(user_prompt)

        # Print tool usage log (optional for debugging)
        for entry in chat_bot.tool_usage_log:
            print(f"\nUser Asked     : {entry['user_input']}")
            print(f"Tool Used      : {entry['tool_used']}")
            print(f"Tool Input     : {entry['tool_input']}")
            print(f"Tool Output    : {entry['tool_output']}")
            print(f"AI Response    : {entry['ai_response']}")

        # Show response in the label
        self.response_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.response_lbl.setText(response_of_llm)
        self.tool_used_lbl.setText(tool_used)

    def toggle_options_visibility(self):
        """Toggles visibility of model selection labels"""
        self.options_visible = not self.options_visible
        
        # Show or hide labels based on the state
        for lbl in self.toggle_labels:
            lbl.setVisible(self.options_visible)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.setWindowTitle("Chat Bot")
    sys.exit(app.exec_())
