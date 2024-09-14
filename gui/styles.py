def button_style():
    return """
        QPushButton {
            background-color: #444444;
            color: white;
            border-radius: 10px;
            padding: 10px;
            border: 2px solid #555555;
        }
        QPushButton:disabled {
            background-color: #666666;
            color: #888888;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QPushButton:pressed {
            background-color: #333333;
        }
    """
