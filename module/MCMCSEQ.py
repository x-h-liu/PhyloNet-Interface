import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
import dendropy
import datetime
import subprocess
import shutil

from module import TaxamapDlg
from module import diploidList
from module import paramList

inputFiles = []
taxa_names = set([])
loci = {}
nchar = 0
taxamap = {}
sgtFiles = []
ListOfDiploid = []
GTR = {"A": "0.25", "C": "0.25", "G": "0.25", "T": "0.25", "AC": "1", "AG": "1", "AT": "1", "CG": "1",
"CT": "1", "GT": "1"}

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MCMCSEQPage1(QWizardPage):

    def __init__(self, parent=None):
        super(MCMCSEQPage1, self).__init__(parent)

        self.inputFiles = inputFiles
        self.loci = loci
      
        self.initUI()
     
    def initUI(self):
        """
        Initialize GUI.
        """

      #  wid = QWidget()
      #  scroll = QScrollArea()
      #  self.setCentralWidget(scroll)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        self.menubar = QMenuBar(self)
        menuMenu = self.menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Title (MCMC_SEQ)
        titleLabel = QLabel()
        titleLabel.setText("MCMC_SEQ")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_SEQ">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)

        # Separation lines
        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        # Two subtitles (mandatory and optional commands)
        mandatoryLabel = QLabel()
        mandatoryLabel.setText("Input Data")

        subTitleFont = QFont()
        subTitleFont.setPointSize(18)
        subTitleFont.setFamily("Times New Roman")
        subTitleFont.setBold(True)
        mandatoryLabel.setFont(subTitleFont)

        # Mandatory parameter labels
        sequenceFileLbl = QLabel("Upload sequence files: \n   (one file per locus)")
        sequenceFileLbl.setToolTip("Please put sequence alignments of different loci into separate files. \n"
                                   "Each file is considered to contain sequence alignments from only one locus.")

        #Instruction inputs
        instructionLabel = QLabel()
        instructionLabel.setText("Input data: Please Upload Gene tree files:\n(one file per locus)")
        instructionLabel.setObjectName("instructionLabel") 

        self.nexus = QCheckBox(".nexus")
        self.nexus.setObjectName("nexus")
        self.fasta = QCheckBox(".fasta")
        self.fasta.setObjectName("fasta")
        self.nexus.stateChanged.connect(self.format)
        self.fasta.stateChanged.connect(self.format)  # Implement mutually exclusive check boxes
        
        # Mandatory parameter inputs

        self.sequenceFileEdit = QTextEdit()
        self.sequenceFileEdit.setReadOnly(True)

        fileSelctionBtn = QToolButton()
        fileSelctionBtn.setText("Browse")
        fileSelctionBtn.clicked.connect(self.selectFile)
        fileSelctionBtn.setToolTip("Please put sequence alignments of different loci into separate files. \n"
                                   "Each file is considered to contain sequence alignments from only one locus.")
        self.registerField("sequenceFileEdit*", self.sequenceFileEdit, "plainText", self.sequenceFileEdit.textChanged)
      # UNCOMMENT THIS ^^ FOR DEBUGGING PURPOSES ONLY  
        

        # Layouts
        # Layout of each parameter (label and input)
        fileFormatLayout = QVBoxLayout()
        fileFormatLayout.addWidget(instructionLabel)
        fileFormatLayout.addWidget(self.nexus)
        fileFormatLayout.addWidget(self.fasta)
        fileFormatLayout.addWidget(sequenceFileLbl)
        seqInputLayout = QHBoxLayout()
        seqInputLayout.addWidget(self.sequenceFileEdit)
        seqInputLayout.addWidget(fileSelctionBtn)
        seqFileLayout = QVBoxLayout()
        seqFileLayout.addLayout(fileFormatLayout)
        seqFileLayout.addLayout(seqInputLayout)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addWidget(line1)
        topLevelLayout.addWidget(mandatoryLabel)
        topLevelLayout.addLayout(seqFileLayout)

        # Scroll bar
        self.setLayout(topLevelLayout)
      #  scroll.setWidget(wid)
      #  scroll.setWidgetResizable(True)
      #  scroll.setMinimumWidth(695)
      #  scroll.setMinimumHeight(750)

        self.menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("logo.png")))

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

        
    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Co-estimation of reticulate phylogenies (ILS & hybridization), gene trees, divergence times and "
                    "population sizes on sequences from multiple independent loci."
                    "\n\nFor species phylogeny or phylogenetic network, we infer network topology, divergence times in "
                    "units of expected number of mutations per site, population sizes in units of population mutation "
                    "rate per site, and inheritance probabilities."
                    "\n\nFor gene trees, we infer gene tree topology and coalescent times in units of expected number "
                    "of mutations per site.")
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

    def selectFile(self):
        """
        Read and store all the user uploaded sequence files. Read a file as soon as user uploads it.
        Store information in a dictionary, where keys are file names(loci names), and values are tuples
        containing the length of sequences in each file and the dna character matrix.
        Execute when file selection button is clicked.
        """
        global inputFiles
        global loci
        global nchar
        inputFiles.clear()
        loci.clear()
        nchar = 0

        if (not self.fasta.isChecked()) and (not self.nexus.isChecked()):
             QMessageBox.warning(self, "Warning", "Please select a file type.", QMessageBox.Ok)
        else:
            if self.nexus.isChecked():
                fname = QFileDialog.getOpenFileNames(self, 'Open file', '/', 'Nexus files (*.nexus *.nex);;Fasta files (*.fasta)')
            elif self.fasta.isChecked():
                fname = QFileDialog.getOpenFileNames(self, 'Open file', '/', 'Fasta files (*.fasta);;Nexus files (*.nexus *.nex)')
            if fname:
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
                                # Store all taxa encountered so far in a global set.
                            self.taxa_names = taxa_names
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
                inputFiles = self.inputFiles
                loci = self.loci
                nchar = self.nchar



