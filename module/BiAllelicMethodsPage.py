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

        # Menu of commands
        self.btn1 = QRadioButton("MCMC_BiMarkers (Bayesian)")
        self.btn2 = QRadioButton("MLE_BiMarkers (Pseudo likelihood)")
        self.methodgroup = QCheckBox("")
        self.registerField("methodgroup*", self.methodgroup)
        #self.btn1.toggled.connect(self.btnState)
        #self.btn2.toggled.connect(self.btnState)

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
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)
        vbox.addWidget(hyperlink)
        vbox.addWidget(launchBtn)
        self.setLayout(vbox)

        vbox.setContentsMargins(50, 10, 50, 10)

        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("logo.png")))
    
    def onChecked(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        self.methodgroup.setCheckState(True)
    

    def btnState(self):
        """
        Originally created this method for the use of toggle.connect,
        yet it is no longer needed. I kept this method in case someone may
        want to use toggle.connect in the future
        """
        rbtn = self.sender()
        btn = str(rbtn.text())
        if rbtn.isChecked() == True:
            return btn

    def aboutMessage(self):
        msg = QDialog()
        msg.setWindowTitle("Phylonet") 
        msg.setWindowIcon(QIcon("logo.png"))
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint )
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
        
        hyperlink = QLabel()
        hyperlink.setText('For more details related to this group please visit '
                          '<a href="http://bioinfo.cs.rice.edu" style="color: #55ddff;">'
                          'http://bioinfo.cs.rice.edu</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setStyleSheet("padding: 10px 100px 80px 100px ;")

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(msg.accept)
        vbox.addWidget(text)
        vbox.addWidget(hyperlink)
        vbox.addWidget(buttonBox)
        msg.setLayout(vbox)
        msg.exec_()

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    def launch(self):
        if self.btn1.isChecked() == True:
            self.MCMCBi = MCMCBiMarkersThreading.MCMCBiMarkersPage()
            self.MCMCBi.show()
            #Closes the window so its cleaner
            self.wizard().close()
        
        elif self.btn2.isChecked() == True:
            self.MLEBi = MLEBiMarkersThreading.MLEBiMarkersPage()
            self.MLEBi.show()
            #Closes the window so its cleaner
            self.wizard().close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BiAllelicMethodsPage()
    ex.show() 
    sys.exit(app.exec_())
