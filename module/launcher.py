import os
import sys
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from module import BiAllelicMethodsPage
from module import MCMCSEQ
from module import TreeMethodsPage
from module import NetworkMP
from module import NetworkML
from module import NetworkMPL
from module import MCMCGT

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


class Launcher(QtWidgets.QWizard):
   
    
    Page_Intro = 1
    Page_BiAllelic = 2
    Page_DirectInf = 3
    Page_GeneTreeEst = 4
    Page_DirectInf2 = 5
    Page_DirectInf3 = 6
    Page_DirectInf4 = 7
    Page_NetworkMP = 8
    Page_NetworkMP2 = 9
    Page_NetworkMP3 = 10
    Page_NetworkMP4 = 11
    Page_NetworkML = 12
    Page_NetworkML2 = 13
    Page_NetworkMPL = 14
    Page_MCMCGT = 15


    def __init__(self):
        super(Launcher, self).__init__()

        self.setDefaultProperty("QTextEdit", "plainText", QtWidgets.QTextEdit.textChanged)
        self.Intro = IntroPage()
        self.BiAllelic = BiAllelicMethodsPage.BiAllelicMethodsPage()
        self.DirectInf = MCMCSEQ.MCMCSEQPage1(parent=self)
        self.DirectInf2 = MCMCSEQ.MCMCSEQPage2()
        self.DirectInf3 = MCMCSEQ.MCMCSEQPage3()
        self.DirectInf4 = MCMCSEQ.MCMCSEQPage4()
        self.GeneTreeEst = TreeMethodsPage.TreeMethodsPage()
        self.NetworkMP = NetworkMP.NetworkMPPage()
        self.NetworkMP2 = NetworkMP.NetworkMPPage2()
        self.NetworkMP3 = NetworkMP.NetworkMPPage3()
        self.NetworkMP4 = NetworkMP.NetworkMPPage4()
        self.NetworkML = NetworkML.NetworkMLPage()
        self.NetworkML2 = NetworkML.NetworkMLPage2()
        self.NetworkMPL = NetworkMPL.NetworkMPLPage()
        self.MCMCGT = MCMCGT.MCMCGTPage()


        self.setPage(self.Page_Intro, self.Intro)
        self.setPage(self.Page_DirectInf, self.DirectInf)
        self.setPage(self.Page_DirectInf2, self.DirectInf2)
        self.setPage(self.Page_DirectInf3, self.DirectInf3)
        self.setPage(self.Page_BiAllelic, self.BiAllelic)
        self.setPage(self.Page_GeneTreeEst, self.GeneTreeEst)
        self.setPage(self.Page_DirectInf4, self.DirectInf4)
        self.setPage(self.Page_NetworkMP, self.NetworkMP)
        self.setPage(self.Page_NetworkML, self.NetworkML)
        self.setPage(self.Page_NetworkMPL, self.NetworkMPL)
        self.setPage(self.Page_MCMCGT, self.MCMCGT)
        self.setPage(self.Page_NetworkMP2, self.NetworkMP2)
        self.setPage(self.Page_NetworkML2, self.NetworkML2)
        self.setPage(self.Page_NetworkMP3, self.NetworkMP3)
        self.setPage(self.Page_NetworkMP4, self.NetworkMP4)

        self.initUI()

       # scrollArea = QtWidgets.QScrollArea()
       # scrollArea.setWidget(self.DirectInf)
       # scrollArea.setWidgetResizable(True)
       # scrollArea.setMinimumWidth(695)
       # scrollArea.setMinimumHeight(750)


    def initUI(self):
        """
        Initialize GUI.
        """
       # wid = QtWidgets.QWidget()
       # self.setCentralWidget(wid)

        self.setModal(1)


    def nextId(self):
        id = self.currentId()
        if id == Launcher.Page_Intro:
            if self.Intro.inputOption1.isChecked():
                return self.Page_DirectInf
            elif self.Intro.inputOption2.isChecked():
                return self.Page_GeneTreeEst
            elif self.Intro.inputOption3.isChecked():
                return self.Page_BiAllelic
            else: 
                return self.Page_DirectInf # Page doesn't matter, just can't be finish, this way the next button still has an "id"
        elif id == Launcher.Page_DirectInf:
            return self.Page_DirectInf2
        elif id == Launcher.Page_DirectInf2:
            return self.Page_DirectInf3
        elif id == Launcher.Page_DirectInf3:
            return self.Page_DirectInf4
        elif id == Launcher.Page_GeneTreeEst:
            if self.GeneTreeEst.methods1.isChecked():
                return self.Page_NetworkMP
            elif self.GeneTreeEst.methods2.isChecked():
                return self.Page_NetworkML
            elif self.GeneTreeEst.methods3.isChecked():
                return self.Page_NetworkMPL
            elif self.GeneTreeEst.methods4.isChecked():
                return self.Page_MCMCGT
            else:
                return self.Page_NetworkMP #Like above doesn't matter, cant be finish
        elif id == Launcher.Page_NetworkMP:
            return self.Page_NetworkMP2
        elif id == Launcher.Page_NetworkML:
            return self.Page_NetworkML2
        elif id == Launcher.Page_NetworkMP2:
            return self.Page_NetworkMP3
        elif id == Launcher.Page_NetworkMP3:
            return self.Page_NetworkMP4
        else:    
            return -1

