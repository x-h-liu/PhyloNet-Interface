import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from module import MLEBiMarkersThreading
from module import MCMCBiMarkersThreading


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


class BiAllelicMethodsPage(QWizardPage):
    def __init__(self):
        super(BiAllelicMethodsPage, self).__init__()

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
      #  wid = QWidget()
      #  self.setCentralWidget(wid)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        # Queston label and two options
        questionLabel = QLabel()
        questionLabel.setObjectName("questionLabel")
        questionLabel.setText("Please select a method:")

        # Drop-down menu of commands
        self.methods = QComboBox(self)
        self.methods.addItem("MCMC_BiMarkers (Bayesian)")
        self.methods.addItem("MLE_BiMarkers (Pseudo likelihood)")

        # Launch button
        launchBtn = QPushButton("Launch", self)
        launchBtn.clicked.connect(self.launch)

        # Link to PhyloNet documentation page
        hyperlink = QLabel()
        hyperlink.setText('For details of these methods, please click '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/List+of+PhyloNet+Commands">'
                          'here</a>')
        hyperlink.linkActivated.connect(self.link)

        # Layouts

        # Main vertical layout.
        vbox = QVBoxLayout()
        vbox.addWidget(questionLabel)
        vbox.addWidget(self.methods)
        vbox.addWidget(hyperlink)
        vbox.addWidget(launchBtn)
        self.setLayout(vbox)

        vbox.setContentsMargins(50, 10, 50, 10)

        self.setWindowTitle('PhyloNetNEXGenerator')
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

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    def launch(self):
        if str(self.methods.currentText()) == "MLE_BiMarkers (Pseudo likelihood)":
            self.MLEBi = MLEBiMarkersThreading.MLEBiMarkersPage()
            self.MLEBi.show()
            self.close()
            #return True
        elif str(self.methods.currentText()) == "MCMC_BiMarkers (Bayesian)":
            self.MCMCBi = MCMCBiMarkersThreading.MCMCBiMarkersPage()
            self.MCMCBi.show()
            self.close()
            #return True
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BiAllelicMethodsPage()
    ex.show() 
    sys.exit(app.exec_())
