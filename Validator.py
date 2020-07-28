import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

class NumValidator(QtGui.QIntValidator):
    """
    Enforce integer inputs
    """
    def validate(self, string, index):
        if len(string) == 0:
            state = QtGui.QValidator.Intermediate
        elif not string.isnumeric():
            state = QtGui.QValidator.Invalid 
        else:
            state = QtGui.QValidator.Acceptable
        return (state, string, index)