class IntroPage(QtWidgets.QWizardPage):
    def __init__(self, parent=Launcher):
        super(IntroPage, self).__init__()

        self.initUI()
    
    def initUI(self):
    
        # Menubar and action.
        aboutAction = QtWidgets.QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        self.menubar = QtWidgets.QMenuBar(self)
        menuMenu = self.menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Queston label and two options
        questionLabel = QtWidgets.QLabel()
        questionLabel.setText("What is your input data type?")

        questionFont = QtGui.QFont()
        questionFont.setPointSize(24)
        questionFont.setFamily("Copperplate")
        questionLabel.setFont(questionFont)  # Font of the question label.


        self.inputOption1 = QtWidgets.QRadioButton("Multiple sequence alignments of unlinked loci (direct inference)")
        self.inputOption2 = QtWidgets.QRadioButton("Gene tree estimates")
        self.inputOption3 = QtWidgets.QRadioButton("Unlinked bi-allelic markers")
        self.invisButton = QtWidgets.QCheckBox("")
        self.registerField("invisButton*", self.invisButton)
      #  self.registerField("alignBox*", self.alignBox)
      #  self.registerField("biAllelicBox*", self.biAllelicBox)

        self.inputOption1.toggled.connect(self.onChecked)
        self.inputOption2.toggled.connect(self.onChecked)
        self.inputOption3.toggled.connect(self.onChecked)
      #  checkBoxFont = QtGui.QFont()
      #  checkBoxFont.setFamily("Times New Roman")
      #  checkBoxFont.setPointSize(15)
      #  self.alignBox.setFont(checkBoxFont)
      #  self.biAllelicBox.setFont(checkBoxFont)  # Font of two checkboxes.

        # OK and Cancel buttons
      #  buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
      #  buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setDefault(True)

      #  buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.close)
      #  buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.okClicked)

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
        vbox.addWidget(self.inputOption1)
        vbox.addWidget(self.inputOption2)
        vbox.addWidget(self.inputOption3)
      #  vbox.addSpacing(20)
      #  vbox.addWidget(self.biAllelicBox)
        self.setLayout(vbox)
      #  self.setFixedSize(750,700)

        # Bottom button box layout.
       # hbox = QtWidgets.QHBoxLayout()
       # hbox.addStretch()
       # hbox.addWidget(buttonBox)

      #  vbox.addLayout(hbox)
      #  vbox.setContentsMargins(50, 10, 50, 10)

        self.menubar.setNativeMenuBar(False)
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
        self.invisButton.setCheckState(True)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = Launcher()
    ex.show()
    sys.exit(app.exec_())
