from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout

def on_click():
    label.setText("Button Clicked!")

app = QApplication([])
window = QWidget()
window.setWindowTitle('Sample App')

layout = QVBoxLayout()

label = QLabel('Hello, PyQt!')
layout.addWidget(label)

button = QPushButton('Click Me')
button.clicked.connect(on_click)
layout.addWidget(button)

window.setLayout(layout)
window.show()
app.exec_()