class MCMCSEQPage2(QWizardPage):

    def __init__(self):
        super(MCMCSEQPage2, self).__init__()

        self.inputFiles = inputFiles
        self.loci = loci
        self.nchar = nchar
        self.taxa_names = taxa_names

        self.taxamap = taxamap
        self.sgtFiles = sgtFiles
        self.ListOfDiploid = ListOfDiploid
        self.GTR = GTR

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
      #  wid = QWidget()
      #  scroll = QScrollArea()
      #  self.setCentralWidget(scroll)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        self.menubar = QMenuBar(self)
        menuMenu = self.menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Title (MCMC_SEQ)
        titleLabel = QLabel()
        titleLabel.setText("MCMC_SEQ")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_SEQ">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)

        # Separation lines
        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame(self)
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        # Two subtitles (mandatory and optional commands)
        optionalLabel = QLabel()
        optionalLabel.setText("MCMC Settings")

        subTitleFont = QFont()
        subTitleFont.setPointSize(18)
        subTitleFont.setFamily("Times New Roman")
        subTitleFont.setBold(True)
        optionalLabel.setFont(subTitleFont)

        # Optional parameter labels
        self.chainLengthLbl = QCheckBox("The length of the MCMC chain:", self)
        self.chainLengthLbl.setObjectName("-cl")
        self.chainLengthLbl.stateChanged.connect(self.onChecked)
        self.registerField("chainLengthLbl", self.chainLengthLbl)

        self.burnInLengthLbl = QCheckBox("The number of iterations in burn-in period:", self)
        self.burnInLengthLbl.setObjectName("-bl")
        self.burnInLengthLbl.stateChanged.connect(self.onChecked)
        self.registerField("burnInLengthLbl", self.burnInLengthLbl)

        self.sampleFrequencyLbl = QCheckBox("The sample frequency:", self)
        self.sampleFrequencyLbl.setObjectName("-sf")
        self.sampleFrequencyLbl.stateChanged.connect(self.onChecked)
        self.registerField("sampleFrequencyLbl", self.sampleFrequencyLbl)

        self.seedLbl = QCheckBox("The random seed:", self)
        self.seedLbl.setObjectName("-sd")
        self.seedLbl.stateChanged.connect(self.onChecked)
        self.registerField("seedLbl", self.seedLbl)

        self.numProcLbl = QCheckBox("Number of threads running in parallel:", self)
        self.numProcLbl.setObjectName("-pl")
        self.numProcLbl.stateChanged.connect(self.onChecked)
        self.registerField("numProcLbl", self.numProcLbl)

        self.outDirLbl = QCheckBox("The absolute path to store the output files:")
        self.outDirLbl.setObjectName("-dir")
        self.outDirLbl.stateChanged.connect(self.onChecked)
        self.registerField("outDirLbl", self.outDirLbl)

        self.tempListLbl = QCheckBox("The list of temperatures for the Metropolis-coupled MCMC chains:", self)
        self.tempListLbl.setObjectName("-mc3")
        self.tempListLbl.stateChanged.connect(self.onChecked)
        self.registerField("tempListLbl", self.tempListLbl)

        # Optional parameter inputs
        self.chainLengthEdit = QLineEdit()
        self.chainLengthEdit.setDisabled(True)
        self.chainLengthEdit.setPlaceholderText("10000000")
        self.registerField("chainLengthEdit", self.chainLengthEdit)

        self.burnInLengthEdit = QLineEdit()
        self.burnInLengthEdit.setDisabled(True)
        self.burnInLengthEdit.setPlaceholderText("2000000")
        self.registerField("burnInLengthEdit", self.burnInLengthEdit)

        self.sampleFrequencyEdit = QLineEdit()
        self.sampleFrequencyEdit.setDisabled(True)
        self.sampleFrequencyEdit.setPlaceholderText("5000")
        self.registerField("sampleFrequencyEdit", self.sampleFrequencyEdit)

        self.seedEdit = QLineEdit()
        self.seedEdit.setDisabled(True)
        self.seedEdit.setPlaceholderText("12345678")
        self.registerField("seedEdit", self.seedEdit)

        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)
        self.registerField("numProcEdit", self.numProcEdit)

        self.outDirEdit = QLineEdit()
        self.outDirEdit.setDisabled(True)
        self.outDirEdit.setPlaceholderText(os.path.expanduser("~"))
        self.outDirBtn = QToolButton()
        self.outDirBtn.setText("Browse")
        self.outDirBtn.setDisabled(True)
        self.outDirBtn.clicked.connect(self.selectDest)
        self.registerField("outDirEdit", self.outDirEdit)

        self.tempListEdit = QLineEdit()
        self.tempListEdit.setDisabled(True)
        self.tempListEdit.setPlaceholderText("(1.0)")
        self.registerField("tempListEdit", self.tempListEdit)

        # Layouts
        # Layout of each parameter (label and input)
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

        outDirLayout = QHBoxLayout()
        outDirLayout.addWidget(self.outDirLbl)
        outDirLayout.addWidget(self.outDirEdit)
        outDirLayout.addWidget(self.outDirBtn)

        tempListLayout = QHBoxLayout()
        tempListLayout.addWidget(self.tempListLbl)
        tempListLayout.addWidget(self.tempListEdit)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        
        topLevelLayout.addWidget(line1)
        topLevelLayout.addWidget(optionalLabel)
        topLevelLayout.addLayout(chainLengthLayout)
        topLevelLayout.addLayout(burnInLengthLayout)
        topLevelLayout.addLayout(sampleFrequencyLayout)
        topLevelLayout.addLayout(seedLayout)
        topLevelLayout.addLayout(numProcLayout)
        topLevelLayout.addLayout(outDirLayout)
        
        topLevelLayout.addWidget(line2)
        topLevelLayout.addLayout(tempListLayout)

        # Scroll bar
        self.setLayout(topLevelLayout)
      #  scroll.setWidget(wid)
      #  scroll.setWidgetResizable(True)
      #  scroll.setMinimumWidth(695)
      #  scroll.setMinimumHeight(750)

        self.menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("logo.png")))

    def selectDest(self):
        """
        Select and display the absolute path to store PhyloNet output files in QLineEdit.
        The path written to output NEXUS file will be content of outDirEdit.
        """
        dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if dir:
            self.outDirEdit.setText(dir)

    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Co-estimation of reticulate phylogenies (ILS & hybridization), gene trees, divergence times and "
                    "population sizes on sequences from multiple independent loci."
                    "\n\nFor species phylogeny or phylogenetic network, we infer network topology, divergence times in "
                    "units of expected number of mutations per site, population sizes in units of population mutation "
                    "rate per site, and inheritance probabilities."
                    "\n\nFor gene trees, we infer gene tree topology and coalescent times in units of expected number "
                    "of mutations per site.")
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

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
        elif self.sender().objectName() == "-dir":
            if self.outDirEdit.isEnabled():
                self.outDirEdit.setDisabled(True)
                self.outDirBtn.setDisabled(True)
            else:
                self.outDirEdit.setDisabled(False)
                self.outDirBtn.setDisabled(False)
        elif self.sender().objectName() == "-mc3":
            if self.tempListEdit.isEnabled():
                self.tempListEdit.setDisabled(True)
            else:
                self.tempListEdit.setDisabled(False)
        else:
            pass

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

