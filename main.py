import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui,QtWidgets, QtCore, QtLocation
from PyQt5.QtGui import QIcon, QPixmap

import module.launcher

from styling import *
from functions import *


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        self.setWindowTitle("Phylonet")
        self.setWindowIcon(QIcon("imgs/logo.png"))
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint
                                      | QtCore.Qt.WindowMinimizeButtonHint)
        self.setWindowFlags(flags)

        wid = QWidget()
        self.setCentralWidget(wid)
        self.setContentsMargins(50, 0, 10, 50)

        # Buttons of two options
        generateBtn = QPushButton(
            "Generate input NEXUS file for PhyloNet", self)
        generateBtn.setObjectName("inputBtn")
        generateBtn.clicked.connect(self.openModule)

        # Question
        header = QLabel()
        pix = QIcon("imgs/header.svg").pixmap(QtCore.QSize(500,87))
        header.setPixmap(pix)

        questionLabel = QLabel("What would you like to do?")
        questionLabel.setObjectName("introQuestion")

        version = QLabel("Version 1.0")
        version.setObjectName("version")

        # main layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(header, alignment=QtCore.Qt.AlignCenter)
        mainLayout.addWidget(generateBtn, alignment=QtCore.Qt.AlignCenter)
        mainLayout.setContentsMargins(250, 20, 250, 10)

        # houses all widgets
        vbox = QVBoxLayout()
        vbox.addWidget(getInfoButton(self))
        vbox.addLayout(mainLayout)
        vbox.addWidget(version, alignment=QtCore.Qt.AlignCenter)
        wid.setLayout(vbox)

        # menubar.setNativeMenuBar(False)
        # self.setWindowTitle('PhyloNetCompanion')
        # self.setWindowIcon(QIcon(resource_path("imgs/logo.png")))

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    def aboutMessage(self):
        msg = QDialog()
        msg.setWindowTitle("Phylonet")
        msg.setWindowIcon(QIcon("imgs/logo.png"))
        flags = QtCore.Qt.WindowFlags(
            QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        msg.setWindowFlags(flags)
        msg.setObjectName("aboutMessage")

        vbox = QVBoxLayout()
        text = QLabel("PhyloNet is a tool designed mainly for analyzing, "
                      "reconstructing, and evaluating reticulate "
                      "(or non-treelike) evolutionary relationships, "
                      "generally known as phylogenetic networks. Various "
                      "methods that we have developed make use of techniques "
                      "and tools from the domain of phylogenetic trees, and "
                      "hence the PhyloNet package includes several tools for "
                      "phylogenetic tree analysis. PhyloNet is released under "
                      "the GNU General Public License. \n\nPhyloNet is designed, "
                      "implemented, and maintained by Rice's BioInformatics Group, "
                      "which is lead by Professor Luay Nakhleh (nakhleh@cs.rice.edu). ")
        text.setWordWrap(True)
        text.setStyleSheet("padding: 60px 100px 10px 100px;")
        text.setObjectName("infoButton")

        hyperlink = QLabel()
        hyperlink.setText('For more details related to this group please visit '
                          '<a href="http://bioinfo.cs.rice.edu">'
                          'http://bioinfo.cs.rice.edu</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("infoButton")
        hyperlink.setStyleSheet("padding: 10px 100px 80px 100px;")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(msg.accept)
        vbox.addWidget(text)
        vbox.addWidget(hyperlink)
        vbox.addWidget(buttonBox)
        msg.setLayout(vbox)
        msg.exec_()

    def openModule(self):
        self.nexGenerator = module.launcher.Launcher()
        self.nexGenerator.show()
        # Closes main window so its cleaner for user
        self.window().setVisible(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyleSheet(style())
    app.setWindowIcon(QtGui.QIcon('imgs/logo.ico'))
    app.setStyle(QStyleFactory.create('Fusion'))

    font = QFont("Arial", 10, 1, False)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    
    ex = Main()
    ex.show()
    sys.exit(app.exec_())