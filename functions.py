import sys
import os
import re
import subprocess

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtLocation
from PyQt5.QtGui import QIcon, QPixmap

def titleHeader(commandName):
    """
    Creates header label for phylonet command name
    """
    titleLabel = QLabel(commandName)
    titleLabel.setObjectName("titleLabel")

    return titleLabel
def instructionLabel(name):
    """
    Creates a label denoting the type of instruction on a page
    """
    instructionLbl = QLabel(name)
    instructionLbl.setObjectName("instructionLabel")

    return instructionLbl

def getInfoButton(self, dpi):
    """
    Returns a button, which when clicked introduces PhyloNet
    """
    #initialize button
    ico = QIcon("info.svg")
    infoButton = QPushButton(self)
    infoButton.setIcon(ico)
    infoButton.setObjectName("infoButton")

    # Set DPI dependent styles
    # awkward but necessary since PYQT5 offers no smooth scaling option
    if dpi <150:
        infoButton.setFixedSize(40,40)
    elif dpi < 200:
        infoButton.setFixedSize(52,52)
    else:
        infoButton.setFixedSize(64,64)

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

def resource_path(relative_path):
    """
    Refer to the location of a file at run-time.
    This function is from
    https://www.reddit.com/r/learnpython/comments/4kjie3/how_to_include_gui_images_with_pyinstaller/
    For more information, visit https://pythonhosted.org/PyInstaller/runtime-information.html#run-time-information
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def validateFile(self, filePath):
    """
    After the .nexus file is generated, validate the file by feeding it to PhyloNet.
    Specify -checkParams on command line to make sure PhyloNet checks input without executing the command.
    """
  
    try:
        subprocess.check_output(
            ["java", "-jar", resource_path("module/testphylonet.jar"),
                filePath, "checkParams"], stderr=subprocess.STDOUT)
        return True
    except subprocess.CalledProcessError as e:
        # If an error is encountered, delete the generated file and display the error to user.
        msg = e.output.decode("utf-8")
        msg = msg.replace("\n", "", 1)
        msg = re.sub(" at \\[[0-9]+,[0-9]+\\]", "", msg)
        os.remove(filePath)
        QMessageBox.warning(self, "Warning", msg, QMessageBox.Ok)
        return False