class MCMCSEQPage3(QWizardPage):
    def __init__(self):
        super(MCMCSEQPage3, self).__init__()

        self.inputFiles = inputFiles
        self.loci = loci
        self.nchar = nchar
        self.taxa_names = taxa_names

        self.taxamap = taxamap
        self.sgtFiles = sgtFiles
        self.ListOfDiploid = ListOfDiploid
        self.GTR = GTR

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
      #  wid = QWidget()
      #  scroll = QScrollArea()
      #  self.setCentralWidget(scroll)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        self.menubar = QMenuBar(self)
        menuMenu = self.menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Title (MCMC_SEQ)
        titleLabel = QLabel()
        titleLabel.setText("MCMC_SEQ")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_SEQ">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)

        # Separation lines
        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame(self)
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        # Two subtitles (mandatory and optional commands)
        optionalLabel = QLabel()
        optionalLabel.setText("Inference Settings")
        optionalLabel2 = QLabel()
        optionalLabel2.setText("Prior Settings")

        subTitleFont = QFont()
        subTitleFont.setPointSize(18)
        subTitleFont.setFamily("Times New Roman")
        subTitleFont.setBold(True)
        optionalLabel.setFont(subTitleFont)
        optionalLabel2.setFont(subTitleFont)

        # Optional parameter labels
        
        self.maxRetLbl = QCheckBox("The maximum number of reticulation nodes in the sampled phylogenetic networks:", self)
        self.maxRetLbl.setObjectName("-mr")
        self.maxRetLbl.stateChanged.connect(self.onChecked)
        self.registerField("maxRetLbl", self.maxRetLbl)

        self.taxamapLbl = QCheckBox("Gene tree / species tree taxa association:", self)
        self.taxamapLbl.setObjectName("-tm")
        self.taxamapLbl.stateChanged.connect(self.onChecked)
        self.registerField("taxamapLbl", self.taxamapLbl)

        self.popSizeLbl = QCheckBox("Fix the population sizes associated with all branches of the phylogenetic network " "to this given value:", self)
        self.popSizeLbl.setObjectName("-fixps")
        self.popSizeLbl.stateChanged.connect(self.onChecked)
        self.registerField("popSizeLbl", self.popSizeLbl)

        self.varypsLbl = QCheckBox("Vary the population sizes across all branches.", self)
        self.registerField("varypsLbl", self.varypsLbl)

        self.ppLbl = QCheckBox("The Poisson parameter in the prior on the number of reticulation nodes:", self)
        self.ppLbl.setObjectName("-pp")
        self.ppLbl.stateChanged.connect(self.onChecked)
        self.registerField("ppLbl", self.ppLbl)

        self.ddLbl = QCheckBox("Disable the prior on the diameters of hybridizations.", self)
        self.registerField("ddLbl", self.ddLbl)

        self.eeLbl = QCheckBox("Enable the Exponential(10) prior on the divergence times of nodes in the phylogenetic "
                               "network.", self)
        self.registerField("eeLbl", self.eeLbl)

        # Optional parameter inputs
        self.maxRetEdit = QLineEdit()
        self.maxRetEdit.setDisabled(True)
        self.maxRetEdit.setPlaceholderText("4")
        self.registerField("maxRetEdit", self.maxRetEdit)

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)
        self.registerField("taxamapEdit", self.taxamapEdit)

        self.popSizeEdit = QLineEdit()
        self.popSizeEdit.setDisabled(True)
        self.registerField("popSizeEdit", self.popSizeEdit)
       
        self.ppEdit = QLineEdit()
        self.ppEdit.setDisabled(True)
        self.ppEdit.setPlaceholderText("1.0")
        self.registerField("ppEdit", self.ppEdit)

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
        
        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)

        topLevelLayout.addWidget(line1)
        topLevelLayout.addWidget(optionalLabel)
        topLevelLayout.addLayout(maxRetLayout)
        topLevelLayout.addLayout(taxamapLayout)
        topLevelLayout.addLayout(popSizeLayout)
        topLevelLayout.addLayout(varypsLayout)

        topLevelLayout.addWidget(line2)
        topLevelLayout.addWidget(optionalLabel2)
        topLevelLayout.addLayout(ppLayout)
        topLevelLayout.addLayout(ddLayout)
        topLevelLayout.addLayout(eeLayout)

        # Scroll bar
        self.setLayout(topLevelLayout)
      #  scroll.setWidget(wid)
      #  scroll.setWidgetResizable(True)
      #  scroll.setMinimumWidth(695)
      #  scroll.setMinimumHeight(750)

        self.menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("logo.png")))

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


    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Co-estimation of reticulate phylogenies (ILS & hybridization), gene trees, divergence times and "
                    "population sizes on sequences from multiple independent loci."
                    "\n\nFor species phylogeny or phylogenetic network, we infer network topology, divergence times in "
                    "units of expected number of mutations per site, population sizes in units of population mutation "
                    "rate per site, and inheritance probabilities."
                    "\n\nFor gene trees, we infer gene tree topology and coalescent times in units of expected number "
                    "of mutations per site.")
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

    def onChecked(self):
        """
        When user clicks the checkbox for an optional command,
        enable or disable the corresponding input widget.
        """
        if self.sender().objectName() == "-mr":
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
        else:
            pass


    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

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

