import os
import sys
from PyQt4.QtGui import *
from PyQt4 import QtCore

import module.launcher
import PostProcessingModule.menu


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


class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        wid = QWidget()
        self.setCentralWidget(wid)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        menubar = self.menuBar()
        menuMenu = menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Buttons of two options
        generateBtn = QPushButton("Generate input NEXUS file for PhyloNet", self)
        postProcessBtn = QPushButton("Display results of PhyloNet commands", self)
        generateBtn.setMinimumWidth(400)

        generateBtn.clicked.connect(self.openModule)
        postProcessBtn.clicked.connect(self.openPostProcess)

        # Image and Title
        pix = QPixmap(resource_path("logo.png"))
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
        top.addStretch()
        top.addWidget(image)
        top.addWidget(lbl)
        top.addStretch()

        # Main vertical layout.
        vbox = QVBoxLayout()
        vbox.addLayout(top)
        vbox.addWidget(line)
        vbox.addWidget(generateBtn)
        vbox.addWidget(postProcessBtn)
        wid.setLayout(vbox)

        vbox.setContentsMargins(50, 10, 50, 10)

        menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetCompanion')
        self.setWindowIcon(QIcon(resource_path("logo.png")))

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

    def openModule(self):
        self.nexGenerator = module.launcher.Launcher()
        self.nexGenerator.show()
        self.close()

    def openPostProcess(self):
        self.outputSummarizer = PostProcessingModule.menu.MenuPage()
        self.outputSummarizer.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
