import sys
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtCore import QDir

class FileDialogHelper:
    def __init__(self, parent=None):
        self.parent = parent

    def getFilePath(self, title="Select a File", directory="", filter_="All Files (*);;"):
        file_dialog = QFileDialog(self.parent, title, directory, filter_)
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                return QDir.toNativeSeparators(selected_files[0])
        return None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fileDialogHelper = FileDialogHelper()
    file_path = fileDialogHelper.getFilePath()
    if file_path:
        print(f"Selected file path: {file_path}")
    else:
        print("No file selected.")
    sys.exit(app.exec_())