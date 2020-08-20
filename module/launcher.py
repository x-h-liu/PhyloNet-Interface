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

import PostProcessingModule.menu

from functions import *
from main import *


def resource_path(relative_path):
    """
    Refer to the location of a file at run-time.
    This function is from
    https://www.reddit.com/r/learnpython/comments/4kjie3/how_to_include_gui_images_with_pyinstaller/
    # run-time-information
    For more information, visit https://pythonhosted.org/PyInstaller/runtime-information.html
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class Launcher(QtWidgets.QWizard):

    Page_Intro = 1
    Page_BiAllelic = 2
    Page_DirectInf = 3
    Page_GeneTreeEst = 4
    Page_NetworkMP = 5
    Page_NetworkML = 6
    Page_NetworkMPL = 7
    Page_MCMCGT = 8

    def __init__(self):
        super(Launcher, self).__init__()

        self.setDefaultProperty("QTextEdit", "plainText",
                                QtWidgets.QTextEdit.textChanged)
        self.Intro = IntroPage()
        self.BiAllelic = BiAllelicMethodsPage.BiAllelicMethodsPage()
        self.DirectInf = MCMCSEQ.MCMCSEQPage()
        self.GeneTreeEst = TreeMethodsPage.TreeMethodsPage()
        self.NetworkMP = NetworkMP.NetworkMPPage()
        self.NetworkML = NetworkML.NetworkMLPage()
        self.NetworkMPL = NetworkMPL.NetworkMPLPage()
        self.MCMCGT = MCMCGT.MCMCGTPage()

        self.setPage(self.Page_Intro, self.Intro)
        self.setPage(self.Page_DirectInf, self.DirectInf)
        self.setPage(self.Page_BiAllelic, self.BiAllelic)
        self.setPage(self.Page_GeneTreeEst, self.GeneTreeEst)
        self.setPage(self.Page_NetworkMP, self.NetworkMP)
        self.setPage(self.Page_NetworkML, self.NetworkML)
        self.setPage(self.Page_NetworkMPL, self.NetworkMPL)
        self.setPage(self.Page_MCMCGT, self.MCMCGT)
        self.initUI()

    def initUI(self):
        """
         GUI.
        """
        #set window title and label
        self.setWindowTitle("Phylonet") 
        self.setWindowIcon(QIcon("module/logo.png"))
        #set maximize and minimize options
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint 
                    | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        #flags = QtCore.Qt.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setModal(1)
        #self.resize(1300, 1100)
        self.setMinimumSize(1300, 1100)
        bLayout = [QWizard.Stretch, QWizard.NextButton, QWizard.CustomButton1, QWizard.CustomButton2, QWizard.CancelButton, QWizard.BackButton]
        self.setButtonLayout(bLayout)

        #set custom button options
        self.setOption(QWizard.HaveCustomButton1, True)
        self.setOption(QWizard.HaveCustomButton2, True)

        self.setButtonText(QWizard.CustomButton1, "&Use Again")
        self.button(QWizard.CustomButton1).setVisible(False)
  
        self.setButtonText(QWizard.CustomButton2, "&Finish")
        self.button(QWizard.CustomButton2).setVisible(False)

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
                # Page doesn't matter, just can't be finish, this way the next button still has an "id"
                return self.Page_DirectInf
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
                return self.Page_NetworkMP  # Like above doesn't matter, cant be finish
        else:
            return -1


class IntroPage(QtWidgets.QWizardPage):
    def __init__(self, parent=Launcher):
        super(IntroPage, self).__init__()
        self.initUI()

    def initUI(self):

        # Queston label and two options
        questionLabel = QtWidgets.QLabel()
        questionLabel.setObjectName("questionLabel")
        questionLabel.setText("What is your input data type?")

        self.inputOption1 = QtWidgets.QRadioButton(
            "Multiple sequence alignments of unlinked loci (direct inference)")
        self.inputOption2 = QtWidgets.QRadioButton("Gene tree estimates")
        self.inputOption3 = QtWidgets.QRadioButton(
            "Unlinked bi-allelic markers")
        self.invisButton = QtWidgets.QCheckBox("")
        self.registerField("invisButton*", self.invisButton)
      #  self.registerField("alignBox*", self.alignBox)
      #  self.registerField("biAllelicBox*", self.biAllelicBox)

        self.inputOption1.toggled.connect(self.onChecked)
        self.inputOption2.toggled.connect(self.onChecked)
        self.inputOption3.toggled.connect(self.onChecked)

        # Layouts
        # Main vertical layout.
        vbox = QtWidgets.QVBoxLayout()
        vbox.setObjectName("vbox")
        vbox.setSpacing(30)

        #info button gotta go
        #vbox.addWidget(getInfoButton(self))
        vbox.addWidget(questionLabel)
        vbox.addWidget(self.inputOption1, alignment=QtCore.Qt.AlignCenter)
        vbox.addWidget(self.inputOption2, alignment=QtCore.Qt.AlignCenter)
        vbox.addWidget(self.inputOption3, alignment=QtCore.Qt.AlignCenter)

        self.setLayout(vbox)

    def onChecked(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        self.invisButton.setCheckState(True)

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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(style)
    ex = Launcher()
    #ex.resize(1266, 982)
    ex.show()
    sys.exit(app.exec_())
