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

class MLEBiMarkersPage(QWizardPage):
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
        super(MLEBiMarkersPage, self).__init__()

        self.inputFiles = []
        self.nchar = 0
        self.taxa_names = set([])
        self.taxamap = {}

        self.TABS = 4

        self.isValidated = False
        self.initUI()

    def initUI(self):
        titleLabel = titleHeader("MLE_BiMarkers")

        hyperlink = QLabel()
        hyperlink.setText(' For more details '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MLE_BiMarkers">'
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
        optionalLabel.setText("ML Settings")
        optionalLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels      
        self.numRunLbl = QCheckBox("The number of iterations of simulated annealing:", self)
        self.numRunLbl.setObjectName("-mnr")
        self.numRunLbl.stateChanged.connect(self.onChecked)

        self.maxExamLbl = QCheckBox("The maximum allowed times of examining a state during one iteration:", self)
        self.maxExamLbl.setObjectName("-mec")
        self.maxExamLbl.stateChanged.connect(self.onChecked)

        self.numOptimumsLbl = QCheckBox("The number of optimal networks to print:", self)
        self.numOptimumsLbl.setObjectName("-mno")
        self.numOptimumsLbl.stateChanged.connect(self.onChecked)

        self.maxFailuresLbl = QCheckBox("The maximum allowed times of failures to accept a new state during one "
                                        "iteration:", self)
        self.maxFailuresLbl.setObjectName("-mf")
        self.maxFailuresLbl.stateChanged.connect(self.onChecked)

        self.parThreadLbl = QCheckBox("The number of threads running in parallel:")
        self.parThreadLbl.setObjectName("-pl")
        self.parThreadLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.numRunEdit = QLineEdit()
        self.numRunEdit.setDisabled(True)
        self.numRunEdit.setPlaceholderText("100")

        self.chainLengthLbl = QCheckBox("The length of the MCMC chain:")
        self.chainLengthLbl.setObjectName("-cl")
        self.chainLengthLbl.stateChanged.connect(self.onChecked)

        self.sampleFrequencyLbl = QCheckBox("The sample frequency:")
        self.sampleFrequencyLbl.setObjectName("-sf")
        self.sampleFrequencyLbl.stateChanged.connect(self.onChecked)

        self.maxExamEdit = QLineEdit()
        self.maxExamEdit.setDisabled(True)
        self.maxExamEdit.setPlaceholderText("50000")

        self.numOptimumsEdit = QLineEdit()
        self.numOptimumsEdit.setDisabled(True)
        self.numOptimumsEdit.setPlaceholderText("10")

        self.maxFailuresEdit = QLineEdit()
        self.maxFailuresEdit.setDisabled(True)
        self.maxFailuresEdit.setPlaceholderText("50")

        self.parThreadEdit = QLineEdit()
        self.parThreadEdit.setDisabled(True)

        # Layouts
        # Layout of each parameter (label and input)
        numRunLayout = QHBoxLayout()
        numRunLayout.addWidget(self.numRunLbl)
        numRunLayout.addStretch(1)
        numRunLayout.addWidget(self.numRunEdit)

        maxExamLayout = QHBoxLayout()
        maxExamLayout.addWidget(self.maxExamLbl)
        maxExamLayout.addStretch(1)
        maxExamLayout.addWidget(self.maxExamEdit)

        numOptimumsLayout = QHBoxLayout()
        numOptimumsLayout.addWidget(self.numOptimumsLbl)
        numOptimumsLayout.addStretch(1)
        numOptimumsLayout.addWidget(self.numOptimumsEdit)

        maxFailuresLayout = QHBoxLayout()
        maxFailuresLayout.addWidget(self.maxFailuresLbl)
        maxFailuresLayout.addStretch(1)
        maxFailuresLayout.addWidget(self.maxFailuresEdit)

        parThreadLayout = QHBoxLayout()
        parThreadLayout.addWidget(self.parThreadLbl)
        parThreadLayout.addStretch(1)
        parThreadLayout.addWidget(self.parThreadEdit)

        # Main Layout tab two
        tabTwoLayout = QVBoxLayout()
        tabTwoLayout.addWidget(optionalLabel)
        tabTwoLayout.addLayout(numRunLayout)
        tabTwoLayout.addLayout(maxExamLayout)
        tabTwoLayout.addLayout(numOptimumsLayout)
        tabTwoLayout.addLayout(maxFailuresLayout)
        tabTwoLayout.addLayout(parThreadLayout)
        tabTwo.setLayout(tabTwoLayout)   

        #add tab two
        self.tabWidget.addTab(tabTwo, 'Parameters')

        #create tab three 
        tabThree = QWidget(self)
        #tabThree.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        optionalLabelA = QLabel()
        optionalLabelA.setObjectName("instructionLabel")
        optionalLabelA.setText("Inference Settings")
        optionalLabelA.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels
        self.pseudoLbl = QCheckBox("Use pseudolikelihood.")

        self.maxRetLbl = QCheckBox("The maximum number of reticulation nodes in the sampled phylogenetic networks:")
        self.maxRetLbl.setObjectName("-mr")
        self.maxRetLbl.stateChanged.connect(self.onChecked)

        self.taxamapLbl = QCheckBox("Gene tree / species tree taxa association:")
        self.taxamapLbl.setObjectName("-tm")
        self.taxamapLbl.stateChanged.connect(self.onChecked)

        self.thetaLbl = QCheckBox("Fix the population mutation rates associated with all branches to this given value:")
        self.thetaLbl.setObjectName("-fixtheta")
        self.thetaLbl.stateChanged.connect(self.onChecked)

        self.espThetaLbl = QCheckBox("Estimate the mean value of prior of population mutation rates.")

        # Optional parameter inputs        
        self.maxRetEdit = QLineEdit()
        self.maxRetEdit.setDisabled(True)
        self.maxRetEdit.setPlaceholderText("4")

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.thetaEdit = QLineEdit()
        self.thetaEdit.setDisabled(True)

        self.ppEdit = QLineEdit()
        self.ppEdit.setDisabled(True)
        self.ppEdit.setPlaceholderText("1.0")

        # Layouts
        # Layout of each parameter (label and input)      
        pseudoLayout = QHBoxLayout()
        pseudoLayout.addWidget(self.pseudoLbl)

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

        espThetaLayout = QHBoxLayout()
        espThetaLayout.addWidget(self.espThetaLbl)

        # Main Layout tab three

        tabThreeLayout = QVBoxLayout()
        tabThreeLayout.addWidget(optionalLabelA)
        tabThreeLayout.addLayout(pseudoLayout)
        tabThreeLayout.addLayout(maxRetLayout)
        tabThreeLayout.addLayout(taxamapLayout)
        tabThreeLayout.addLayout(thetaLayout)
        tabThreeLayout.addLayout(espThetaLayout)

        tabThree.setLayout(tabThreeLayout)          

        #add tabthree
        self.tabWidget.addTab(tabThree, 'Parameters')

        #create tab four 
        tabFour = QWidget(self)

        optionalLabelB = QLabel()
        optionalLabelB.setObjectName("instructionLabel")
        optionalLabelB.setText("Starting State and Data Related Settings")
        optionalLabelB.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        # Optional parameter labels
        self.sNetLbl = QCheckBox("Specify the starting network:")
        self.sNetLbl.setObjectName("-snet")
        self.sNetLbl.stateChanged.connect(self.onChecked)

        self.startingThetaPriorLbl = QCheckBox(
            "Specify the mean value of prior of population mutation rate:")
        self.startingThetaPriorLbl.setObjectName("-ptheta")
        self.startingThetaPriorLbl.stateChanged.connect(self.onChecked)

        self.diploidLbl = QCheckBox("Sequence sampled from diploids.")

        self.dominantMarkerLbl = QCheckBox(
            "Specify which marker is dominant if the data is dominant:")
        self.dominantMarkerLbl.setObjectName("-dominant")
        self.dominantMarkerLbl.stateChanged.connect(self.onChecked)

        self.opLbl = QCheckBox("Ignore all monomorphic sites.")

        # Optional parameter inputs

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)

        self.startingThetaPriorEdit = QLineEdit()
        self.startingThetaPriorEdit.setDisabled(True)
        self.startingThetaPriorEdit.setPlaceholderText("0.036")

        self.dominantMarkerEdit = QComboBox(self)
        self.dominantMarkerEdit.addItem("0")
        self.dominantMarkerEdit.addItem("1")
        self.dominantMarkerEdit.setDisabled(True)

        self.sampleFrequencyEdit = QLineEdit()
        self.sampleFrequencyEdit.setDisabled(True)
        self.sampleFrequencyEdit.setPlaceholderText("500")

        self.seedEdit = QLineEdit()
        self.seedEdit.setDisabled(True)
        self.seedEdit.setPlaceholderText("12345678")

    
        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        # Layouts
        # Layout of each parameter (label and input)

        sNetLayout = QHBoxLayout()
        sNetLayout.addWidget(self.sNetLbl)
        sNetLayout.addWidget(self.sNetEdit)

        startingThetaPriorLayout = QHBoxLayout()
        startingThetaPriorLayout.addWidget(self.startingThetaPriorLbl)
        startingThetaPriorLayout.addStretch(1)
        startingThetaPriorLayout.addWidget(self.startingThetaPriorEdit)

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

        # Main Layout tab four

        tabFourLayout = QVBoxLayout()
        tabFourLayout.addWidget(optionalLabelB)
        tabFourLayout.addLayout(sNetLayout)
        tabFourLayout.addLayout(startingThetaPriorLayout)
        tabFourLayout.addLayout(diploidLayout)
        tabFourLayout.addLayout(dominantMarkerLayout)
        tabFourLayout.addLayout(opLayout)
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
        if self.sequenceFileEdit.document() == "" or self.numReticulationsEdit.text() == "":
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
        try:
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
        except ValueError as e:
            msg = str(e) + ". \nPlease enter a file with such data."
            QMessageBox.warning(self, "Warning", msg, QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def onChecked(self):
        """
        When user clicks the checkbox for an optional command,
        enable or disable the corresponding input widget.
        """
        if self.sender().objectName() == "-mnr":
            if self.numRunEdit.isEnabled():
                self.numRunEdit.setDisabled(True)
            else:
                self.numRunEdit.setDisabled(False)
        elif self.sender().objectName() == "-mec":
            if self.maxExamEdit.isEnabled():
                self.maxExamEdit.setDisabled(True)
            else:
                self.maxExamEdit.setDisabled(False)
        elif self.sender().objectName() == "-mno":
            if self.numOptimumsEdit.isEnabled():
                self.numOptimumsEdit.setDisabled(True)
            else:
                self.numOptimumsEdit.setDisabled(False)
        elif self.sender().objectName() == "-mf":
            if self.maxFailuresEdit.isEnabled():
                self.maxFailuresEdit.setDisabled(True)
            else:
                self.maxFailuresEdit.setDisabled(False)
        elif self.sender().objectName() == "-pl":
            if self.parThreadEdit.isEnabled():
                self.parThreadEdit.setDisabled(True)
            else:
                self.parThreadEdit.setDisabled(False)
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
                outputStr = ""
                outputStr += "#NEXUS\n"

                # Write headers of DATA block
                outputStr += "Begin data;\n"
                #2000 is a placeholder to be replaced with phased files
                outputStr += "Dimensions ntax= 2000"
                
                outputStr += " nchar="
                outputStr += str(self.nchar)
                outputStr += ";\n"
                outputStr += 'Format datatype=dna symbols="012" missing=? gap=-;\n'
                outputStr += "Matrix\n"
                outputStr += ";END;\n"

                # Write PHYLONET block.
                outputStr += "BEGIN PHYLONET;\n"
                outputStr += "MLE_BiMarkers"

                # Write optional commands based on user selection.
                if self.pseudoLbl.isChecked():
                    outputStr += " -pseudo"

                if self.numRunLbl.isChecked():
                    if self.numRunEdit.text() == "":
                        pass
                    else:
                        outputStr += " -mnr "
                        outputStr += str(self.numRunEdit.text())

                if self.maxExamLbl.isChecked():
                    if self.maxRetEdit.text() == "":
                        pass
                    else:
                        outputStr += " -mec "
                        outputStr += str(self.maxExamEdit.text())

                if self.numOptimumsLbl.isChecked():
                    if self.numOptimumsEdit.text() == "":
                        pass
                    else:
                        outputStr += " -mno "
                        outputStr += str(self.numOptimumsEdit.text())

                if self.maxFailuresLbl.isChecked():
                    if self.maxFailuresEdit.text() == "":
                        pass
                    else:
                        outputStr += " -mf "
                        outputStr += str(self.maxFailuresEdit.text())

                if self.parThreadLbl.isChecked():
                    if self.parThreadEdit.text() == "":
                        pass
                    else:
                        outputStr += " -pl "
                        outputStr += str(self.parThreadEdit.text())

                if self.maxRetLbl.isChecked():
                    if self.maxRetEdit.text() == "":
                        pass
                    else:
                        outputStr += " -mr "
                        outputStr += str(self.maxRetEdit.text())

                if self.taxamapLbl.isChecked():
                    if len(self.taxamap) == 0:
                        pass
                    else:
                        # Get a mapping from species to taxon.
                        speciesToTaxonMap = self.__inverseMapping(self.taxamap)
                        # Write taxa map.
                        outputStr += " -tm <"
                        for firstSpecies in speciesToTaxonMap:
                            outputStr += firstSpecies
                            outputStr += ":"
                            outputStr += speciesToTaxonMap[firstSpecies][0]
                            for taxon in speciesToTaxonMap[firstSpecies][1:]:
                                outputStr += ","
                                outputStr += taxon
                            speciesToTaxonMap.pop(firstSpecies)
                            break
                        for species in speciesToTaxonMap:
                            outputStr += "; "
                            outputStr += species
                            outputStr += ":"
                            outputStr += speciesToTaxonMap[species][0]
                            for taxon in speciesToTaxonMap[species][1:]:
                                outputStr += ","
                                outputStr += taxon
                        outputStr += ">"

                if self.thetaLbl.isChecked():
                    if self.thetaEdit.text() == "":
                        pass
                    else:
                        outputStr += " -fixtheta "
                        outputStr += str(self.thetaEdit.text())

                if self.espThetaLbl.isChecked():
                    outputStr += " -esptheta"

                if self.sNetLbl.isChecked():
                    if self.sNetEdit.text() == "":
                        pass
                    else:
                        outputStr += " -snet "
                        outputStr += str(self.sNetEdit.text())

                if self.startingThetaPriorLbl.isChecked():
                    if self.startingThetaPriorEdit.text() == "":
                        pass
                    else:
                        outputStr += " -ptheta "
                        outputStr += str(self.startingThetaPriorEdit.text())

                if self.diploidLbl.isChecked():
                    outputStr += " -diploid"

                if self.dominantMarkerLbl.isChecked():
                    outputStr += " -dominant "
                    outputStr += str(self.dominantMarkerEdit.currentText())

                if self.opLbl.isChecked():
                    outputStr += " -op"
                #write to outputfile
                outputFile.write(outputStr)

            # Validate the generated file
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
        CLear page's field
        """
        self.inputFiles = []
        self.nchar = 0
        self.taxa_names = set([])

        self.taxamap = {}

        self.nexus.setChecked(False)
        self.fasta.setChecked(False)
        self.sequenceFileEdit.clear()
        self.numReticulationsEdit.clear()

        self.numRunLbl.setChecked(False)
        self.numRunEdit.clear()
        self.maxExamLbl.setChecked(False)
        self.maxExamEdit.clear()
        self.numOptimumsLbl.setChecked(False)
        self.numOptimumsEdit.clear()
        self.maxFailuresLbl.setChecked(False)
        self.maxFailuresEdit.clear()
        self.parThreadLbl.setChecked(False)
        self.parThreadEdit.clear()
        
        self.pseudoLbl.setChecked(False)
        self.maxRetLbl.setChecked(False)
        self.maxRetEdit.clear()
        self.taxamapLbl.setChecked(False)
        self.thetaLbl.setChecked(False)
        self.thetaEdit.clear()
        self.espThetaLbl.setChecked(False)

        self.sNetLbl.setChecked(False)
        self.sNetEdit.clear()
        self.startingThetaPriorLbl.setChecked(False)
        self.startingThetaPriorEdit.clear()
        self.diploidLbl.setChecked(False) 
        self.dominantMarkerLbl.setChecked(False)
        self.dominantMarkerEdit.clear()
        self.opLbl.setChecked(False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MLEBiMarkersPage()
    ex.show()
    sys.exit(app.exec_())