class MCMCSEQPage4(QWizardPage):

    def initializePage(self):
        
        self.sequenceFileEdit = self.field("sequenceFileEdit")
        self.chainLengthLbl = self.field("chainLengthLbl") 
        self.chainLengthEdit = self.field("chainLengthEdit") 
        self.burnInLengthLbl = self.field("burnInLengthLbl")
        self.burnInLengthEdit = self.field("burnInLengthEdit")
        self.sampleFrequencyLbl = self.field("sampleFrequencyLbl")
        self.sampleFrequencyEdit = self.field("sampleFrequencyEdit")
        self.seedLbl = self.field("seedLbl")
        self.seedEdit = self.field("seedEdit")
        self.numProcLbl = self.field("numProcLbl")
        self.numProcEdit = self.field("numProcEdit")
        self.outDirLbl = self.field("outDirLbl")
        self.outDirEdit = self.field("outDirEdit")
        self.tempListLbl = self.field("tempListLbl")
        self.tempListEdit = self.field("tempListEdit")
        self.maxRetLbl = self.field("maxRetLbl")
        self.maxRetEdit = self.field("maxRetEdit")
        self.taxamapLbl = self.field("taxamapLbl")
        self.popSizeLbl = self.field("popSizeLbl")
        self.popSizeEdit = self.field("popSizeEdit")
        self.varypsLbl = self.field("varypsLbl")
        self.ppLbl = self.field("ppLbl")
        self.ppEdit = self.field("ppEdit")
        self.ddLbl = self.field("ddLbl")
        self.eeLbl = self.field("eeLbl")
        return

    def __init__(self):
        super(MCMCSEQPage4, self).__init__()

        self.taxa_names = taxa_names
        self.inputFiles = inputFiles
        self.sgtFiles = sgtFiles
        self.ListOfDiploid = ListOfDiploid
        self.GTR = GTR
        self.nchar = nchar
        self.loci = loci
        self.taxamap = taxamap
        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
      #  wid = QWidget()
      #  scroll = QScrollArea()
      #  self.setCentralWidget(scroll)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        self.menubar = QMenuBar(self)
        menuMenu = self.menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Title (MCMC_SEQ)
        titleLabel = QLabel()
        titleLabel.setText("MCMC_SEQ")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_SEQ">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)

        # Separation lines
        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame(self)
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        line3 = QFrame(self)
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)

        line4 = QFrame(self)
        line4.setFrameShape(QFrame.HLine)
        line4.setFrameShadow(QFrame.Sunken)

        # Two subtitles (mandatory and optional commands)
        optionalLabel = QLabel()
        optionalLabel.setText("Starting State Settings")

        subTitleFont = QFont()
        subTitleFont.setPointSize(18)
        subTitleFont.setFamily("Times New Roman")
        subTitleFont.setBold(True)
        optionalLabel.setFont(subTitleFont)

        # Optional parameter labels

        self.sgtFileLbl = QCheckBox("Starting gene trees for each locus:")
        self.sgtFileLbl.setObjectName("-sgt")
        self.sgtFileLbl.stateChanged.connect(self.onChecked)
        self.registerField("sgtFileLbl",self.sgtFileLbl)

        self.sNetLbl = QCheckBox("The starting network:")
        self.sNetLbl.setObjectName("-snet")
        self.sNetLbl.stateChanged.connect(self.onChecked)
        self.registerField("sNetLbl", self.sNetLbl)

        self.sPopLbl = QCheckBox("The starting population size:")
        self.sPopLbl.setObjectName("-sps")
        self.sPopLbl.stateChanged.connect(self.onChecked)
        self.registerField("sPopLbl", self.sPopLbl)

        self.preLbl = QCheckBox("The number of iterations for pre burn-in:")
        self.preLbl.setObjectName("-pre")
        self.preLbl.stateChanged.connect(self.onChecked)
        self.registerField("preLbl", self.preLbl)

        self.gtrLbl = QCheckBox("Set GTR (general time-reversible) as the substitution model:")
        self.gtrLbl.setObjectName("-gtr")
        self.gtrLbl.stateChanged.connect(self.onChecked)
        self.registerField("gtrLbl", self.gtrLbl)

        self.diploidLbl = QCheckBox("Diploid species list:")
        self.diploidLbl.setObjectName("-diploid")
        self.diploidLbl.stateChanged.connect(self.onChecked)
        self.registerField("diploidLbl", self.diploidLbl)

        # Optional parameter inputs

        self.sgtFileEdit = QLineEdit()
        self.sgtFileEdit.setDisabled(True)
        self.sgtFileEdit.setReadOnly(True)
        self.registerField("sgtFileEdit", self.sgtFileEdit)

        self.sgtFileSelctionBtn = QToolButton()
        self.sgtFileSelctionBtn.setText("Browse")
        self.sgtFileSelctionBtn.clicked.connect(self.selectSgtFile)
        self.sgtFileSelctionBtn.setDisabled(True)
        self.registerField("sgtFileSelctionBtn", self.sgtFileSelctionBtn)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)
        self.registerField("sNetEdit", self.sNetEdit)

        self.sPopEdit = QLineEdit()
        self.sPopEdit.setDisabled(True)
        self.sPopEdit.setPlaceholderText("0.036")
        self.registerField("sPopEdit", self.sPopEdit)

        self.preEdit = QLineEdit()
        self.preEdit.setDisabled(True)
        self.preEdit.setPlaceholderText("10")
        self.registerField("preEdit", self.preEdit)

        self.gtrEdit = QPushButton("Set model")
        self.gtrEdit.setDisabled(True)
        self.gtrEdit.clicked.connect(self.getGTR)
        self.registerField("gtrEdit", self.gtrEdit)

        self.diploidEdit = QPushButton("Set diploid species")
        self.diploidEdit.setDisabled(True)
        self.diploidEdit.clicked.connect(self.getDiploid)
        self.registerField("diploidEdit", self.diploidEdit)

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

        sNetLayout = QHBoxLayout()
        sNetLayout.addWidget(self.sNetLbl)
        sNetLayout.addWidget(self.sNetEdit)

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

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        
        topLevelLayout.addWidget(line1)
        topLevelLayout.addWidget(optionalLabel)
        topLevelLayout.addLayout(sgtFileLayout)
        topLevelLayout.addLayout(sNetLayout)
        topLevelLayout.addLayout(sPopLayout)
        topLevelLayout.addLayout(preLayout)
        
        topLevelLayout.addWidget(line2)
        topLevelLayout.addLayout(gtrLayout)

        topLevelLayout.addWidget(line3)
        topLevelLayout.addLayout(diploidLayout)

        topLevelLayout.addWidget(line4)
        topLevelLayout.addLayout(btnLayout)

        # Scroll bar
        self.setLayout(topLevelLayout)
      #  scroll.setWidget(wid)
      #  scroll.setWidgetResizable(True)
      #  scroll.setMinimumWidth(695)
      #  scroll.setMinimumHeight(750)

        self.menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon(resource_path("logo.png")))

    
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
        
    def aboutMessage(self):

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Co-estimation of reticulate phylogenies (ILS & hybridization), gene trees, divergence times and "
                    "population sizes on sequences from multiple independent loci."
                    "\n\nFor species phylogeny or phylogenetic network, we infer network topology, divergence times in "
                    "units of expected number of mutations per site, population sizes in units of population mutation "
                    "rate per site, and inheritance probabilities."
                    "\n\nFor gene trees, we infer gene tree topology and coalescent times in units of expected number "
                    "of mutations per site.")
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

    def onChecked(self):
        """
        When user clicks the checkbox for an optional command,
        enable or disable the corresponding input widget.
        """

        if self.sender().objectName() == "-sgt":
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

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

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


        fname = QFileDialog.getOpenFileName(self, 'Open file', '/', 'Nexus files (*.nexus *.nex);; Newick files (*.newick)')
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
            QMessageBox.warning(self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return

    def generate(self):
        """
        Generate NEXUS file based on user input.
        """
        self.inputFiles = inputFiles
        self.loci = loci
        self.nchar = nchar

        directory = QFileDialog.getSaveFileName(self, "Save File", "/", "Nexus Files (*.nexus)") 
        
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
                    currentFile.read(path=file, schema=schema, preserve_underscores=True)
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
                data.write(path=path, schema="nexus", suppress_taxa_blocks=True, unquoted_underscores=True)
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
                outputFile.write('Format datatype=dna symbols="ACGTMRWSYK" missing=? gap=-;\n')
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
                if self.chainLengthLbl == True:
                    if self.chainLengthEdit == "":
                        pass
                    else:
                        outputFile.write(" -cl ")
                        outputFile.write(str(self.chainLengthEdit))

                if self.burnInLengthLbl == True:
                    if self.burnInLengthEdit == "":
                        pass
                    else:
                        outputFile.write(" -bl ")
                        outputFile.write(str(self.burnInLengthEdit))

                if self.sampleFrequencyLbl == True:
                    if self.sampleFrequencyEdit == "":
                        pass
                    else:
                        outputFile.write(" -sf ")
                        outputFile.write(str(self.sampleFrequencyEdit))

                if self.seedLbl == True:
                    if self.seedEdit == "":
                        pass
                    else:
                        outputFile.write(" -sd ")
                        outputFile.write(str(self.seedEdit))

                if self.numProcLbl == True:
                    if self.numProcEdit == "":
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.numProcEdit))

                if self.outDirLbl == True:
                    if self.outDirEdit == "":
                        pass
                    else:
                        outputFile.write(" -dir ")
                        outputFile.write('"')
                        outputFile.write(str(self.outDirEdit))
                        outputFile.write('"')

                if self.tempListLbl == True:
                    if self.tempListEdit == "":
                        pass
                    else:
                        outputFile.write(" -mc3 ")
                        outputFile.write(str(self.tempListEdit))

                if self.maxRetLbl == True:
                    if self.maxRetEdit == "":
                        pass
                    else:
                        outputFile.write(" -mr ")
                        outputFile.write(str(self.maxRetEdit))
                        

                if self.taxamapLbl == True:
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

                if self.popSizeLbl == True:
                    if self.popSizeEdit == "":
                        pass
                    else:
                        outputFile.write(" -fixps ")
                        outputFile.write(str(self.popSizeEdit))

                if self.varypsLbl == True:
                    outputFile.write(" -varyps")

                if self.ppLbl == True: 
                    if self.ppEdit == "":
                        pass
                    else:
                        outputFile.write(" -pp ")
                        outputFile.write(str(self.ppEdit))

                if self.ddLbl == True:
                    outputFile.write(" -dd")

                if self.eeLbl == True:
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
                    if self.sNetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -snet ")
                        outputFile.write(str(self.sNetEdit.text()))

                if self.sPopLbl.isChecked():
                    if self.sPopEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -sps ")
                        outputFile.write(str(self.sPopEdit.text()))

                if self.preLbl.isChecked():
                    if self.preEdit.text().isEmpty():
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

            # Clear all data after one write.
            self.inputFiles = []
            self.taxamap = {}
            self.sequenceFileEdit = ""
            self.loci = {}
            self.nchar = 0
            self.taxa_names = set([])
            self.ListOfDiploid = []
            self.sgtFiles = []
            self.sgtFileEdit.clear()

            # Validate the generated file.
            self.validateFile(path)
        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except emptyDesinationError:
            QMessageBox.warning(self, "Warning", "Please specify destination for generated NEXUS file.", QMessageBox.Ok)
            return
        except Exception as e:
            # Clear all data when encounters an exception.
            self.inputFiles = []
            self.taxamap = {}
            self.sequenceFileEdit = ""
            self.loci = {}
            self.nchar = 0
            self.taxa_names = set([])
            self.ListOfDiploid = []
            self.sgtFiles = []
            self.sgtFileEdit.clear()
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def validateFile(self, filePath):
        """
        After the .nexus file is generated, validate the file by feeding it to PhyloNet.
        Specify -checkParams on command line to make sure PhyloNet checks input without executing the command.
        """
        try:
            subprocess.check_output(
                ["java", "-jar", resource_path("module/testphylonet.jar"),
                 filePath, "checkParams"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # If an error is encountered, delete the generated file and display the error to user.
            os.remove(filePath)
            QMessageBox.warning(self, "Warning", e.output, QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MCMCSEQPage1()
    ex.show()
    sys.exit(app.exec_())
