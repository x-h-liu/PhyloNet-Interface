import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtLocation
from PyQt5.QtGui import QIcon, QPixmap

import module.launcher
import PostProcessingModule.menu

from styling import *
from functions import *


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


class Main(QDialog):
    def __init__(self):
        super(Main, self).__init__()
        SM = SubMain()
        self.setWindowTitle("Phylonet") 
        self.setWindowIcon(QIcon("logo.png"))
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint 
                    | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(flags)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(SM)

        self.setLayout(mainLayout)


class SubMain(QMainWindow):
    def __init__(self):
        super(SubMain, self).__init__()
        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        wid = QWidget()
        self.setCentralWidget(wid)

        # Buttons of two options
        generateBtn = QPushButton(
            "Generate input NEXUS file for PhyloNet", self)
        postProcessBtn = QPushButton(
            "Display results of PhyloNet commands", self)

        generateBtn.clicked.connect(self.openModule)
        postProcessBtn.clicked.connect(self.openPostProcess)

        # Image and Title
        image = QLabel(self)
        pix = QPixmap(resource_path("PhyloNet-Interface/logo.png"))
        image.setPixmap(pix)
        self.resize(20, 10)
        image.setObjectName("image")

        phylonetLabel = QLabel("PhyloNet")
        phylonetLabel.setObjectName("phylonetLabel")

        # Separation line
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")

        # Layouts
        # Top level logo and title.
        top = QHBoxLayout()
        top.addStretch()
        top.addWidget(image)
        top.addWidget(phylonetLabel)
        top.addStretch()

        # Frame container for the top level layout
        topFrame = QFrame()
        topFrame.setObjectName("topFrame")
        topFrame.setLayout(top)

        # Middle level question
        questionLabel = QLabel()
        questionLabel.setObjectName("questionLabel")
        questionLabel.setText(
            "Welcome to PhyloNet. What would you like to do?")

        # Bottom level options
        hbox = QHBoxLayout()
        hbox.addWidget(generateBtn)
        hbox.addWidget(postProcessBtn)

        # Main vertical layout.
        vbox = QVBoxLayout()
        vbox.addWidget(getInfoButton(self))
        vbox.addWidget(topFrame)
        vbox.addWidget(line)
        vbox.addWidget(questionLabel)
        vbox.addLayout(hbox)
        wid.setLayout(vbox)

        vbox.setContentsMargins(50, 10, 50, 10)

    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("PhyloNet is a tool designed mainly for analyzing, "
                    "reconstructing, and evaluating reticulate "
                    "(or non-treelike) evolutionary relationships, "
                    "generally known as phylogenetic networks. Various "
                    "methods that we have developed make use of techniques "
                    "and tools from the domain of phylogenetic trees, and "
                    "hence the PhyloNet package includes several tools for "
                    "phylogenetic tree analysis. PhyloNet is released under "
                    "the GNU General Public License. \n\nPhyloNet is designed, "
                    "implemented, and maintained by Rice's BioInformatics Group, "
                    "which is lead by Professor Luay Nakhleh (nakhleh@cs.rice.edu). "
                    "For more details related to this group please visit "
                    "http://bioinfo.cs.rice.edu.")
        msg.exec_()

    def openModule(self):
        self.nexGenerator = module.launcher.Launcher()
        self.nexGenerator.show()
        #Closes main window so its cleaner for user
        self.window().setVisible(False)

    def openPostProcess(self):
        self.outputSummarizer = PostProcessingModule.menu.MenuPage()
        self.outputSummarizer.show()
        #same as above
        self.window().setVisible(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(style())
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
