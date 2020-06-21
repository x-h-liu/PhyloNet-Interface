from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtLocation
from PyQt5.QtGui import QIcon, QPixmap

# Creates header label for command name


def titleHeader(commandName):
    titleLabel = QLabel()
    titleLabel.setObjectName("titleLabel")
    titleLabel.setText(commandName)

    return titleLabel

#


def lineSeparator(self):
    line = QFrame(self)
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setObjectName("line")
    return line

# Container for setting options


def optionFrame(optionLayout):
    optionFrame = QFrame()
    optionFrame.setObjectName("optionFrame")
    optionFrame.setLayout(optionLayout)

    return optionFrame


def getInfoButton(self):
    infoButton = QPushButton("i", self)
    infoButton.setObjectName("infoButton")
    infoButton.clicked.connect(self.aboutMessage)

    return infoButton
