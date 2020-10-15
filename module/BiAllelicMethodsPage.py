import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from module import NetworkMP
from module import NetworkML
from module import NetworkMPL
from module import MCMCGT

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


class BiAllelicMethodsPage(QWizardPage):
    def __init__(self):
        super(BiAllelicMethodsPage, self).__init__()

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """

        # Queston label and two options
        questionLabel = QLabel()
        questionLabel.setText("Please select a method:")
        questionLabel.setObjectName("questionLabel")

        # Drop-down menu of commands
        self.methods1 = QRadioButton(
            "MCMC_BiMarkers (Bayesian)")
        self.methods2 = QRadioButton("MLE_BiMarkers (Pseudo likelihood)")
        self.methodgroup = QCheckBox("")
        
        self.methods1.toggled.connect(self.onChecked)
        self.methods2.toggled.connect(self.onChecked)
        

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
        vbox.addWidget(hyperlink)
        vbox.addWidget(self.methods1)
        vbox.addWidget(self.methods2)

      #  vbox.addWidget(launchBtn)
        self.setLayout(vbox)

        vbox.setContentsMargins(50, 10, 50, 10)

        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("logo.png")))

    def onChecked(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        self.methodgroup.setCheckState(True)


    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BiAllelicMethodsPage()
    ex.show()
    sys.exit(app.exec_())
