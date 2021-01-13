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
from module import paramList
from functions import *

class MCMCBiMarkersPage(QWizardPage):
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
        super(MCMCBiMarkersPage, self).__init__()

        self.inputFiles = []
        self.nchar = 0
        self.taxa_names = set([])

        self.taxamap = {}

        self.TABS = 5

        self.isValidated = False
        self.initUI()

    def initUI(self):
        titleLabel = titleHeader("MCMC_BiMarkers")

        hyperlink = QLabel()
        hyperlink.setText(' For more details '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_BiMarkers">'
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
        instructionLabel.setText("Input data: Please Upload Sequence File")
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

        #Initialize Layouts each parameter

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
        optionalLabel.setText("MCMC and MC3 Settings")
        optionalLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels      
        self.chainLengthLbl = QCheckBox("The length of the MCMC chain:")
        self.chainLengthLbl.setObjectName("-cl")
        self.chainLengthLbl.stateChanged.connect(self.onChecked)

        self.burnInLengthLbl = QCheckBox(
            "The number of iterations in burn-in period:", self)
        self.burnInLengthLbl.setObjectName("-bl")
        self.burnInLengthLbl.stateChanged.connect(self.onChecked)

        self.sampleFrequencyLbl = QCheckBox("The sample frequency:")
        self.sampleFrequencyLbl.setObjectName("-sf")
        self.sampleFrequencyLbl.stateChanged.connect(self.onChecked)

        self.seedLbl = QCheckBox("The random seed:")
        self.seedLbl.setObjectName("-sd")
        self.seedLbl.stateChanged.connect(self.onChecked)

        self.parThreadLbl = QCheckBox(
            "The number of threads running in parallel:")
        self.parThreadLbl.setObjectName("-pl")
        self.parThreadLbl.stateChanged.connect(self.onChecked)

        self.tempListLbl = QCheckBox(
            "The list of temperatures for the Metropolis-coupled MCMC chains:", self)
        self.tempListLbl.setObjectName("-mc3")
        self.tempListLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.chainLengthEdit = QLineEdit()
        self.chainLengthEdit.setDisabled(True)
        self.chainLengthEdit.setPlaceholderText("500000")

        self.burnInEdit = QLineEdit()
        self.burnInEdit.setDisabled(True)
        self.burnInEdit.setPlaceholderText("200000")

        self.sampleFrequencyEdit = QLineEdit()
        self.sampleFrequencyEdit.setDisabled(True)
        self.sampleFrequencyEdit.setPlaceholderText("500")

        self.seedEdit = QLineEdit()
        self.seedEdit.setDisabled(True)
        self.seedEdit.setPlaceholderText("12345678")
        
        self.parThreadEdit = QLineEdit()
        self.parThreadEdit.setDisabled(True)

        self.tempListEdit = QLineEdit()
        self.tempListEdit.setDisabled(True)
        self.tempListEdit.setPlaceholderText("(1.0)")

        #Initialize Layouts each parameter 

        chainLengthLayout = QHBoxLayout()
        chainLengthLayout.addWidget(self.chainLengthLbl)
        chainLengthLayout.addStretch(1)
        chainLengthLayout.addWidget(self.chainLengthEdit)

        burnInLayout = QHBoxLayout()
        burnInLayout.addWidget(self.burnInLengthLbl)
        burnInLayout.addStretch(1)
        burnInLayout.addWidget(self.burnInEdit)

        sampleFrequencyLayout = QHBoxLayout()
        sampleFrequencyLayout.addWidget(self.sampleFrequencyLbl)
        sampleFrequencyLayout.addStretch(1)
        sampleFrequencyLayout.addWidget(self.sampleFrequencyEdit)

        seedLayout = QHBoxLayout()
        seedLayout.addWidget(self.seedLbl)
        seedLayout.addStretch(1)
        seedLayout.addWidget(self.seedEdit)

        parThreadLayout = QHBoxLayout()
        parThreadLayout.addWidget(self.parThreadLbl)
        parThreadLayout.addStretch(1)
        parThreadLayout.addWidget(self.parThreadEdit)

        tempListLayout = QHBoxLayout()
        tempListLayout.addWidget(self.tempListLbl)
        tempListLayout.addWidget(self.tempListEdit)

        # Main Layout tab two
        tabTwoLayout = QVBoxLayout()
        tabTwoLayout.addWidget(optionalLabel)
        tabTwoLayout.addLayout(chainLengthLayout)
        tabTwoLayout.addLayout(burnInLayout)
        tabTwoLayout.addLayout(sampleFrequencyLayout)
        tabTwoLayout.addLayout(seedLayout)
        tabTwoLayout.addLayout(parThreadLayout)
        tabTwoLayout.addLayout(tempListLayout)
        tabTwo.setLayout(tabTwoLayout)   

        #add tab two
        self.tabWidget.addTab(tabTwo, 'Parameters')
        
        #create tab three 
        tabThree = QWidget(self)

        optionalLabelA = QLabel()
        optionalLabelA.setObjectName("instructionLabel")
        optionalLabelA.setText("Inference Settings")
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

        self.thetaLbl = QCheckBox(
            "Fix the population mutation rates associated with all branches to this given value:")
        self.thetaLbl.setObjectName("-fixtheta")
        self.thetaLbl.stateChanged.connect(self.onChecked)

        self.varyThetaLbl = QCheckBox(
            "The population mutation rates across all branches may be different.")

        self.espThetaLbl = QCheckBox(
            "Estimate the mean value of prior of population mutation rates.")

        # Optional parameter inputs
        self.maxRetEdit = QLineEdit()
        self.maxRetEdit.setDisabled(True)
        self.maxRetEdit.setPlaceholderText("4")

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setObjectName("taxamapEdit")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.thetaEdit = QLineEdit()
        self.thetaEdit.setDisabled(True)

        #Initialize Layouts each parameter

        maxRetLayout = QHBoxLayout()
        maxRetLayout.addWidget(self.maxRetLbl)
        maxRetLayout.addStretch(1)
        maxRetLayout.addWidget(self.maxRetEdit)

        taxamapLayout = QHBoxLayout()
        taxamapLayout.addWidget(self.taxamapLbl)
        taxamapLayout.addStretch(1)
        taxamapLayout.addWidget(self.taxamapEdit)

        thetaLayout = QHBoxLayout()
        thetaLayout.addWidget(self.thetaLbl)
        thetaLayout.addStretch(1)
        thetaLayout.addWidget(self.thetaEdit)

        varyThetaLayout = QHBoxLayout()
        varyThetaLayout.addWidget(self.varyThetaLbl)

        espThetaLayout = QHBoxLayout()
        espThetaLayout.addWidget(self.espThetaLbl)

        # Main Layout tab three

        tabThreeLayout = QVBoxLayout()
        tabThreeLayout.addWidget(optionalLabelA)
        tabThreeLayout.addLayout(maxRetLayout)
        tabThreeLayout.addLayout(taxamapLayout)
        tabThreeLayout.addLayout(thetaLayout)
        tabThreeLayout.addLayout(varyThetaLayout)
        tabThreeLayout.addLayout(espThetaLayout)

        tabThree.setLayout(tabThreeLayout)          

        #add tabthree
        self.tabWidget.addTab(tabThree, 'Parameters')

        #create tab four 
        tabFour = QWidget(self)

        optionalLabelB = QLabel()
        optionalLabelB.setObjectName("instructionLabel")
        optionalLabelB.setText("Prior and Starting State Settings")
        optionalLabelB.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels
        self.ppLbl = QCheckBox(
            "The Poisson parameter in the prior on the number of reticulation nodes:")
        self.ppLbl.setObjectName("-pp")
        self.ppLbl.stateChanged.connect(self.onChecked)

        self.ddLbl = QCheckBox(
            "Disable the prior on the diameters of hybridizations.", self)

        self.eeLbl = QCheckBox("The Exponential parameter in the prior on the divergence times of nodes in the "
                               "phylogenetic network:", self)
        self.eeLbl.setObjectName("-ee")
        self.eeLbl.stateChanged.connect(self.onChecked)

        self.sNetLbl = QCheckBox("Specify the starting network:")
        self.sNetLbl.setObjectName("-snet")
        self.sNetLbl.stateChanged.connect(self.onChecked)

        self.startingThetaPriorLbl = QCheckBox(
            "Specify the mean value of prior of population mutation rate:")
        self.startingThetaPriorLbl.setObjectName("-ptheta")
        self.startingThetaPriorLbl.stateChanged.connect(self.onChecked)
        # Optional parameter inputs
        self.ppEdit = QLineEdit()
        self.ppEdit.setDisabled(True)
        self.ppEdit.setPlaceholderText("1.0")

        self.eeEdit = QLineEdit()
        self.eeEdit.setDisabled(True)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)

        self.startingThetaPriorEdit = QLineEdit()
        self.startingThetaPriorEdit.setDisabled(True)
        self.startingThetaPriorEdit.setPlaceholderText("0.036")

        #Initialize Layouts each parameter

        ppLayout = QHBoxLayout()
        ppLayout.addWidget(self.ppLbl)
        ppLayout.addStretch(1)
        ppLayout.addWidget(self.ppEdit)

        ddLayout = QHBoxLayout()
        ddLayout.addWidget(self.ddLbl)

        eeLayout = QHBoxLayout()
        eeLayout.addWidget(self.eeLbl)
        eeLayout.addStretch(1)
        eeLayout.addWidget(self.eeEdit)

        sNetLayout = QHBoxLayout()
        sNetLayout.addWidget(self.sNetLbl)
        sNetLayout.addWidget(self.sNetEdit)

        startingThetaPriorLayout = QHBoxLayout()
        startingThetaPriorLayout.addWidget(self.startingThetaPriorLbl)
        startingThetaPriorLayout.addStretch(1)
        startingThetaPriorLayout.addWidget(self.startingThetaPriorEdit)


        # Main Layout tab four

        tabFourLayout = QVBoxLayout()
        tabFourLayout.addWidget(optionalLabelB)
        tabFourLayout.addLayout(ppLayout)
        tabFourLayout.addLayout(ddLayout)
        tabFourLayout.addLayout(eeLayout)
        tabFourLayout.addLayout(sNetLayout)
        tabFourLayout.addLayout(startingThetaPriorLayout)

        tabFour.setLayout(tabFourLayout)          

        #add tabFour
        self.tabWidget.addTab(tabFour, 'Parameters')
        
        #create tab five 
        tabFive = QWidget(self)

        optionalLabelC = QLabel()
        optionalLabelC.setObjectName("instructionLabel")
        optionalLabelC.setText("Data Related Settings")
        optionalLabelC.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels
        self.diploidLbl = QCheckBox("Sequence sampled from diploids.")

        self.dominantMarkerLbl = QCheckBox(
            "Specify which marker is dominant if the data is dominant:")
        self.dominantMarkerLbl.setObjectName("-dominant")
        self.dominantMarkerLbl.stateChanged.connect(self.onChecked)

        self.opLbl = QCheckBox("Ignore all monomorphic sites.")

        # Optional parameter inputs
        self.dominantMarkerEdit = QComboBox(self)
        self.dominantMarkerEdit.addItem("0")
        self.dominantMarkerEdit.addItem("1")
        self.dominantMarkerEdit.setDisabled(True)

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        #Initialize Layouts each parameter
        diploidLayout = QHBoxLayout()
        diploidLayout.addWidget(self.diploidLbl)

        dominantMarkerLayout = QHBoxLayout()
        dominantMarkerLayout.addWidget(self.dominantMarkerLbl)
        dominantMarkerLayout.addStretch(1)
        dominantMarkerLayout.addWidget(self.dominantMarkerEdit)

        opLayout = QHBoxLayout()
        opLayout.addWidget(self.opLbl)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)

        # Main Layout tab five

        tabFiveLayout = QVBoxLayout()
        tabFiveLayout.addWidget(optionalLabelC)
        tabFiveLayout.addLayout(diploidLayout)
        tabFiveLayout.addLayout(dominantMarkerLayout)
        tabFiveLayout.addLayout(opLayout)
        tabFiveLayout.addLayout(btnLayout)

        tabFive.setLayout(tabFiveLayout)          

        #add tabFive
        self.tabWidget.addTab(tabFive, 'Generate')
        
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
                self.taxamap = {}
            else:
                self.fasta.setChecked(False)
        elif self.sender().objectName() == "fasta":
            if not self.fasta.isChecked():
                self.sequenceFileEdit.clear()
                self.inputFiles = []
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
                            # Store data from this file
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
                            # Store data from this file
                            self.sequenceFileEdit.append(onefname)
                            self.inputFiles.append(str(onefname))
                else:
                    return

    def onChecked(self):
        """
        When user clicks the checkbox for an optional command,
        enable or disable the corresponding input widget.
        """
        if self.sender().objectName() == "-cl":
            if self.chainLengthEdit.isEnabled():
                self.chainLengthEdit.setDisabled(True)
            else:
                self.chainLengthEdit.setDisabled(False)
        elif self.sender().objectName() == "-bl":
            if self.burnInEdit.isEnabled():
                self.burnInEdit.setDisabled(True)
            else:
                self.burnInEdit.setDisabled(False)
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
            if self.parThreadEdit.isEnabled():
                self.parThreadEdit.setDisabled(True)
            else:
                self.parThreadEdit.setDisabled(False)
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
        elif self.sender().objectName() == "-fixtheta":
            if self.thetaEdit.isEnabled():
                self.thetaEdit.setDisabled(True)
            else:
                self.thetaEdit.setDisabled(False)
        elif self.sender().objectName() == "-pp":
            if self.ppEdit.isEnabled():
                self.ppEdit.setDisabled(True)
            else:
                self.ppEdit.setDisabled(False)
        elif self.sender().objectName() == "-ee":
            if self.eeEdit.isEnabled():
                self.eeEdit.setDisabled(True)
            else:
                self.eeEdit.setDisabled(False)
        elif self.sender().objectName() == "-snet":
            if self.sNetEdit.isEnabled():
                self.sNetEdit.setDisabled(True)
            else:
                self.sNetEdit.setDisabled(False)
        elif self.sender().objectName() == "-ptheta":
            if self.startingThetaPriorEdit.isEnabled():
                self.startingThetaPriorEdit.setDisabled(True)
            else:
                self.startingThetaPriorEdit.setDisabled(False)
        elif self.sender().objectName() == "-dominant":
            if self.dominantMarkerEdit.isEnabled():
                self.dominantMarkerEdit.setDisabled(True)
            else:
                self.dominantMarkerEdit.setDisabled(False)
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

            path = str(directory[0])
            with open(path, "a") as outputFile:
                outputFile.write("#NEXUS\n")
                outputFile.write("Begin data;\n")
                #the 2000 is a place holder, this function has many missing parts
                outputFile.write("Dimensions ntax= 2000")

                outputFile.write(" nchar=")
                outputFile.write(str(self.nchar))
                outputFile.write(";\n")
                outputFile.write(
                    'Format datatype=dna symbols="012" missing=? gap=-;\n')
                outputFile.write("Matrix\n")
                outputFile.write(";End;\n\n")

                # Write PHYLONET block.
                outputFile.write("BEGIN PHYLONET;\n")
                outputFile.write("MCMC_BiMarkers")

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

                if self.parThreadLbl.isChecked():
                    if self.parThreadEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.parThreadEdit.text()))

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

                if self.thetaLbl.isChecked():
                    if self.thetaEdit.text() == "" :
                        pass
                    else:
                        outputFile.write(" -fixtheta ")
                        outputFile.write(str(self.thetaEdit.text()))

                if self.varyThetaLbl.isChecked():
                    outputFile.write(" -varytheta ")

                if self.espThetaLbl.isChecked():
                    outputFile.write(" -esptheta ")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
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
                if self.sNetLbl.isChecked():
                    if self.sNetEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -snet ")
                        outputFile.write(str(self.sNetEdit.text()))

                if self.startingThetaPriorLbl.isChecked():
                    if self.startingThetaPriorEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -ptheta ")
                        outputFile.write(str(self.startingThetaPriorEdit.text()))

                if self.diploidLbl.isChecked():
                    outputFile.write(" -diploid")

                if self.dominantMarkerLbl.isChecked():
                    outputFile.write(" -dominant ")
                    outputFile.write(str(self.dominantMarkerEdit.currentText()))

                if self.opLbl.isChecked():
                    outputFile.write(" -op")

                outputFile.write(";\n")
                outputFile.write("END;")
            
            # Validate the generated file.
            self.isValidated = validateFile(self, path)
            #clears inputs if they are validated      
            if self.isValidated:
                self.clear()
                self.generated.emit(True)
                successMessage(self)

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
        Clear page's field
        """
        self.inputFiles = []
        self.nchar = 0
        self.taxa_names = set([])

        self.taxamap = {}

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
        self.parThreadLbl.setChecked(False)
        self.parThreadEdit.clear()
        self.tempListLbl.setChecked(False)
        self.tempListEdit.clear()

        self.maxRetLbl.setChecked(False)
        self.maxRetEdit.clear()
        self.taxamapLbl.setChecked(False)
        self.thetaLbl.setChecked(False)
        self.thetaEdit.clear()
        #self.varyThetaLbl.setChecked(False)
        #self.espThetaLbl.setChecked(False)
        self.ppLbl.setChecked(False)
        self.ppEdit.clear()

        #self.ddLbl.setChecked(False)
        self.eeLbl.setChecked(False)
        self.sNetLbl.setChecked(False)
        self.sNetEdit.clear()

        self.startingThetaPriorLbl.setChecked(False)
        self.startingThetaPriorEdit.clear()
        #self.diploidLbl.setChecked(False)

        self.dominantMarkerLbl.setChecked(False)
        self.dominantMarkerEdit.clear()

        #self.opLbl.setChecked(False) 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MCMCBiMarkersPage()
    ex.show()
    sys.exit(app.exec_())
