import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
import dendropy
import datetime
import subprocess
import shutil

from Validator import NumValidator
from module import TaxamapDlg
from functions import *


inputFiles = []
geneTreeNames = []
taxamap = {}

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

class NetworkMLCVPage(QWizardPage):
    #set signals for page
    restarted = QtCore.pyqtSignal(bool)
    generated = QtCore.pyqtSignal(bool)
    def initializePage(self):
        #get the wizard buttons
        again_button = self.wizard().button(QWizard.CustomButton1)
        finish_button = self.wizard().button(QWizard.CustomButton2)
        back_button = self.wizard().button(QWizard.BackButton)
        
        self.generated.connect(lambda : again_button.setVisible(True))
        self.generated.connect(lambda : finish_button.setVisible(True))
        self.generated.connect(lambda : self.wizard().button(QWizard.CancelButton).setVisible(False))

        #close if finish button is clicked
        finish_button.clicked.connect(lambda : self.wizard().close())

        #take the user back to first page if use again is clicked
        #and hide the wizard button
        again_button.clicked.connect(lambda : self.tabWidget.setCurrentIndex(0))
        again_button.clicked.connect(lambda : self.restarted.emit(True))

        # in case back button is clicked while custom buttons are available
        #hide custom buttons
        back_button.clicked.connect(lambda: again_button.setVisible(False))
        back_button.clicked.connect(lambda: finish_button.setVisible(False))

        #if the user choosees to use again, hide custom buttons
        #reintroduce cancel button
        self.restarted.connect(lambda : again_button.setVisible(False))
        self.restarted.connect(lambda: finish_button.setVisible(False))
        self.restarted.connect(lambda : self.wizard().button(QWizard.CancelButton).setVisible(True))
        self.restarted.connect(lambda : self.inspectInputs())
        
        #if you're on last page and the bar is disabled restore buttons 'em
        #edge case
        if self.tabWidget.currentIndex() == self.TABS - 1:
            again_button.setVisible(True)
            finish_button.setVisible(True)

    def __init__(self):
        super(NetworkMLCVPage, self).__init__()
        
        self.inputFiles = []
        self.geneTreeNames = []
        self.taxamap = {}
        self.multiTreesPerLocus = False
        self.TABS = 4

        self.isValidated = False
        self.initUI()

    def initUI(self):
        titleLabel = titleHeader("InferNetwork_ML_CV")

        hyperlink = QLabel()
        hyperlink.setText('For more details '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_ML_CV+Command">'
                          'click here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")
        
        head = QHBoxLayout()
        head.setSpacing(0)
        head.addWidget(titleLabel)
        head.addWidget(hyperlink)

        #title and help link, available on each page
        pageLayout = QVBoxLayout()
        pageLayout.addLayout(head)

        #create tabs
        self.tabWidget = QTabWidget(self)
        self.tabWidget.tabBar().setShape(QTabBar.TriangularNorth)

        self.tabWidget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        #create first    
        tabOne = QWidget(self)
        
        #tab sub header
        instructionLabel = QLabel()
        instructionLabel.setText("Input data: Please Upload Gene tree files:\n(one file per locus)")
        instructionLabel.setObjectName("instructionLabel")  

        # Mandatory parameter labels
        self.nexus = QCheckBox(".nexus")
        self.nexus.setObjectName("nexus")
        self.newick = QCheckBox(".newick")
        self.newick.setObjectName("newick")
        numReticulationsLbl = QLabel("Maximum number of reticulations to add:")
        # Implement mutually exclusive check boxes
        self.nexus.stateChanged.connect(self.format)
        self.newick.stateChanged.connect(self.format)

        # Mandatory parameter inputs
        self.geneTreesEdit = QTextEdit()
        self.geneTreesEdit.textChanged.connect(self.inspectInputs)
        self.geneTreesEdit.setReadOnly(True)
        self.geneTreesEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        fileSelctionBtn = QToolButton()
        fileSelctionBtn.setText("Browse")
        fileSelctionBtn.clicked.connect(self.selectFile)

        self.numReticulationsEdit = QLineEdit()
        self.numReticulationsEdit.textChanged.connect(self.inspectInputs)
        self.numReticulationsEdit.setValidator(NumValidator())
        self.numReticulationsEdit.setToolTip("Please enter a non-negative integer")

        # Layouts
        # Layout of each parameter (label and input)
        fileFormatLayout = QVBoxLayout()
        fileFormatLayout.addWidget(instructionLabel)
        fileFormatLayout.addWidget(self.nexus)
        fileFormatLayout.addWidget(self.newick)
        geneTreeDataLayout = QHBoxLayout()
        geneTreeDataLayout.addWidget(self.geneTreesEdit)
        geneTreeDataLayout.addWidget(fileSelctionBtn)
      
        numReticulationsLayout = QHBoxLayout()
        numReticulationsLayout.addWidget(numReticulationsLbl)
        numReticulationsLayout.addWidget(self.numReticulationsEdit)

        # Main layout for tab one
        tabOneLayout = QVBoxLayout()
        tabOneLayout.addLayout(fileFormatLayout)
        tabOneLayout.addLayout(geneTreeDataLayout)
        tabOneLayout.addLayout(numReticulationsLayout)

        tabOne.setLayout(tabOneLayout)

        #Add tab One
        self.tabWidget.addTab(tabOne, 'Mandatory')

        #create tab two
        tabTwo = QWidget(self)
        #tabTwo.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        optionalLabel = QLabel()
        optionalLabel.setObjectName("instructionLabel")
        optionalLabel.setText("Optional Parameters")
        optionalLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels
        self.numFoldsLbl = QCheckBox("Number of folds in K-fold cross-validation", self)
        self.numFoldsLbl.setObjectName("-cv")
        self.numFoldsLbl.stateChanged.connect(self.onChecked)

        self.thresholdLbl = QCheckBox("Gene trees bootstrap threshold:", self)
        self.thresholdLbl.setObjectName("-b")
        self.thresholdLbl.stateChanged.connect(self.onChecked)

        self.taxamapLbl = QCheckBox(
            "Gene tree / species tree taxa association:", self)
        self.taxamapLbl.setObjectName("-a")
        self.taxamapLbl.stateChanged.connect(self.onChecked)

        self.sNetLbl = QCheckBox("The network to start search:", self)
        self.sNetLbl.setObjectName("-s")
        self.sNetLbl.stateChanged.connect(self.onChecked)

        self.hybridLbl = QCheckBox("A set of specified hybrid species:", self)
        self.hybridLbl.setObjectName("-h")
        self.hybridLbl.stateChanged.connect(self.onChecked)

        self.wetOpLbl = QCheckBox("Weights of operations for network arrangement during the network search:", self)
        self.wetOpLbl.setObjectName("-w")
        self.wetOpLbl.stateChanged.connect(self.onChecked)

        self.numRunLbl = QCheckBox("The number of runs of the search:", self)
        self.numRunLbl.setObjectName("-x")
        self.numRunLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.numFoldsEdit = QLineEdit()
        self.numFoldsEdit.setDisabled(True)
        self.numFoldsEdit.setPlaceholderText("10")

        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setDisabled(True)

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setObjectName("taxamapEdit")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)

        self.hybridEdit = QLineEdit()
        self.hybridEdit.setDisabled(True)

        self.wetOpEdit = QLineEdit()
        self.wetOpEdit.setDisabled(True)
        self.wetOpEdit.setPlaceholderText("(0.1,0.1,0.15,0.55,0.15,0.15,2.8)")
        self.wetOpEdit.setMinimumWidth(200)

        self.numRunEdit = QLineEdit()
        self.numRunEdit.setDisabled(True)
        self.numRunEdit.setPlaceholderText("5")
 
        # Layouts
        # Layout of each parameter (label and input)
        numFoldsLayout = QHBoxLayout()
        numFoldsLayout.addWidget(self.numFoldsLbl)
        numFoldsLayout.addStretch(1)
        numFoldsLayout.addWidget(self.numFoldsEdit)

        thresholdLayout = QHBoxLayout()
        thresholdLayout.addWidget(self.thresholdLbl)
        thresholdLayout.addStretch(1)
        thresholdLayout.addWidget(self.thresholdEdit)

        taxamapLayout = QHBoxLayout()
        taxamapLayout.addWidget(self.taxamapLbl)
        taxamapLayout.addStretch(1)
        taxamapLayout.addWidget(self.taxamapEdit)

        sNetLayout = QHBoxLayout()
        sNetLayout.addWidget(self.sNetLbl)
        sNetLayout.addWidget(self.sNetEdit)

        hybridLayout = QHBoxLayout()
        hybridLayout.addWidget(self.hybridLbl)
        hybridLayout.addWidget(self.hybridEdit)

        wetOpLayout = QHBoxLayout()
        wetOpLayout.addWidget(self.wetOpLbl)
        wetOpLayout.addStretch(1)
        wetOpLayout.addWidget(self.wetOpEdit)

        numRunLayout = QHBoxLayout()
        numRunLayout.addWidget(self.numRunLbl)
        numRunLayout.addStretch(1)
        numRunLayout.addWidget(self.numRunEdit)

        # Main Layout tab two
        tabTwoLayout = QVBoxLayout()
        tabTwoLayout.addWidget(optionalLabel)
        tabTwoLayout.addLayout(numFoldsLayout)
        tabTwoLayout.addLayout(thresholdLayout)
        tabTwoLayout.addLayout(taxamapLayout)
        tabTwoLayout.addLayout(sNetLayout)
        tabTwoLayout.addLayout(hybridLayout)
        tabTwoLayout.addLayout(wetOpLayout)
        tabTwoLayout.addLayout(numRunLayout)
        tabTwo.setLayout(tabTwoLayout)   

        #add tab two
        self.tabWidget.addTab(tabTwo, 'Parameters')

        #create tab three 
        tabThree = QWidget(self)
        #tabThree.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        optionalLabelA = QLabel()
        optionalLabelA.setObjectName("instructionLabel")
        optionalLabelA.setText("Optional Parameters")
        optionalLabelA.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)


        # Optional parameter labels
        self.branchlengthLbl = QCheckBox("Use the branch lengths of the gene trees for the inference.", self)
        self.branchlengthLbl.stateChanged.connect(self.onChecked)

        self.nNetExamLbl = QCheckBox("Maximum number of network topologies to examine:", self)
        self.nNetExamLbl.setObjectName("-m")
        self.nNetExamLbl.stateChanged.connect(self.onChecked)

        self.maxDiaLbl = QCheckBox("Maximum diameter to make an arrangement during network search:", self)
        self.maxDiaLbl.setObjectName("-md")
        self.maxDiaLbl.stateChanged.connect(self.onChecked)

        self.retDiaLbl = QCheckBox("Maximum diameter for a reticulation event:", self)
        self.retDiaLbl.setObjectName("-rd")
        self.retDiaLbl.stateChanged.connect(self.onChecked)

        self.oLabel = QCheckBox("Optimize branch lengths and inheritance probabilities for every proposed species "
                                "network during the search", self)

        self.stopCriterionLbl = QCheckBox("The original stopping criterion of Brent's algorithm:", self)
        self.stopCriterionLbl.setObjectName("-p")
        self.stopCriterionLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.nNetExamEdit = QLineEdit()
        self.nNetExamEdit.setDisabled(True)
        self.nNetExamEdit.setPlaceholderText("infinity")

        self.maxDiaEdit = QLineEdit()
        self.maxDiaEdit.setDisabled(True)
        self.maxDiaEdit.setPlaceholderText("infinity")

        self.retDiaEdit = QLineEdit()
        self.retDiaEdit.setDisabled(True)
        self.retDiaEdit.setPlaceholderText("infinity")     

        self.stopCriterionEdit = QLineEdit()
        self.stopCriterionEdit.setDisabled(True)
        self.stopCriterionEdit.setPlaceholderText("(0.01, 0.001)")

        #Layouts
        blLayout = QHBoxLayout()
        blLayout.addWidget(self.branchlengthLbl)

        nNetExamLayout = QHBoxLayout()
        nNetExamLayout.addWidget(self.nNetExamLbl)
        nNetExamLayout.addStretch(1)
        nNetExamLayout.addWidget(self.nNetExamEdit)

        maxDiaLayout = QHBoxLayout()
        maxDiaLayout.addWidget(self.maxDiaLbl)
        maxDiaLayout.addStretch(1)
        maxDiaLayout.addWidget(self.maxDiaEdit)

        retDiaLayout = QHBoxLayout()
        retDiaLayout.addWidget(self.retDiaLbl)
        retDiaLayout.addStretch(1)
        retDiaLayout.addWidget(self.retDiaEdit)

        oLayout = QHBoxLayout()
        oLayout.addWidget(self.oLabel)

        stopCriterionLayout = QHBoxLayout()
        stopCriterionLayout.addWidget(self.stopCriterionLbl)
        stopCriterionLayout.addStretch(1)
        stopCriterionLayout.addWidget(self.stopCriterionEdit)

        # Main Layout tab three

        tabThreeLayout = QVBoxLayout()
        tabThreeLayout.addWidget(optionalLabelA)
        tabThreeLayout.addLayout(blLayout)
        tabThreeLayout.addLayout(nNetExamLayout)
        tabThreeLayout.addLayout(maxDiaLayout)
        tabThreeLayout.addLayout(retDiaLayout)
        tabThreeLayout.addLayout(oLayout)
        tabThreeLayout.addLayout(stopCriterionLayout)

        tabThree.setLayout(tabThreeLayout)          

        #add tabthree
        self.tabWidget.addTab(tabThree, 'Parameters')

        #create tab four 
        tabFour = QWidget(self)

        optionalLabelB = QLabel()
        optionalLabelB.setObjectName("instructionLabel")
        optionalLabelB.setText("Optional Parameters")
        optionalLabelB.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)


        # Optional parameter labels
        self.maxRoundLbl = QCheckBox("Maximum number of rounds to optimize branch lengths for a network topology:", self)
        self.maxRoundLbl.setObjectName("-r")
        self.maxRoundLbl.stateChanged.connect(self.onChecked)

        self.maxTryPerBrLbl = QCheckBox("Maximum number of trial per branch in one round to optimize branch lengths for "
                                        "a network topology:", self)
        self.maxTryPerBrLbl.setObjectName("-t")
        self.maxTryPerBrLbl.stateChanged.connect(self.onChecked)

        self.improveThresLbl = QCheckBox("Minimum threshold of improvement to continue the next round of optimization "
                                         "of branch lengths:", self)
        self.improveThresLbl.setObjectName("-i")
        self.improveThresLbl.stateChanged.connect(self.onChecked)

        self.maxBlLbl = QCheckBox("Maximum branch lengths considered:", self)
        self.maxBlLbl.setObjectName("-l")
        self.maxBlLbl.stateChanged.connect(self.onChecked)

        self.numProcLbl = QCheckBox("Number of processors:", self)
        self.numProcLbl.setObjectName("-pl")
        self.numProcLbl.stateChanged.connect(self.onChecked)

        self.diLbl = QCheckBox("Output Rich Newick string that can be read by Dendroscope.")
        self.diLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.maxRoundEdit = QLineEdit()
        self.maxRoundEdit.setDisabled(True)
        self.maxRoundEdit.setPlaceholderText("100")

        self.maxTryPerBrEdit = QLineEdit()
        self.maxTryPerBrEdit.setDisabled(True)
        self.maxTryPerBrEdit.setPlaceholderText("100")

        self.improveThresEdit = QLineEdit()
        self.improveThresEdit.setDisabled(True)
        self.improveThresEdit.setPlaceholderText("0.001")

        self.maxBlEdit = QLineEdit()
        self.maxBlEdit.setDisabled(True)
        self.maxBlEdit.setPlaceholderText("6")

        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)
        self.numProcEdit.setPlaceholderText("1")

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        # Layouts
        # Layout of each parameter (label and input)
        maxRoundLayout = QHBoxLayout()
        maxRoundLayout.addWidget(self.maxRoundLbl)
        maxRoundLayout.addStretch(1)
        maxRoundLayout.addWidget(self.maxRoundEdit)

        maxTryPerBrLayout = QHBoxLayout()
        maxTryPerBrLayout.addWidget(self.maxTryPerBrLbl)
        maxTryPerBrLayout.addStretch(1)
        maxTryPerBrLayout.addWidget(self.maxTryPerBrEdit)

        improveThresLayout = QHBoxLayout()
        improveThresLayout.addWidget(self.improveThresLbl)
        improveThresLayout.addStretch(1)
        improveThresLayout.addWidget(self.improveThresEdit)

        maxBlLayout = QHBoxLayout()
        maxBlLayout.addWidget(self.maxBlLbl)
        maxBlLayout.addStretch(1)
        maxBlLayout.addWidget(self.maxBlEdit)

        numProcLayout = QHBoxLayout()
        numProcLayout.addWidget(self.numProcLbl)
        numProcLayout.addStretch(1)
        numProcLayout.addWidget(self.numProcEdit)

        diLayout = QHBoxLayout()
        diLayout.addWidget(self.diLbl)


        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)

        # Main Layout tab four

        tabFourLayout = QVBoxLayout()
        tabFourLayout.addWidget(optionalLabelB)
        tabFourLayout.addLayout(maxRoundLayout)
        tabFourLayout.addLayout(maxTryPerBrLayout)
        tabFourLayout.addLayout(improveThresLayout)
        tabFourLayout.addLayout(maxBlLayout)
        tabFourLayout.addLayout(numProcLayout)
        tabFourLayout.addLayout(diLayout)
        tabFourLayout.addLayout(btnLayout)

        tabFour.setLayout(tabFourLayout)          

        #add tabFour
        self.tabWidget.addTab(tabFour, 'Generate')

        #disable tab bar, initially   
        self.tabWidget.tabBar().setDisabled(True)
        self.tabWidget.tabBar().setToolTip("This a mandatory input. Complete it to enable the tab bar")

        #add widget to page layout
        pageLayout.addWidget(self.tabWidget)
        self.setLayout(pageLayout)

    def inspectInputs(self):
        """
        Inspects whether mandatory fields have been filled
        emits signal if so
        """
        if self.geneTreesEdit.document().isEmpty() or self.numReticulationsEdit.text() == "":
            self.tabWidget.tabBar().setDisabled(True)
            #set appropriate tool tip based on page location
            if self.tabWidget.currentIndex() == 0:
                self.tabWidget.tabBar().setToolTip("This a mandatory input. Complete it to enable the tab bar")
            else:
                self.tabWidget.tabBar().setToolTip("Click use again to return to first page")
            self.tabWidget.setStyleSheet("QTabBar::tab:selected{background-color: #aaeeff;}")
        else:
            self.tabWidget.tabBar().setDisabled(False)
            self.tabWidget.tabBar().setToolTip("Mandatory input completed! You can now use tab bar")
            self.tabWidget.setStyleSheet("QTabBar::tab:selected{background-color: #2196f3;}")
              
    def __inverseMapping(self, map):
        """
        Convert a mapping from taxon to species to a mapping from species to a list of taxon.
        """
        o = {}
        for k, v in map.items():
            if v in o:
                o[v].append(k)
            else:
                o[v] = [k]
        return o

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    def format(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        if self.sender().objectName() == "nexus":
            if not self.nexus.isChecked():
                self.geneTreesEdit.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
            else:
                self.newick.setChecked(False)
        elif self.sender().objectName() == "newick":
            if not self.newick.isChecked():
                self.geneTreesEdit.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
            else:
                self.nexus.setChecked(False)
                self.newick.setChecked(True)

    def selectFile(self):
        """
        Store all the user uploaded gene tree files.
        Execute when file selection button is clicked.
        """
        if (not self.newick.isChecked()) and (not self.nexus.isChecked()):
            QMessageBox.warning(self, "Warning", "Please select a file type.", QMessageBox.Ok)
        else:
            if self.nexus.isChecked():
                fname = QFileDialog.getOpenFileNames(self, 'Open file', '/', 'Nexus files (*.nexus *.nex)')
            elif self.newick.isChecked():
                fname = QFileDialog.getOpenFileNames(self, 'Open file', '/', 'Newick files (*.newick)') 
            #if a file has been inputted, proceed 
            if len(fname[0]) > 0:
                fileType = fname[1]
                if self.nexus.isChecked():
                    if fileType != 'Nexus files (*.nexus *.nex)':
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus or .nex files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            self.geneTreesEdit.append(onefname)
                            self.inputFiles.append(str(onefname))

                elif self.newick.isChecked():
                    if fileType != 'Newick files (*.newick)':
                        QMessageBox.warning(self, "Warning", "Please upload only .newick files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            self.geneTreesEdit.append(onefname)
                            self.inputFiles.append(str(onefname))

    def onChecked(self):
        """
        When user clicks the checkbox for an optional command,
        enable or disable the corresponding text edit.
        """
        if self.sender().objectName() == "-cv":
            if self.numFoldsEdit.isEnabled():
                self.numFoldsEdit.setDisabled(True)
            else:
                self.numFoldsEdit.setDisabled(False)
        if self.sender().objectName() == "-b":
            if self.thresholdEdit.isEnabled():
                self.thresholdEdit.setDisabled(True)
            else:
                self.thresholdEdit.setDisabled(False)
        elif self.sender().objectName() == "-a":
            if self.taxamapEdit.isEnabled():
                self.taxamapEdit.setDisabled(True)
            else:
                self.taxamapEdit.setDisabled(False)
        elif self.sender().objectName() == "-s":
            if self.sNetEdit.isEnabled():
                self.sNetEdit.setDisabled(True)
            else:
                self.sNetEdit.setDisabled(False)
        elif self.sender().objectName() == "-h":
            if self.hybridEdit.isEnabled():
                self.hybridEdit.setDisabled(True)
            else:
                self.hybridEdit.setDisabled(False)
        elif self.sender().objectName() == "-w":
            if self.wetOpEdit.isEnabled():
                self.wetOpEdit.setDisabled(True)
            else:
                self.wetOpEdit.setDisabled(False)
        elif self.sender().objectName() == "-x":
            if self.numRunEdit.isEnabled():
                self.numRunEdit.setDisabled(True)
            else:
                self.numRunEdit.setDisabled(False)
        elif self.sender().objectName() == "-m":
            if self.nNetExamEdit.isEnabled():
                self.nNetExamEdit.setDisabled(True)
            else:
                self.nNetExamEdit.setDisabled(False)
        elif self.sender().objectName() == "-md":
            if self.maxDiaEdit.isEnabled():
                self.maxDiaEdit.setDisabled(True)
            else:
                self.maxDiaEdit.setDisabled(False)
        elif self.sender().objectName() == "-rd":
            if self.retDiaEdit.isEnabled():
                self.retDiaEdit.setDisabled(True)
            else:
                self.retDiaEdit.setDisabled(False)
        elif self.sender().objectName() == "-f":
            if self.maxFEdit.isEnabled():
                self.maxFEdit.setDisabled(True)
            else:
                self.maxFEdit.setDisabled(False)
        elif self.sender().objectName() == "-p":
            if self.stopCriterionEdit.isEnabled():
                self.stopCriterionEdit.setDisabled(True)
            else:
                self.stopCriterionEdit.setDisabled(False)
        elif self.sender().objectName() == "-r":
            if self.maxRoundEdit.isEnabled():
                self.maxRoundEdit.setDisabled(True)
            else:
                self.maxRoundEdit.setDisabled(False)
        elif self.sender().objectName() == "-t":
            if self.maxTryPerBrEdit.isEnabled():
                self.maxTryPerBrEdit.setDisabled(True)
            else:
                self.maxTryPerBrEdit.setDisabled(False)
        elif self.sender().objectName() == "-i":
            if self.improveThresEdit.isEnabled():
                self.improveThresEdit.setDisabled(True)
            else:
                self.improveThresEdit.setDisabled(False)
        elif self.sender().objectName() == "-l":
            if self.maxBlEdit.isEnabled():
                self.maxBlEdit.setDisabled(True)
            else:
                self.maxBlEdit.setDisabled(False)
        elif self.sender().objectName() == "-pl":
            if self.numProcEdit.isEnabled():
                self.numProcEdit.setDisabled(True)
            else:
                self.numProcEdit.setDisabled(False)
        else:
            pass
    def getTaxamap(self):
        """
        When user clicks "Set taxa map", open up TaxamapDlg for user input
        and update taxa map.
        """
        class emptyFileError(Exception):
            pass
        try:
            if len(self.inputFiles) == 0:
                raise emptyFileError

            # Read files
            if self.nexus.isChecked():
                schema = "nexus"
            else:
                schema = "newick"

            data = dendropy.TreeList()
            for file in self.inputFiles:
                data.read(path=file, schema=schema, preserve_underscores=True)

            # Raise exception is found no tree data.
            if len(data) == 0:
                raise Exception("No tree data found in data file")

            # If it's the first time being clicked, set up the inital mapping,
            # which assumes only one individual for each species.
            if len(self.taxamap) == 0:
                for taxon in data.taxon_namespace:
                    self.taxamap[taxon.label] = taxon.label
            else:
                # If it's not the first time being clicked, check if user has changed input files.
                for taxon in data.taxon_namespace:
                    if taxon.label not in self.taxamap:
                        for taxon in data.taxon_namespace:
                            self.taxamap[taxon.label] = taxon.label
                        break

            # Execute TaxamapDlg
            dialog = TaxamapDlg.TaxamapDlg(data.taxon_namespace, self.taxamap, self)
            if dialog.exec_():
                self.taxamap = dialog.getTaxamap()
            #Update global attribute
            taxamap = self.taxamap
        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def generate(self):
        """
        Generate NEXUS file based on user input.
        """
        directory = QFileDialog.getSaveFileName(
            self, "Save File", "/", "Nexus Files (*.nexus)")

        class emptyFileError(Exception):
            pass

        class emptyNumReticulationError(Exception):
            pass

        class emptyDesinationError(Exception):
            pass

        try:
            if (not self.nexus.isChecked()) and (not self.newick.isChecked()):
                raise emptyFileError
            if len(self.inputFiles) == 0:
                raise emptyFileError
            if directory[0] == "":
                raise emptyDesinationError
            # the file format to read
            if self.nexus.isChecked():
                schema = "nexus"
            else:
                schema = "newick"

            # a TreeList that stores all the uploaded gene trees
            data = dendropy.TreeList()
            # read each uploaded file
            for file in self.inputFiles:
                fileName = os.path.splitext(os.path.basename(file))[0]
                currentFile = dendropy.TreeList()
                # read in gene trees
                currentFile.read(path=file, schema=schema, preserve_underscores=True)
                if len(currentFile) > 1:
                    # If a file contains multiple trees, assume those trees come from one locus
                    self.multiTreesPerLocus = True
                    counter = 0
                    currentLocus = []
                    for tree in currentFile:
                        # rename gene trees
                        tree.label = fileName + str(counter)
                        currentLocus.append(tree.label)
                        counter += 1
                    self.geneTreeNames.append(currentLocus)
                    data.extend(currentFile)
                else:
                    # If a file contains only one tree, assume only that tree comes from that locus
                    for tree in currentFile:
                        tree.label = fileName
                        self.geneTreeNames.append(tree.label)
                    data.extend(currentFile)

            # Raise exception is found no tree data.
            if len(data) == 0:
                raise Exception("No tree data found in data file")

            # Write out TREES block.
            path = str(directory[0])
            data.write(path=path, schema="nexus", suppress_taxa_blocks=True, unquoted_underscores=True)

            # Ready to write PHYLONET block.
            with open(path, "a") as outputFile:
                outputFile.write("\nBEGIN PHYLONET;\n\n")
                outputFile.write("Infernetwork_ML_CV (")
                # Write out all the gene tree names.
                if not self.multiTreesPerLocus:
                    # If there's only one tree per locus, write a comma delimited list of gene tree identifiers.
                    outputFile.write(self.geneTreeNames[0])
                    for genetree in self.geneTreeNames[1:]:
                        outputFile.write(",")
                        outputFile.write(genetree)
                    outputFile.write(") ")
                else:
                    # If there are multiple trees per locus, write a comma delimited list of sets of gene tree
                    # identifiers.
                    if type(self.geneTreeNames[0]) is list:
                        outputFile.write("{")
                        outputFile.write(self.geneTreeNames[0][0])
                        for genetree in self.geneTreeNames[0][1:]:
                            outputFile.write(",")
                            outputFile.write(genetree)
                        outputFile.write("}")
                    else:
                        outputFile.write("{")
                        outputFile.write(self.geneTreeNames[0])
                        outputFile.write("}")

                    for locus in self.geneTreeNames[1:]:
                        outputFile.write(",")
                        if type(locus) is list:
                            outputFile.write("{")
                            outputFile.write(locus[0])
                            for genetree in locus[1:]:
                                outputFile.write(",")
                                outputFile.write(genetree)
                            outputFile.write("}")
                        else:
                            outputFile.write("{")
                            outputFile.write(locus)
                            outputFile.write("}")
                    outputFile.write(") ")

                # Write out maximum number of reticulation to add.
                outputFile.write(str(self.numReticulationsEdit.text()))

                # -a taxa map command
                if self.taxamapLbl.isChecked():
                    if len(self.taxamap) == 0:
                        pass
                    else:
                        # Get a mapping from species to taxon.
                        speciesToTaxonMap = self.__inverseMapping(self.taxamap)
                        # Write taxa map.
                        outputFile.write(" -a <")
                        for firstSpecies in speciesToTaxonMap:
                            outputFile.write(firstSpecies)
                            outputFile.write(":")
                            outputFile.write(speciesToTaxonMap[firstSpecies][0])
                            for taxon in speciesToTaxonMap[firstSpecies][1:]:
                                outputFile.write(",")
                                outputFile.write(taxon)
                            speciesToTaxonMap.pop(firstSpecies)
                            break
                        for species in speciesToTaxonMap:
                            outputFile.write("; ")
                            outputFile.write(species)
                            outputFile.write(":")
                            outputFile.write(speciesToTaxonMap[species][0])
                            for taxon in speciesToTaxonMap[species][1:]:
                                outputFile.write(",")
                                outputFile.write(taxon)

                        outputFile.write(">")
                # -cv numfolds command
                if self.numFoldsLbl.isChecked():
                    if self.numFoldsEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -cv ")
                        outputFile.write(str(self.numFoldsEdit.text()))

                # -b threshold command
                if self.thresholdLbl.isChecked():
                    if self.thresholdEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -b ")
                        outputFile.write(str(self.thresholdEdit.text()))

                # -s startingNetwork command
                if self.sNetLbl.isChecked():
                    if self.sNetEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -s ")
                        outputFile.write(str(self.sNetEdit.text()))

                # -h {s1 [, s2...]} command
                if self.hybridLbl.isChecked():
                    if self.hybridEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -h ")
                        outputFile.write(str(self.hybridEdit.text()))

                # -w (w1, ..., w6) command
                if self.wetOpLbl.isChecked():
                    if self.wetOpEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -w ")
                        outputFile.write(str(self.wetOpEdit.text()))

                # -x numRuns command
                if self.numRunLbl.isChecked():
                    if self.numRunEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -x ")
                        outputFile.write(str(self.numRunEdit.text()))

                # -m maxNetExamined command
                if self.nNetExamLbl.isChecked():
                    if self.nNetExamEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -m ")
                        outputFile.write(str(self.nNetExamEdit.text()))

                # -md maxDiameter command
                if self.maxDiaLbl.isChecked():
                    if self.maxDiaEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -md ")
                        outputFile.write(str(self.maxDiaEdit.text()))

                # -rd reticulationDiameter command
                if self.retDiaLbl.isChecked():
                    if self.retDiaEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -rd ")
                        outputFile.write(str(self.retDiaEdit.text()))

                # -o command
                if self.oLabel.isChecked():
                    outputFile.write(" -o")

                # -p command
                if self.stopCriterionLbl.isChecked():
                    if self.stopCriterionEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -p ")
                        outputFile.write(str(self.stopCriterionEdit.text()))

                # -r command
                if self.maxRoundLbl.isChecked():
                    if self.maxRoundEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -r ")
                        outputFile.write(str(self.maxRoundEdit.text()))

                # -t command
                if self.maxTryPerBrLbl.isChecked():
                    if self.maxTryPerBrEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -t ")
                        outputFile.write(str(self.maxTryPerBrEdit.text()))

                # -i command
                if self.improveThresLbl.isChecked():
                    if self.improveThresEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -i ")
                        outputFile.write(str(self.improveThresEdit.text()))

                # -l command
                if self.maxBlLbl.isChecked():
                    if self.maxBlEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -l ")
                        outputFile.write(str(self.maxBlEdit.text()))

                # -pl numProcessors command
                if self.numProcLbl.isChecked():
                    if self.numProcEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.numProcEdit.text()))

                # -di command
                if self.diLbl.isChecked():
                    outputFile.write(" -di")


                # End of NEXUS
                outputFile.write(";\n\n")
                outputFile.write("END;")

            # Validate the generated file.
            self.validateFile(path)
            #clears inputs if they are validated
            if self.isValidated:
                self.clear()
                self.generated.emit(True)
                self.successMessage()

        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except emptyDesinationError:
            QMessageBox.warning(self, "Warning", "Please specify destination for generated NEXUS file.", QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def clear(self):
        """
        CLear page's field
        """
        self.geneTreeNames = []
        self.inputFiles = []
        self.taxamap = {}
        self.multiTreesPerLocus = False

        self.nexus.setChecked(False)
        self.newick.setChecked(False)
        self.geneTreesEdit.clear()
        self.numReticulationsEdit.clear()

        self.numFoldsLbl.setChecked(False)
        self.numFoldsEdit.clear()
        self.thresholdLbl.setChecked(False)
        self.thresholdEdit.clear()
        self.taxamapLbl.setChecked(False)
        self.sNetLbl.setChecked(False)
        self.sNetEdit.clear()
        self.nNetExamLbl.setChecked(False)
        self.nNetExamEdit.clear()
        self.maxDiaLbl.setChecked(False)
        self.maxDiaEdit.clear()
        self.hybridLbl.setChecked(False)
        self.hybridEdit.clear()
        self.wetOpLbl.setChecked(False)
        self.wetOpEdit.clear()
        self.retDiaLbl.setChecked(False)
        self.retDiaEdit.clear()
        self.stopCriterionLbl.setChecked(False)
        self.stopCriterionEdit.clear()
        self.oLabel.setChecked(False)
        self.numRunLbl.setChecked(False)
        self.numRunEdit.clear()
        self.maxRoundLbl.setChecked(False)
        self.maxRoundEdit.clear()
        self.maxTryPerBrLbl.setChecked(False)
        self.maxTryPerBrEdit.clear()
        self.improveThresLbl.setChecked(False)
        self.improveThresEdit.clear()
        self.branchlengthLbl.setChecked(False)
        self.maxBlLbl.setChecked(False)
        self.maxBlEdit.clear()
        self.numProcLbl.setChecked(False)
        self.numProcEdit.clear()
        self.diLbl.setChecked(False)     

    def successMessage(self):
        msg = QDialog()
        msg.setWindowTitle("Phylonet") 
        msg.setWindowIcon(QIcon("logo.png"))
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint )
        msg.setWindowFlags(flags)
        msg.setObjectName("successMessage")

        vbox = QVBoxLayout()

        ico = QLabel()
        complete = QPixmap("module/complete.svg")
        ico.setPixmap(complete)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.clicked.connect(msg.accept)

        vbox.addWidget(ico, alignment=QtCore.Qt.AlignCenter)
        vbox.addWidget(buttonBox)
        vbox.setSpacing(0)
 
        msg.setLayout(vbox)
        msg.setModal(1)
        msg.exec_()

    def validateFile(self, filePath):
        """
        After the .nexus file is generated, validate the file by feeding it to PhyloNet.
        Specify -checkParams on command line to make sure PhyloNet checks input without executing the command.
        """
  
        try:
            subprocess.check_output(
                ["java", "-jar", resource_path("module/testphylonet.jar"),
                 filePath, "checkParams"], stderr=subprocess.STDOUT)
            self.isValidated = True
        except subprocess.CalledProcessError as e:
            # If an error is encountered, delete the generated file and display the error to user.
            self.isValidated = False
            msg = e.output.decode("utf-8")
            msg = msg.replace("\n", "", 1)
            os.remove(filePath)
            QMessageBox.warning(self, "Warning", msg, QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkMLCVPage()
    ex.show()
    sys.exit(app.exec_())