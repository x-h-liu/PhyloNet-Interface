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
from module import diploidList
from module import paramList
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

class MCMCSEQPage(QWizardPage):
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
        super(MCMCSEQPage, self).__init__()

        self.inputFiles = []
        self.loci = {}
        self.nchar = 0
        self.taxa_names = set([])

        self.taxamap = {}
        self.sgtFiles = []
        self.ListOfDiploid = []
        self.GTR = {"A": "0.25", "C": "0.25", "G": "0.25", "T": "0.25", "AC": "1", "AG": "1", "AT": "1", "CG": "1",
       "CT": "1", "GT": "1"}
        self.TABS = 4

        self.isValidated = False
        self.initUI()

    def initUI(self):
        titleLabel = titleHeader("MCMC_SEQ")

        hyperlink = QLabel()
        hyperlink.setText(' For more details '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_SEQ">'
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
        self.fasta = QCheckBox(".fasta")
        self.fasta.setObjectName("fasta")
        numReticulationsLbl = QLabel("Maximum number of reticulations to add:")
        # Implement mutually exclusive check boxes
        self.nexus.stateChanged.connect(self.format)
        self.fasta.stateChanged.connect(self.format)

        # Mandatory parameter inputs
        self.sequenceFileEdit = QTextEdit()
        self.sequenceFileEdit.textChanged.connect(self.inspectInputs)
        self.sequenceFileEdit.setReadOnly(False)
        self.sequenceFileEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

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
        fileFormatLayout.addWidget(self.fasta)
        geneTreeDataLayout = QHBoxLayout()
        geneTreeDataLayout.addWidget(self.sequenceFileEdit)
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
        self.sNetLbl = QCheckBox("The starting network:")
        self.sNetLbl.setObjectName("-snet")
        self.sNetLbl.stateChanged.connect(self.onChecked)

        self.chainLengthLbl = QCheckBox("The length of the MCMC chain:", self)
        self.chainLengthLbl.setObjectName("-cl")
        self.chainLengthLbl.stateChanged.connect(self.onChecked)

        self.burnInLengthLbl = QCheckBox(
            "The number of iterations in burn-in period:", self)
        self.burnInLengthLbl.setObjectName("-bl")
        self.burnInLengthLbl.stateChanged.connect(self.onChecked)

        self.sampleFrequencyLbl = QCheckBox("The sample frequency:", self)
        self.sampleFrequencyLbl.setObjectName("-sf")
        self.sampleFrequencyLbl.stateChanged.connect(self.onChecked)

        self.seedLbl = QCheckBox("The random seed:", self)
        self.seedLbl.setObjectName("-sd")
        self.seedLbl.stateChanged.connect(self.onChecked)

        self.numProcLbl = QCheckBox(
            "Number of threads running in parallel:", self)
        self.numProcLbl.setObjectName("-pl")
        self.numProcLbl.stateChanged.connect(self.onChecked)

        self.tempListLbl = QCheckBox(
            "The list of temperatures for the Metropolis-coupled MCMC chains:", self)
        self.tempListLbl.setObjectName("-mc3")
        self.tempListLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)
        self.sNetEdit.setPlaceholderText("")

        self.chainLengthEdit = QLineEdit()
        self.chainLengthEdit.setDisabled(True)
        self.chainLengthEdit.setPlaceholderText("10000000")

        self.burnInLengthEdit = QLineEdit()
        self.burnInLengthEdit.setDisabled(True)
        self.burnInLengthEdit.setPlaceholderText("2000000")

        self.sampleFrequencyEdit = QLineEdit()
        self.sampleFrequencyEdit.setDisabled(True)
        self.sampleFrequencyEdit.setPlaceholderText("5000")

        self.seedEdit = QLineEdit()
        self.seedEdit.setDisabled(True)
        self.seedEdit.setPlaceholderText("12345678")

        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)

        self.tempListEdit = QLineEdit()
        self.tempListEdit.setDisabled(True)
        self.tempListEdit.setPlaceholderText("(1.0)")

        # Layouts
        # Layout of each parameter (label and input)
        sNetLayout = QHBoxLayout()
        sNetLayout.addWidget(self.sNetLbl)
        sNetLayout.addWidget(self.sNetEdit)

        chainLengthLayout = QHBoxLayout()
        chainLengthLayout.addWidget(self.chainLengthLbl)
        chainLengthLayout.addStretch(1)
        chainLengthLayout.addWidget(self.chainLengthEdit)

        burnInLengthLayout = QHBoxLayout()
        burnInLengthLayout.addWidget(self.burnInLengthLbl)
        burnInLengthLayout.addStretch(1)
        burnInLengthLayout.addWidget(self.burnInLengthEdit)

        sampleFrequencyLayout = QHBoxLayout()
        sampleFrequencyLayout.addWidget(self.sampleFrequencyLbl)
        sampleFrequencyLayout.addStretch(1)
        sampleFrequencyLayout.addWidget(self.sampleFrequencyEdit)

        seedLayout = QHBoxLayout()
        seedLayout.addWidget(self.seedLbl)
        seedLayout.addStretch(1)
        seedLayout.addWidget(self.seedEdit)

        numProcLayout = QHBoxLayout()
        numProcLayout.addWidget(self.numProcLbl)
        numProcLayout.addStretch(1)
        numProcLayout.addWidget(self.numProcEdit)

        tempListLayout = QHBoxLayout()
        tempListLayout.addWidget(self.tempListLbl)
        tempListLayout.addWidget(self.tempListEdit)

        # Main Layout tab two
        tabTwoLayout = QVBoxLayout()
        tabTwoLayout.addWidget(optionalLabel)
        tabTwoLayout.addLayout(sNetLayout)
        tabTwoLayout.addLayout(chainLengthLayout)
        tabTwoLayout.addLayout(burnInLengthLayout)
        tabTwoLayout.addLayout(sampleFrequencyLayout)
        tabTwoLayout.addLayout(seedLayout)
        tabTwoLayout.addLayout(numProcLayout)
        tabTwoLayout.addLayout(tempListLayout)
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
        self.maxRetLbl = QCheckBox(
            "The maximum number of reticulation nodes in the sampled phylogenetic networks:", self)
        self.maxRetLbl.setObjectName("-mr")
        self.maxRetLbl.stateChanged.connect(self.onChecked)

        self.taxamapLbl = QCheckBox(
            "Gene tree / species tree taxa association:", self)
        self.taxamapLbl.setObjectName("-tm")
        self.taxamapLbl.stateChanged.connect(self.onChecked)

        self.popSizeLbl = QCheckBox(
            "Fix the population sizes associated with all branches of the phylogenetic network " "to this given value:", self)
        self.popSizeLbl.setObjectName("-fixps")
        self.popSizeLbl.stateChanged.connect(self.onChecked)

        self.varypsLbl = QCheckBox(
            "Vary the population sizes across all branches.", self)
 
        self.ppLbl = QCheckBox(
            "The Poisson parameter in the prior on the number of reticulation nodes:", self)
        self.ppLbl.setObjectName("-pp")
        self.ppLbl.stateChanged.connect(self.onChecked)

        self.ddLbl = QCheckBox(
            "Disable the prior on the diameters of hybridizations.", self)

        self.eeLbl = QCheckBox("Enable the Exponential(10) prior on the divergence times of nodes in the phylogenetic "
                               "network.", self)

        # Optional parameter inputs
        self.maxRetEdit = QLineEdit()
        self.maxRetEdit.setDisabled(True)
        self.maxRetEdit.setPlaceholderText("4")

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setObjectName("taxamapEdit")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.popSizeEdit = QLineEdit()
        self.popSizeEdit.setDisabled(True)

        self.ppEdit = QLineEdit()
        self.ppEdit.setDisabled(True)
        self.ppEdit.setPlaceholderText("1.0")

        # Layouts
        # Layout of each parameter (label and input)      

        maxRetLayout = QHBoxLayout()
        maxRetLayout.addWidget(self.maxRetLbl)
        maxRetLayout.addStretch(1)
        maxRetLayout.addWidget(self.maxRetEdit)

        taxamapLayout = QHBoxLayout()
        taxamapLayout.addWidget(self.taxamapLbl)
        taxamapLayout.addStretch(1)
        taxamapLayout.addWidget(self.taxamapEdit)

        popSizeLayout = QHBoxLayout()
        popSizeLayout.addWidget(self.popSizeLbl)
        popSizeLayout.addStretch(1)
        popSizeLayout.addWidget(self.popSizeEdit)

        varypsLayout = QHBoxLayout()
        varypsLayout.addWidget(self.varypsLbl)

        ppLayout = QHBoxLayout()
        ppLayout.addWidget(self.ppLbl)
        ppLayout.addStretch(1)
        ppLayout.addWidget(self.ppEdit)

        ddLayout = QHBoxLayout()
        ddLayout.addWidget(self.ddLbl)

        eeLayout = QHBoxLayout()
        eeLayout.addWidget(self.eeLbl)

        # Main Layout tab three

        tabThreeLayout = QVBoxLayout()
        tabThreeLayout.addWidget(optionalLabelA)
        #tabThreeLayout.addLayout(sNetLayout)
        tabThreeLayout.addLayout(maxRetLayout)
        tabThreeLayout.addLayout(taxamapLayout)
        tabThreeLayout.addLayout(popSizeLayout)
        tabThreeLayout.addLayout(varypsLayout)
        tabThreeLayout.addLayout(ppLayout)
        tabThreeLayout.addLayout(ddLayout)
        tabThreeLayout.addLayout(eeLayout)

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
        self.sgtFileLbl = QCheckBox("Starting gene trees for each locus:")
        self.sgtFileLbl.setObjectName("-sgt")
        self.sgtFileLbl.stateChanged.connect(self.onChecked)

        #self.sNetLbl = QCheckBox("The starting network:")
        #self.sNetLbl.setObjectName("-snet")
        #self.sNetLbl.stateChanged.connect(self.onChecked)

        self.sPopLbl = QCheckBox("The starting population size:")
        self.sPopLbl.setObjectName("-sps")
        self.sPopLbl.stateChanged.connect(self.onChecked)

        self.preLbl = QCheckBox("The number of iterations for pre burn-in:")
        self.preLbl.setObjectName("-pre")
        self.preLbl.stateChanged.connect(self.onChecked)

        self.gtrLbl = QCheckBox(
            "Set GTR (general time-reversible) as the substitution model:")
        self.gtrLbl.setObjectName("-gtr")
        self.gtrLbl.stateChanged.connect(self.onChecked)

        self.diploidLbl = QCheckBox("Diploid species list:")
        self.diploidLbl.setObjectName("-diploid")
        self.diploidLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs

        self.sgtFileEdit = QLineEdit()
        self.sgtFileEdit.setDisabled(True)
        self.sgtFileEdit.setReadOnly(True)

        self.sgtFileSelctionBtn = QToolButton()
        self.sgtFileSelctionBtn.setText("Browse")
        self.sgtFileSelctionBtn.setObjectName("sgtFileSelctionBtn")
        self.sgtFileSelctionBtn.clicked.connect(self.selectSgtFile)
        self.sgtFileSelctionBtn.setDisabled(True)

        #self.sNetEdit = QLineEdit()
        #self.sNetEdit.setDisabled(True)
        #self.sNetEdit.setPlaceholderText("")

        self.sPopEdit = QLineEdit()
        self.sPopEdit.setDisabled(True)
        self.sPopEdit.setPlaceholderText("0.036")

        self.preEdit = QLineEdit()
        self.preEdit.setDisabled(True)
        self.preEdit.setPlaceholderText("10")

        self.gtrEdit = QPushButton("Set model")
        self.gtrEdit.setObjectName("gtrEdit")
        self.gtrEdit.setDisabled(True)
        self.gtrEdit.clicked.connect(self.getGTR)

        self.diploidEdit = QPushButton("Set diploid species")
        self.diploidEdit.setObjectName("diploidEdit")
        self.diploidEdit.setDisabled(True)
        self.diploidEdit.clicked.connect(self.getDiploid)

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        # Layouts
        # Layout of each parameter (label and input)

        sgtFileFormatLayout = QVBoxLayout()
        sgtFileFormatLayout.addWidget(self.sgtFileLbl)
        sgtInputLayout = QHBoxLayout()
        sgtInputLayout.addWidget(self.sgtFileEdit)
        sgtInputLayout.addWidget(self.sgtFileSelctionBtn)
        sgtFileLayout = QVBoxLayout()
        sgtFileLayout.addLayout(sgtFileFormatLayout)
        sgtFileLayout.addLayout(sgtInputLayout)

        #sNetLayout = QHBoxLayout()
        #sNetLayout.addWidget(self.sNetLbl)
        #sNetLayout.addWidget(self.sNetEdit)

        sPopLayout = QHBoxLayout()
        sPopLayout.addWidget(self.sPopLbl)
        sPopLayout.addStretch(1)
        sPopLayout.addWidget(self.sPopEdit)

        preLayout = QHBoxLayout()
        preLayout.addWidget(self.preLbl)
        preLayout.addStretch(1)
        preLayout.addWidget(self.preEdit)

        gtrLayout = QHBoxLayout()
        gtrLayout.addWidget(self.gtrLbl)
        gtrLayout.addStretch(1)
        gtrLayout.addWidget(self.gtrEdit)

        diploidLayout = QHBoxLayout()
        diploidLayout.addWidget(self.diploidLbl)
        diploidLayout.addStretch(1)
        diploidLayout.addWidget(self.diploidEdit)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)

        # Main Layout tab four

        tabFourLayout = QVBoxLayout()
        tabFourLayout.addWidget(optionalLabelB)
        tabFourLayout.addLayout(sgtFileFormatLayout)
        #tabFourLayout.addLayout(sNetLayout)
        tabFourLayout.addLayout(sPopLayout)
        tabFourLayout.addLayout(preLayout)
        tabFourLayout.addLayout(gtrLayout)
        tabFourLayout.addLayout(diploidLayout)
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
        if self.sequenceFileEdit.document().isEmpty() or self.numReticulationsEdit.text() == "":
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
                self.sequenceFileEdit.clear()
                self.inputFiles = []
                self.loci = {}
                self.taxamap = {}
            else:
                self.fasta.setChecked(False)
        elif self.sender().objectName() == "fasta":
            if not self.fasta.isChecked():
                self.sequenceFileEdit.clear()
                self.inputFiles = []
                self.loci = {}
                self.taxamap = {}
            else:
                self.nexus.setChecked(False)
                self.fasta.setChecked(True)

    def selectFile(self):
        """
        Read and store all the user uploaded sequence files. Read a file as soon as user uploads it.
        Store information in a dictionary, where keys are file names(loci names), and values are tuples
        containing the length of sequences in each file and the dna character matrix.
        Execute when file selection button is clicked.
        """
        if (not self.fasta.isChecked()) and (not self.nexus.isChecked()):
            QMessageBox.warning(self, "Warning", "Please select a file type.", QMessageBox.Ok)
        else:
            if self.nexus.isChecked():
                fname = QFileDialog.getOpenFileNames(self, 'Open file', '/', 'Nexus files (*.nexus *.nex)')
            elif self.fasta.isChecked():
                fname = QFileDialog.getOpenFileNames(self, 'Open file', '/', 'Fasta files (*.fasta)')
            #if a file has been inputted, proceed
            if len(fname[0]) > 0:
                fileType = fname[1]
                if self.nexus.isChecked():
                    if fileType != 'Nexus files (*.nexus *.nex)':
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus or .nex files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            # Read in sequences from one file.
                            dna = dendropy.DnaCharacterMatrix.get(path=str(onefname), schema="nexus"
                                                                      , preserve_underscores=True)
                            # Get the length of sequences in this file, and accumulate lengths of sequences in
                            # all input files
                            self.nchar = 0
                            for seq in dna.values():
                                seqLen = len(seq)
                                self.nchar += seqLen
                                break
                            for taxon in dna:
                                self.taxa_names.add(taxon.label)
                            # Store data from this file in loci dictionary
                            self.loci[os.path.splitext(os.path.basename(str(onefname)))[0]] = [seqLen, dna]
                            self.sequenceFileEdit.append(onefname)
                            self.inputFiles.append(str(onefname))

                elif self.fasta.isChecked():
                    if fileType != 'Fasta files (*.fasta)':
                        QMessageBox.warning(self, "Warning", "Please upload only .fasta files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            # Read in sequences from one file.
                            dna = dendropy.DnaCharacterMatrix.get(path=str(onefname), schema="fasta")
                            # Get the length of sequences in this file, and accumulate lengths of sequences in
                            # all input files
                            self.nchar = 0
                            for seq in dna.values():
                                seqLen = len(seq)
                                self.nchar += seqLen
                                break
                            # Store all taxa encountered so far in a global set.
                            for taxon in dna:
                                self.taxa_names.add(taxon.label)
                            # Store data from this file in loci dictionary
                            self.loci[os.path.splitext(os.path.basename(str(onefname)))[0]] = [seqLen, dna]
                            self.sequenceFileEdit.append(onefname)
                            self.inputFiles.append(str(onefname))
                else:
                    return

    def onChecked(self):
        """
        When user clicks the checkbox for an optional command,
        enable or disable the corresponding text edit.
        """
        if self.sender().objectName() == "-cl":
            if self.chainLengthEdit.isEnabled():
                self.chainLengthEdit.setDisabled(True)
            else:
                self.chainLengthEdit.setDisabled(False)
        elif self.sender().objectName() == "-bl":
            if self.burnInLengthEdit.isEnabled():
                self.burnInLengthEdit.setDisabled(True)
            else:
                self.burnInLengthEdit.setDisabled(False)
        elif self.sender().objectName() == "-sf":
            if self.sampleFrequencyEdit.isEnabled():
                self.sampleFrequencyEdit.setDisabled(True)
            else:
                self.sampleFrequencyEdit.setDisabled(False)
        elif self.sender().objectName() == "-sd":
            if self.seedEdit.isEnabled():
                self.seedEdit.setDisabled(True)
            else:
                self.seedEdit.setDisabled(False)
        elif self.sender().objectName() == "-pl":
            if self.numProcEdit.isEnabled():
                self.numProcEdit.setDisabled(True)
            else:
                self.numProcEdit.setDisabled(False)
        elif self.sender().objectName() == "-mc3":
            if self.tempListEdit.isEnabled():
                self.tempListEdit.setDisabled(True)
            else:
                self.tempListEdit.setDisabled(False)
        elif self.sender().objectName() == "-mr":
            if self.maxRetEdit.isEnabled():
                self.maxRetEdit.setDisabled(True)
            else:
                self.maxRetEdit.setDisabled(False)
        elif self.sender().objectName() == "-tm":
            if self.taxamapEdit.isEnabled():
                self.taxamapEdit.setDisabled(True)
            else:
                self.taxamapEdit.setDisabled(False)
        elif self.sender().objectName() == "-fixps":
            if self.popSizeEdit.isEnabled():
                self.popSizeEdit.setDisabled(True)
            else:
                self.popSizeEdit.setDisabled(False)
        elif self.sender().objectName() == "-pp":
            if self.ppEdit.isEnabled():
                self.ppEdit.setDisabled(True)
            else:
                self.ppEdit.setDisabled(False)   
        elif self.sender().objectName() == "-sgt":
            if self.sgtFileEdit.isEnabled():
                self.sgtFileEdit.setDisabled(True)
                self.sgtFileSelctionBtn.setDisabled(True)
            else:
                self.sgtFileEdit.setDisabled(False)
                self.sgtFileSelctionBtn.setDisabled(False)
        elif self.sender().objectName() == "-snet":
            if self.sNetEdit.isEnabled():
                self.sNetEdit.setDisabled(True)
            else:
                self.sNetEdit.setDisabled(False)
        elif self.sender().objectName() == "-sps":
            if self.sPopEdit.isEnabled():
                self.sPopEdit.setDisabled(True)
            else:
                self.sPopEdit.setDisabled(False)
        elif self.sender().objectName() == "-pre":
            if self.preEdit.isEnabled():
                self.preEdit.setDisabled(True)
            else:
                self.preEdit.setDisabled(False)
        elif self.sender().objectName() == "-gtr":
            if self.gtrEdit.isEnabled():
                self.gtrEdit.setDisabled(True)
            else:
                self.gtrEdit.setDisabled(False)
        elif self.sender().objectName() == "-diploid":
            if self.diploidEdit.isEnabled():
                self.diploidEdit.setDisabled(True)
            else:
                self.diploidEdit.setDisabled(False)     
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

            # Create a taxon_namespace object based on current taxa names set.
            taxa = dendropy.TaxonNamespace()
            for taxon in list(self.taxa_names):
                taxa.add_taxon(dendropy.Taxon(taxon))

            # If it's the first time being clicked, set up the initial mapping,
            # which assumes only one individual for each species.
            if len(self.taxamap) == 0:
                for taxon in taxa:
                    self.taxamap[taxon.label] = taxon.label
            else:
                # If it's not the first time being clicked, check if user has changed input files.
                for taxon in taxa:
                    if taxon.label not in self.taxamap:
                        for taxon in taxa:
                            self.taxamap[taxon.label] = taxon.label
                        break

            # Execute TaxamapDlg
            dialog = TaxamapDlg.TaxamapDlg(taxa, self.taxamap, self)
            if dialog.exec_():
                self.taxamap = dialog.getTaxamap()
        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def sgtFormat(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        Only one of .nexus and .newick can be selected.
        """
        if self.sender().objectName() == "sgtNexus":
            if not self.sgtNexus.isChecked():
                pass
            else:
                self.sgtNewick.setChecked(False)
                # Clear stored starting gene tree files.
                self.sgtFileEdit.clear()
                self.sgtFiles = []
        elif self.sender().objectName() == "sgtNewick":
            if not self.sgtNewick.isChecked():
                pass
            else:
                self.sgtNexus.setChecked(False)
                # Clear stored starting gene tree files.
                self.sgtFileEdit.clear()
                self.sgtFiles = []

    def selectSgtFile(self):
        """
        Store all the user uploaded starting gene tree file names. Reading happens in the "generate" function.
        Files should be uploaded in the same order as loci.
        Each file should contain only one gene tree (Or multiple gene trees, as long as gene trees themselves
        are in the same order as loci).
        Execute when starting gene tree file selection button is clicked.
        """
        fname = QFileDialog.getOpenFileName(
            self, 'Open file', '/', 'Nexus files (*.nexus *.nex);; Newick files (*.newick)')
        if fname[1] == 'Nexus files (*.nexus *.nex)':
            # Store the file name in a global list.
            self.sgtFileEdit.insert(fname[0])
            self.sgtFiles.append(str(fname[0]))
        elif fname[1] == 'Newick files (*.newick)':
            # Store the file name in a global list.
            self.sgtFileEdit.insert(fname[0])
            self.sgtFiles.append(str(fname[0]))
        else:
            return

    def getGTR(self):
        """
        Set general time-reversible as the substitution model.
        Open up a dialog for user to input ten parameters. Get result from the dialog and store as
        a global variable. Default parameters is JC69 model.
        """
        dialog = paramList.ParamListDlg(self.GTR, self)
        if dialog.exec_():
            self.GTR = dialog.getParamList()

    def getDiploid(self):
        """
        Set diploid species list.
        Open up a dialog for user to select diploid species. Get result from the dialog and store as
        a global variable.
        """
        class emptyFileError(Exception):
            pass

        try:
            if len(self.inputFiles) == 0:
                raise emptyFileError

            # Create a taxon_namespace object based on current taxa names set.
            taxa = dendropy.TaxonNamespace()
            for taxon in list(self.taxa_names):
                taxa.add_taxon(dendropy.Taxon(taxon))

            dialog = diploidList.DiploidListDlg(taxa, self.ListOfDiploid, self)

            if dialog.exec_():
                # If executed, update diploid species list.
                self.ListOfDiploid = dialog.getDiploidSpeciesList()

        except emptyFileError:
            QMessageBox.warning(
                self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return

    def generate(self):
        """
        Generate NEXUS file based on user input.
        """

        directory = QFileDialog.getSaveFileName(
            self, "Save File", "/", "Nexus Files (*.nexus)")

        class emptyFileError(Exception):
            pass

        class emptyDesinationError(Exception):
            pass

        try:
            if len(self.inputFiles) == 0:
                raise emptyFileError
            if directory[0] == "":
                raise emptyDesinationError

            # If user specifies starting gene trees, read gene tree files and write them to output NEXUS first.
            if self.sgtFileLbl.isChecked() and (self.sgtNexus.isChecked() or self.sgtNewick.isChecked()):
                if self.sgtNexus.isChecked():
                    schema = "nexus"
                else:
                    schema = "newick"

                # a TreeList that stores all the uploaded gene trees
                data = dendropy.TreeList()
                # All uploaded gene tree names
                geneTreeNames = []
                # read each uploaded file
                for file in self.sgtFiles:
                    fileName = os.path.splitext(os.path.basename(file))[0]
                    currentFile = dendropy.TreeList()
                    # read in gene trees
                    currentFile.read(path=file, schema=schema,
                                     preserve_underscores=True)
                    if len(currentFile) == 0:
                        raise Exception("No tree data found in gene tree file")
                    counter = 0
                    for tree in currentFile:
                        # rename gene trees
                        tree.label = fileName + str(counter)
                        geneTreeNames.append(tree.label)
                        counter += 1
                    data.extend(currentFile)

                # Write out TREES block.
                path = str(directory[0])
                data.write(path=path, schema="nexus",
                           suppress_taxa_blocks=True, unquoted_underscores=True)
            else:
                # If not, just create a file to write.
                path = str(directory[0])
            with open(path, "a") as outputFile:
                # Write #NEXUS or not depends on the existence of TREES block.
                if self.sgtFileLbl.isChecked() and (self.sgtNexus.isChecked() or self.sgtNewick.isChecked()):
                    outputFile.write("\n")
                else:
                    outputFile.write("#NEXUS\n")
                # Write headers of DATA block
                outputFile.write("Begin data;\n")
                outputFile.write("Dimensions ntax=")
                outputFile.write(str(len(self.taxa_names)))
                outputFile.write(" nchar=")
                outputFile.write(str(self.nchar))
                outputFile.write(";\n")
                outputFile.write(
                    'Format datatype=dna symbols="ACGTMRWSYK" missing=? gap=-;\n')
                outputFile.write("Matrix\n")

                # Write loci.
                for locus in self.loci:
                    outputFile.write("[")
                    outputFile.write(locus)
                    outputFile.write(", ")
                    outputFile.write(str(self.loci[locus][0]))
                    outputFile.write("]\n")

                    for taxon, seq in self.loci[locus][1].items():
                        outputFile.write(taxon.label)
                        outputFile.write(" ")
                        outputFile.write(seq.symbols_as_string())
                        outputFile.write("\n")
                outputFile.write(";END;\n")

                # Write PHYLONET block.
                outputFile.write("BEGIN PHYLONET;\n")
                outputFile.write("MCMC_SEQ")

                # Write optional commands based on user selection.
                if self.chainLengthLbl.isChecked():
                    if self.chainLengthEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -cl ")
                        outputFile.write(str(self.chainLengthEdit.text()))

                if self.burnInLengthLbl.isChecked():
                    if self.burnInLengthEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -bl ")
                        outputFile.write(str(self.burnInLengthEdit.text()))

                if self.sampleFrequencyLbl.isChecked():
                    if self.sampleFrequencyEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -sf ")
                        outputFile.write(str(self.sampleFrequencyEdit.text()))

                if self.seedLbl.isChecked():
                    if self.seedEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -sd ")
                        outputFile.write(str(self.seedEdit.text()))

                if self.numProcLbl.isChecked():
                    if self.numProcEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.numProcEdit.text()))

                if self.tempListLbl.isChecked():
                    if self.tempListEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -mc3 ")
                        outputFile.write(str(self.tempListEdit.text()))

                if self.maxRetLbl.isChecked():
                    if self.maxRetEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -mr ")
                        outputFile.write(str(self.maxRetEdit.text()))

                if self.taxamapLbl.isChecked():
                    if len(self.taxamap) == 0:
                        pass
                    else:
                        # Get a mapping from species to taxon.
                        speciesToTaxonMap = self.__inverseMapping(self.taxamap)
                        # Write taxa map.
                        outputFile.write(" -tm <")
                        for firstSpecies in speciesToTaxonMap:
                            outputFile.write(firstSpecies)
                            outputFile.write(":")
                            outputFile.write(
                                speciesToTaxonMap[firstSpecies][0])
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

                if self.popSizeLbl.isChecked():
                    if self.popSizeEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -fixps ")
                        outputFile.write(str(self.popSizeEdit.text()))

                if self.varypsLbl.isChecked():
                    outputFile.write(" -varyps")

                if self.ppLbl.isChecked():
                    if self.ppEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pp ")
                        outputFile.write(str(self.ppEdit.text()))

                if self.ddLbl.isChecked():
                    outputFile.write(" -dd")

                if self.eeLbl.isChecked():
                    outputFile.write(" -ee")

                if self.sgtFileLbl.isChecked() and (self.sgtNexus.isChecked() or self.sgtNewick.isChecked()):
                    # Write out all the gene tree names.
                    outputFile.write(" -sgt (")
                    outputFile.write(geneTreeNames[0])
                    for genetree in geneTreeNames[1:]:
                        outputFile.write(",")
                        outputFile.write(genetree)
                    outputFile.write(")")

                if self.sNetLbl.isChecked():
                    if self.sNetEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -snet ")
                        outputFile.write(str(self.sNetEdit.text()))

                if self.sPopLbl.isChecked():
                    if self.sPopEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -sps ")
                        outputFile.write(str(self.sPopEdit.text()))

                if self.preLbl.isChecked():
                    if self.preEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pre ")
                        outputFile.write(str(self.preEdit.text()))

                if self.gtrLbl.isChecked():
                    outputFile.write(" -gtr (")
                    outputFile.write(self.GTR["A"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["C"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["G"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["T"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["AC"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["AG"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["AT"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["CG"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["CT"])
                    outputFile.write(",")
                    outputFile.write(self.GTR["GT"])
                    outputFile.write(")")

                if self.diploidLbl.isChecked():
                    if len(self.ListOfDiploid) == 0:
                        pass
                    else:
                        outputFile.write(" -diploid (")
                        outputFile.write(self.ListOfDiploid[0])
                        for species in self.ListOfDiploid[1:]:
                            outputFile.write(",")
                            outputFile.write(species)
                        outputFile.write(")")

                outputFile.write(";\n")
                outputFile.write("END;")

            # Validate the generated file.
            self.validateFile(path)
            #clears inputs if they are validated      
            if self.isValidated:
                self.clear()
                self.generated.emit(True)
                self.successMessage()

        except emptyFileError:
            QMessageBox.warning(
                self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except emptyDesinationError:
            QMessageBox.warning(
                self, "Warning", "Please specify destination for generated NEXUS file.", QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def clear(self):
        """
        CLear page's field
        """
        self.inputFiles = []
        self.loci = {}
        self.nchar = 0
        self.taxa_names = set([])

        self.taxamap = {}
        self.sgtFiles = []
        self.ListOfDiploid = []

        self.nexus.setChecked(False)
        self.fasta.setChecked(False)
        self.sequenceFileEdit.clear()
        self.numReticulationsEdit.clear()

        self.chainLengthLbl.setChecked(False)
        self.chainLengthEdit.clear()
        self.burnInLengthLbl.setChecked(False)
        self.burnInLengthEdit.clear()
        self.sampleFrequencyLbl.setChecked(False)
        self.sampleFrequencyEdit.clear()
        self.seedLbl.setChecked(False)
        self.seedEdit.clear()
        self.numProcLbl.setChecked(False)
        self.numProcEdit.clear()
        self.tempListLbl.setChecked(False)
        self.tempListEdit.clear()

        self.maxRetLbl.setChecked(False)
        self.maxRetEdit.clear()
        self.taxamapLbl.setChecked(False)
        self.popSizeLbl.setChecked(False)
        self.popSizeEdit.clear()
        self.varypsLbl.setChecked(False)
        self.ppLbl.setChecked(False)
        self.ppEdit.clear()
        self.ddLbl.setChecked(False)
        self.eeLbl.setChecked(False)

        self.sgtFileLbl.setChecked(False)
        self.sgtFileEdit.clear()
        self.sNetLbl.setChecked(False)
        self.sNetEdit.clear()
        self.sPopLbl.setChecked(False)
        self.sPopEdit.clear()
        self.preLbl.setChecked(False)
        self.preEdit.clear()
        self.gtrLbl.setChecked(False)
        self.diploidLbl.setChecked(False) 

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
    ex = MCMCSEQPage()
    ex.show()
    sys.exit(app.exec_())
