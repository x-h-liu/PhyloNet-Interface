import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from module import TreeMethodsPage
from module import MCMCSEQ


def resource_path(relative_path):
    """
    Refer to the location of a file at run-time.
    This function is from
    https://www.reddit.com/r/learnpython/comments/4kjie3/how_to_include_gui_images_with_pyinstaller/
    #run-time-information
    For more information, visit https://pythonhosted.org/PyInstaller/runtime-information.html
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class SecondPage(QWizardPage):
    def __init__(self):
        super(SecondPage, self).__init__()

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # wid = QWidget()
        # self.setCentralWidget(wid)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        self.menubar = QMenuBar(self)
        menuMenu = self.menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Queston label and two options
        questionLabel = QLabel()
        questionLabel.setText(
            "Do you want direct inference or two-step inference using gene tree estimates?")
        questionLabel.setWordWrap(True)

        questionFont = QFont()
        questionFont.setPointSize(24)
        questionFont.setFamily("Copperplate")
        questionLabel.setFont(questionFont)  # Font of the question label.

        # Buttons of two options
        directBtn = QPushButton("Direct inference", self)
        geneTreeBtn = QPushButton("Using gene tree estimates", self)

        directBtn.clicked.connect(self.openMCMC)
        geneTreeBtn.clicked.connect(self.openTreePage)

        # Image and Title
        pix = QPixmap(resource_path("imgs/logo.png"))
        image = QLabel(self)
        image.setPixmap(pix)
        lbl = QLabel("PhyloNet")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setBold(True)
        lbl.setFont(titleFont)  # Font of the PhyloNet title.

        # Separation line
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        # Layouts
        # Top level logo and title.
        top = QHBoxLayout()
        top.addWidget(image)
        top.addWidget(lbl)

        # Button layout
        buttonBox = QHBoxLayout()
        buttonBox.addWidget(directBtn)
        buttonBox.addWidget(geneTreeBtn)

        # Main vertical layout.
        vbox = QVBoxLayout()
        vbox.addLayout(top)
        vbox.addWidget(line)
        vbox.addWidget(questionLabel)
        vbox.addSpacing(20)
        vbox.addLayout(buttonBox)
        self.setLayout(vbox)

        vbox.setContentsMargins(50, 10, 50, 10)

        self.menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("imgs/logo.png"))) """

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
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

    def openTreePage(self):
        """
        Open the page for selecting a tree-based method.
        """
        self.treePage = TreeMethodsPage.TreeMethodsPage()
        self.treePage.show()
        self.close()

    def openMCMC(self):
        """
        Open the page for MCMC_SEQ command.
        """
        self.MCMCPage = MCMCSEQ.MCMCSEQPage()
        self.MCMCPage.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SecondPage()
    ex.show()
    sys.exit(app.exec_())
