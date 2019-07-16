import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import dendropy


class ParamListDlg(QDialog):
    """
    The dialog for setting general time-reversible model.
    Input a dictionary, whose keys are A, C, G, T,
    A>C, A>G, A>T, C>G, C>T and G>T, and values are values
    for these parameters. Both key and value should be string.
    """
    def __init__(self, currentList, parent=None):
        super(ParamListDlg, self).__init__(parent)

        # Current model
        self.paramList = currentList.copy()

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # Labels and inputs
        # Default values for parameters are passed
        # in by caller
        self.freqALbl = QLabel("Base frequency for A:")
        self.freqCLbl = QLabel("Base frequency for C:")
        self.freqGLbl = QLabel("Base frequency for G:")
        self.freqTLbl = QLabel("Base frequency for T:")

        self.transACLbl = QLabel("Transition probability for A > C:")
        self.transAGLbl = QLabel("Transition probability for A > G:")
        self.transATLbl = QLabel("Transition probability for A > T:")
        self.transCGLbl = QLabel("Transition probability for C > G:")
        self.transCTLbl = QLabel("Transition probability for C > T:")
        self.transGTLbl = QLabel("Transition probability for G > T:")

        self.freqAEdit = QLineEdit(self.paramList["A"])
        self.freqCEdit = QLineEdit(self.paramList["C"])
        self.freqGEdit = QLineEdit(self.paramList["G"])
        self.freqTEdit = QLineEdit(self.paramList["T"])

        self.transACEDit = QLineEdit(self.paramList["AC"])
        self.transAGEDit = QLineEdit(self.paramList["AG"])
        self.transATEDit = QLineEdit(self.paramList["AT"])
        self.transCGEDit = QLineEdit(self.paramList["CG"])
        self.transCTEDit = QLineEdit(self.paramList["CT"])
        self.transGTEDit = QLineEdit(self.paramList["GT"])

        # Labels and inputs layout
        freqALayout = QHBoxLayout()
        freqALayout.addWidget(self.freqALbl)
        freqALayout.addStretch(1)
        freqALayout.addWidget(self.freqAEdit)

        freqCLayout = QHBoxLayout()
        freqCLayout.addWidget(self.freqCLbl)
        freqCLayout.addStretch(1)
        freqCLayout.addWidget(self.freqCEdit)

        freqGLayout = QHBoxLayout()
        freqGLayout.addWidget(self.freqGLbl)
        freqGLayout.addStretch(1)
        freqGLayout.addWidget(self.freqGEdit)

        freqTLayout = QHBoxLayout()
        freqTLayout.addWidget(self.freqTLbl)
        freqTLayout.addStretch(1)
        freqTLayout.addWidget(self.freqTEdit)

        transACLayout = QHBoxLayout()
        transACLayout.addWidget(self.transACLbl)
        transACLayout.addStretch(1)
        transACLayout.addWidget(self.transACEDit)

        transAGLayout = QHBoxLayout()
        transAGLayout.addWidget(self.transAGLbl)
        transAGLayout.addStretch(1)
        transAGLayout.addWidget(self.transAGEDit)

        transATLayout = QHBoxLayout()
        transATLayout.addWidget(self.transATLbl)
        transATLayout.addStretch(1)
        transATLayout.addWidget(self.transATEDit)

        transCGLayout = QHBoxLayout()
        transCGLayout.addWidget(self.transCGLbl)
        transCGLayout.addStretch(1)
        transCGLayout.addWidget(self.transCGEDit)

        transCTLayout = QHBoxLayout()
        transCTLayout.addWidget(self.transCTLbl)
        transCTLayout.addStretch(1)
        transCTLayout.addWidget(self.transCTEDit)

        transGTLayout = QHBoxLayout()
        transGTLayout.addWidget(self.transGTLbl)
        transGTLayout.addStretch(1)
        transGTLayout.addWidget(self.transGTEDit)

        # Buttons
        cancel = QPushButton("Cancel")
        set = QPushButton("Set")
        set.setDefault(True)
        set.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(cancel)
        btnLayout.addWidget(set)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addLayout(freqALayout)
        topLevelLayout.addLayout(freqCLayout)
        topLevelLayout.addLayout(freqGLayout)
        topLevelLayout.addLayout(freqTLayout)
        topLevelLayout.addLayout(transACLayout)
        topLevelLayout.addLayout(transAGLayout)
        topLevelLayout.addLayout(transATLayout)
        topLevelLayout.addLayout(transCGLayout)
        topLevelLayout.addLayout(transCTLayout)
        topLevelLayout.addLayout(transGTLayout)
        topLevelLayout.addLayout(btnLayout)

        self.setLayout(topLevelLayout)

    def accept(self):
        """
        When user clicks "Set", update the internal parameter list based on what user
        enters in GUI.
        Throws an exception and diplay a warning if not all parameters are entered.
        """
        class emptyInputError(Exception):
            pass

        try:
            if self.freqAEdit.text() == "":
                raise emptyInputError
            else:
                self.paramList["A"] = str(self.freqAEdit.text())

            if self.freqCEdit.text() == "":
                raise emptyInputError
            else:
                self.paramList["C"] = str(self.freqCEdit.text())

            if self.freqGEdit.text() == "":
                raise emptyInputError
            else:
                self.paramList["G"] = str(self.freqGEdit.text())

            if self.freqTEdit.text() == "":
                raise emptyInputError
            else:
                self.paramList["T"] = str(self.freqTEdit.text())

            if self.transACEDit.text() == "":
                raise emptyInputError
            else:
                self.paramList["AC"] = str(self.transACEDit.text())

            if self.transAGEDit.text() == "":
                raise emptyInputError
            else:
                self.paramList["AG"] = str(self.transAGEDit.text())

            if self.transATEDit.text() == "":
                raise emptyInputError
            else:
                self.paramList["AT"] = str(self.transATEDit.text())

            if self.transCGEDit.text() == "":
                raise emptyInputError
            else:
                self.paramList["CG"] = str(self.transCGEDit.text())

            if self.transCTEDit.text() == "":
                raise emptyInputError
            else:
                self.paramList["CT"] = str(self.transCTEDit.text())

            if self.transGTEDit.text() == "":
                raise emptyInputError
            else:
                self.paramList["GT"] = str(self.transGTEDit.text())

            QDialog.accept(self)
        except emptyInputError:
            QMessageBox.warning(self, "Warning", "Please provide all parameters.", QMessageBox.Ok)

    def getParamList(self):
        """
        Return the current parameter list to caller.
        """
        return self.paramList


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mapping = {"A": None, "C": None, "G": None, "T": None, "AC": None, "AG": None, "AT": None, "CG": None, "CT": None,
               "GT": None}
    ex = ParamListDlg(mapping, parent=None)
    ex.show()
    sys.exit(app.exec_())
