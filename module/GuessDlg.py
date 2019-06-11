import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore


class GuessDlg(QDialog):
    """
    The dialog for user's specification on how to set species names.
    """
    def __init__(self, parent=None):
        super(GuessDlg, self).__init__(parent)

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # Texts
        shouldBeLabel = QLabel("Species names should be:")
        everythingLabel = QLabel("Everything")
        theLabel = QLabel("the")
        dotLabel = QLabel(".")

        font = QFont()
        font.setPointSize(18)
        shouldBeLabel.setFont(font)

        # Several guess options
        self.beforeAfter = QComboBox()
        self.beforeAfter.addItem("before")
        self.beforeAfter.addItem("after")

        self.firstLast = QComboBox()
        self.firstLast.addItem("first")
        self.firstLast.addItem("last")

        self.delimiter = QComboBox()
        self.delimiter.addItem("white space")
        self.delimiter.addItem("_")
        self.delimiter.addItem(".")

        # OK and Cancel buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept)

        # Layout
        sentenceLayout = QHBoxLayout()
        sentenceLayout.addWidget(everythingLabel)
        sentenceLayout.addWidget(self.beforeAfter)
        sentenceLayout.addWidget(theLabel)
        sentenceLayout.addWidget(self.firstLast)
        sentenceLayout.addWidget(self.delimiter)
        sentenceLayout.addWidget(dotLabel)

        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(shouldBeLabel)
        topLevelLayout.addLayout(sentenceLayout)
        topLevelLayout.addWidget(buttonBox)

        self.setLayout(topLevelLayout)

    def getInfo(self):
        """
        Return user's choice to caller.
        """
        info = (str(self.beforeAfter.currentText()), str(self.firstLast.currentText()),
                str(self.delimiter.currentText()))
        return info


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GuessDlg(parent=None)
    ex.show()
    sys.exit(app.exec_())
