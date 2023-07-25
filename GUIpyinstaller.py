import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog, QProgressBar, QPlainTextEdit, QComboBox, QLineEdit, QStyle, QWidget
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont
from PyQt5.QtCore import QProcess, Qt


class PyInstallerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyInstaller GUI")
        self.setWindowIcon(QIcon("pyinstaller_icon.png"))  # Set the icon, make sure the icon file is in the same folder
        self.setGeometry(100, 100, 900, 500)
        self.initUI()

    def initUI(self):
        # Set color scheme and font style
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))  # Set background color to white
        palette.setColor(QPalette.Text, QColor(0, 0, 0))  # Set text color to black
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))  # Set button text color to black
        palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)
        self.setFont(QFont('Arial', 10))

        self.file_path_label = QLabel('選擇文件：', self)
        self.file_path_label.move(20, 20)
        self.file_path_button = QPushButton('選擇文件', self)
        self.file_path_button.move(20, 50)

        self.file_path_line_edit = QLineEdit(self)
        self.file_path_line_edit.move(150, 55)
        self.file_path_line_edit.resize(200, 30)

        self.output_path_label = QLabel('輸出路徑：', self)
        self.output_path_label.move(20, 90)
        self.output_path_button = QPushButton('選擇路徑', self)
        self.output_path_button.move(20, 120)

        self.output_path_line_edit = QLineEdit(self)
        self.output_path_line_edit.move(150, 125)
        self.output_path_line_edit.resize(200, 30)

        self.icon_path_label = QLabel('選擇icon：', self)
        self.icon_path_label.move(20, 160)
        self.icon_path_button = QPushButton('選擇icon', self)
        self.icon_path_button.move(20, 190)

        self.icon_path_line_edit = QLineEdit(self)
        self.icon_path_line_edit.move(150, 195)
        self.icon_path_line_edit.resize(200, 30)

        self.package_mode_label = QLabel('打包方式：', self)
        self.package_mode_label.move(20, 230)
        self.package_mode_combo_box = QComboBox(self)
        self.package_mode_combo_box.move(150, 230)
        self.package_mode_combo_box.addItem('One Directory')
        self.package_mode_combo_box.addItem('One File')

        self.interface_mode_label = QLabel('介面方式：', self)
        self.interface_mode_label.move(20, 270)
        self.interface_mode_combo_box = QComboBox(self)
        self.interface_mode_combo_box.move(150, 270)
        self.interface_mode_combo_box.addItem('Console Based')
        self.interface_mode_combo_box.addItem('Window Based')

        self.progress_text_edit = QPlainTextEdit(self)
        self.progress_text_edit.move(400, 60)
        self.progress_text_edit.resize(460, 300)
        self.progress_text_edit.setReadOnly(True)

        self.progress_label = QLabel('目前進度：', self)
        self.progress_label.move(400, 20)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.move(400, 380)
        self.progress_bar.resize(515, 30)

        self.build_button = QPushButton('執行', self)
        self.build_button.move(400, 420)
        self.build_button.resize(460, 50)

        self.file_path_button.clicked.connect(self.get_file_path)
        self.output_path_button.clicked.connect(self.get_output_path)
        self.icon_path_button.clicked.connect(self.get_icon_path)
        self.build_button.clicked.connect(self.run_command)

    def get_file_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "Python Files (*.py)", options=options)
        if file_name:
            self.file_path_line_edit.setText(file_name)

    def get_output_path(self):
        dir_ = QFileDialog.getExistingDirectory(self, 'Select a directory')
        if dir_:
            self.output_path_line_edit.setText(dir_)

    def get_icon_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "Icon Files (*.ico)", options=options)
        if file_name:
            self.icon_path_line_edit.setText(file_name)

    def build_command(self):
        command = f'pyinstaller --noupx '
        if self.package_mode_combo_box.currentText() == 'One Directory':
            command += '--onedir '
        else:
            command += '--onefile '
        if self.interface_mode_combo_box.currentText() == 'Console Based':
            command += '--console '
        else:
            command += '--windowed '
        if self.icon_path_line_edit.text():
            command += f'--icon={self.icon_path_line_edit.text()} '
        command += f'--distpath={self.output_path_line_edit.text()} '
        command += f'{self.file_path_line_edit.text()}'
        return command

    def run_command(self):
        self.process = QProcess()

        # Connect the signal emitted during process execution.
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)  # new line

        self.build_button.setEnabled(False)  # Disable the button to avoid multiple runs.
        self.progress_bar.setRange(0, 0)  # Set the progress bar to 'busy' mode.
        self.progress_text_edit.setPlainText("執行中...")  # Display 'Running...' in the progress text box.

        command = self.build_command()
        self.process.start(command)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode().strip()
        self.progress_text_edit.appendPlainText(data)

    def handle_stderr(self):
        error = self.process.readAllStandardError().data().decode().strip()
        self.progress_text_edit.appendPlainText(error)

    # New function to handle process finish
    def process_finished(self):
        self.progress_text_edit.appendPlainText('finish')
        self.progress_bar.setRange(0, 1)  # Reset the progress bar.
        self.build_button.setEnabled(True)  # Enable the button after the process finish.


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create and show the application window
    window = PyInstallerGUI()
    window.show()

    # Run the main Qt loop
    sys.exit(app.exec())
