import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from module import NetworkMP
from module import NetworkML
from module import NetworkMLCV
from module import NetworkMLBootstrap
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


class TreeMethodsPage(QWizardPage):
    def __init__(self):
        super(TreeMethodsPage, self).__init__()

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
            "Inference under the MDC Criterion (parsimony)")
        self.methods2 = QRadioButton("Inference under maximum likelihood")
        self.methods3 = QRadioButton("Inference under maximum likelihood, using K-fold cross-validation.")
        self.methods4 = QRadioButton("Inference under maximum likelihood with parametric bootstrap.")
        self.methods5 = QRadioButton(
            "Inference under maximum pseudo-likelihood")
        self.methods6 = QRadioButton("Bayenesian MCMC posterior estimation")
        self.methodgroup = QCheckBox("")
        self.registerField("methodgroup*", self.methodgroup)

        self.methods1.toggled.connect(self.onChecked)
        self.methods2.toggled.connect(self.onChecked)
        self.methods3.toggled.connect(self.onChecked)
        self.methods4.toggled.connect(self.onChecked)
        self.methods5.toggled.connect(self.onChecked)
        self.methods6.toggled.connect(self.onChecked)


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
        vbox.addWidget(self.methods3)
        vbox.addWidget(self.methods4)
        vbox.addWidget(self.methods5)
        vbox.addWidget(self.methods6)

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
    ex = TreeMethodsPage()
    ex.show()
    sys.exit(app.exec_())
