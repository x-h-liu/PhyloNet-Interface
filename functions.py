from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtLocation
from PyQt5.QtGui import QIcon, QPixmap


def titleHeader(commandName):
    """
    Creates header label for phylonet command name
    """
    titleLabel = QLabel()
    titleLabel.setObjectName("titleLabel")
    titleLabel.setText(commandName)

    return titleLabel

def getInfoButton(self):
    """
    Returns a button, which when clicked introduces PhyloNet
    """
    #initialize button
    ico = QIcon("info.svg")
    infoButton = QPushButton(self)
    infoButton.setIcon(ico)
    infoButton.setObjectName("infoButton")
    infoButton.setFixedSize(60,60)
    infoButton.setIconSize(infoButton.size())

    #connect button to message that introduces PhyloNet    
    infoButton.clicked.connect(self.aboutMessage)
    return infoButton

def successMessage(self):
    """
    Creates and launches success message if generate operation worked
    """
    #initialize message ui
    msg = QDialog()
    msg.setContentsMargins(100,100,100,10)
    msg.setWindowTitle("Phylonet") 
    msg.setWindowIcon(QIcon("imgs/logo.png"))
    flags = QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint )
    msg.setWindowFlags(flags)
    msg.setObjectName("successMessage")

    vbox = QVBoxLayout()
    #add image and button
    ico = QLabel()
    complete = QPixmap("imgs/complete.svg")
    ico.setPixmap(complete)
    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
    buttonBox.clicked.connect(msg.accept)

    vbox.addWidget(ico, alignment=QtCore.Qt.AlignCenter)
    vbox.addWidget(buttonBox, alignment=QtCore.Qt.AlignCenter)
    vbox.setSpacing(30)
 
    msg.setLayout(vbox)
    msg.setModal(1)
    #launch message
    msg.exec_()