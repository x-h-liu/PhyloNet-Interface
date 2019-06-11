import os
import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from module import SecondPage
from module import BiAllelicMethodsPage


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


class Launcher(QtWidgets.QMainWindow):
    def __init__(self):
        super(Launcher, self).__init__()

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        wid = QtWidgets.QWidget()
        self.setCentralWidget(wid)

        # Menubar and action.
        aboutAction = QtWidgets.QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        menubar = self.menuBar()
        menuMenu = menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Queston label and two options
        questionLabel = QtWidgets.QLabel()
        questionLabel.setText("What is your input data type?")

        questionFont = QtGui.QFont()
        questionFont.setPointSize(24)
        questionFont.setFamily("Copperplate")
        questionLabel.setFont(questionFont)  # Font of the question label.

        self.alignBox = QtWidgets.QCheckBox("Multiple sequence alignments of unlinked loci", self)
        self.biAllelicBox = QtWidgets.QCheckBox("Unlinked bi-allelic markers", self)

        self.alignBox.stateChanged.connect(self.onChecked)
        self.biAllelicBox.stateChanged.connect(self.onChecked)  # Implement mutually exclusive check boxes

        checkBoxFont = QtGui.QFont()
        checkBoxFont.setFamily("Times New Roman")
        checkBoxFont.setPointSize(15)
        self.alignBox.setFont(checkBoxFont)
        self.biAllelicBox.setFont(checkBoxFont)  # Font of two checkboxes.

        # OK and Cancel buttons
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setDefault(True)

        buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close)
        buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.okClicked)

        # Image and Title
        pix = QtGui.QPixmap(resource_path("logo.png"))
        image = QtWidgets.QLabel(self)
        image.setPixmap(pix)
        lbl = QtWidgets.QLabel("PhyloNet")

        titleFont = QtGui.QFont()
        titleFont.setPointSize(24)
        titleFont.setBold(True)
        lbl.setFont(titleFont)  # Font of the PhyloNet title.

        # Separation line
        line = QtWidgets.QFrame(self)
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Layouts
        # Top level logo and title.
        top = QtWidgets.QHBoxLayout()
        top.addWidget(image)
        top.addWidget(lbl)

        # Main vertical layout.
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(top)
        vbox.addWidget(line)
        vbox.addWidget(questionLabel)
        vbox.addSpacing(20)
        vbox.addWidget(self.alignBox)
        vbox.addSpacing(20)
        vbox.addWidget(self.biAllelicBox)
        wid.setLayout(vbox)

        # Bottom button box layout.
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(buttonBox)

        vbox.addLayout(hbox)
        vbox.setContentsMargins(50, 10, 50, 10)

        menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QtGui.QIcon(resource_path("logo.png")))

    def aboutMessage(self):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
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
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

    def onChecked(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        if self.sender().text() == "Multiple sequence alignments of unlinked loci":
            if not self.alignBox.isChecked():
                pass
            else:
                self.biAllelicBox.setChecked(False)
        elif self.sender().text() == "Unlinked bi-allelic markers":
            if not self.biAllelicBox.isChecked():
                pass
            else:
                self.alignBox.setChecked(False)
                self.biAllelicBox.setChecked(True)

    def okClicked(self):
        if self.alignBox.isChecked():
            self.newPage = SecondPage.SecondPage()
            self.newPage.show()
            self.close()
        elif self.biAllelicBox.isChecked():
            self.newPage = BiAllelicMethodsPage.BiAllelicMethodsPage()
            self.newPage.show()
            self.close()
        else:
            pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Launcher()
    ex.show()
    sys.exit(app.exec_())