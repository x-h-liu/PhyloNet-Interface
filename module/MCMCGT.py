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

from module import TaxamapDlg
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

class MCMCGTPage(QWizardPage):
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
        self.restarted.connect(lambda : self.inspectInput())
        
        #if you're on last page and the bar is disabled restore buttons 'em
        #edge case
        if self.tabWidget.currentIndex() == self.TABS - 1:
            again_button.setVisible(True)
            finish_button.setVisible(True)

    def __init__(self):
        super(MCMCGTPage, self).__init__()
        
        self.inputFiles = []
        self.geneTreeNames = []
        self.taxamap = {}
        self.multiTreesPerLocus = False
        self.TABS = 3

        self.isValidated = False
        self.initUI()

    def initUI(self):
        titleLabel = titleHeader("MCMC_GT")

        hyperlink = QLabel()
        hyperlink.setText('For more details '
                          '<a style="" href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_GT">'
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
        self.nexus.stateChanged.connect(self.format)
        # Implement mutually exclusive check boxes
        self.newick.stateChanged.connect(self.format)

        # Mandatory parameter inputs
        self.geneTreesEdit = QTextEdit()
        self.geneTreesEdit.textChanged.connect(self.inspectInput)
        self.geneTreesEdit.setReadOnly(True)
        #self.registerField("geneTreesEditTab*", self.geneTreesEditTab, "plainText", self.geneTreesEditTab.textChanged)
        #self.geneTreesEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        fileSelctionBtn = QToolButton()
        fileSelctionBtn.setText("Browse")
        fileSelctionBtn.clicked.connect(self.selectFile)

        # Layouts
        # Layout of each parameter (label and input)
        fileFormatLayout = QVBoxLayout()
        fileFormatLayout.addWidget(instructionLabel)
        fileFormatLayout.addWidget(self.nexus)
        fileFormatLayout.addWidget(self.newick)
        geneTreeDataLayout = QHBoxLayout()
        geneTreeDataLayout.addWidget(self.geneTreesEdit)
        geneTreeDataLayout.addWidget(fileSelctionBtn)

        # Main layout for tab one
        tabOneLayout = QVBoxLayout()
        tabOneLayout.addLayout(fileFormatLayout)
        tabOneLayout.addLayout(geneTreeDataLayout)

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

        self.ppLbl = QCheckBox(
            "The Poisson parameter in the prior on the number of reticulation nodes:", self)
        self.ppLbl.setObjectName("-pp")
        self.ppLbl.stateChanged.connect(self.onChecked)

        self.maxRetLbl = QCheckBox(
            "The maximum number of reticulation nodes in the sampled phylogenetic networks:", self)
        self.maxRetLbl.setObjectName("-mr")
        self.maxRetLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.chainLengthEdit = QLineEdit()
        self.chainLengthEdit.setDisabled(True)
        self.chainLengthEdit.setPlaceholderText("1100000")

        self.burnInLengthEdit = QLineEdit()
        self.burnInLengthEdit.setDisabled(True)
        self.burnInLengthEdit.setPlaceholderText("100000")

        self.sampleFrequencyEdit = QLineEdit()
        self.sampleFrequencyEdit.setDisabled(True)
        self.sampleFrequencyEdit.setPlaceholderText("1000")

        self.seedEdit = QLineEdit()
        self.seedEdit.setDisabled(True)
        self.seedEdit.setPlaceholderText("12345678")

        self.ppEdit = QLineEdit()
        self.ppEdit.setDisabled(True)
        self.ppEdit.setPlaceholderText("1.0")

        self.maxRetEdit = QLineEdit()
        self.maxRetEdit.setDisabled(True)
        self.maxRetEdit.setPlaceholderText("infinity")

        # Layouts
        # Layouts of each parameter and inputs
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

        ppLayout = QHBoxLayout()
        ppLayout.addWidget(self.ppLbl)
        ppLayout.addStretch(1)
        ppLayout.addWidget(self.ppEdit)

        maxRetLayout = QHBoxLayout()
        maxRetLayout.addWidget(self.maxRetLbl)
        maxRetLayout.addStretch(1)
        maxRetLayout.addWidget(self.maxRetEdit)

        # Main Layout tab two
        tabTwoLayout = QVBoxLayout()
        tabTwoLayout.addWidget(optionalLabel)

        tabTwoLayout.addLayout(chainLengthLayout)
        tabTwoLayout.addLayout(burnInLengthLayout)
        tabTwoLayout.addLayout(sampleFrequencyLayout)
        tabTwoLayout.addLayout(seedLayout)
        tabTwoLayout.addLayout(ppLayout)
        tabTwoLayout.addLayout(maxRetLayout)
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
        self.numProcLbl = QCheckBox(
            "Number of threads running in parallel:", self)
        self.numProcLbl.setObjectName("-pl")
        self.numProcLbl.stateChanged.connect(self.onChecked)

        self.tempListLbl = QCheckBox(
            "The list of temperatures for the Metropolis-coupled MCMC chains:", self)
        self.tempListLbl.setObjectName("-tp")
        self.tempListLbl.stateChanged.connect(self.onChecked)

        self.sNetListLbl = QCheckBox(
            "Comma delimited list of network identifiers:", self)
        self.sNetListLbl.setObjectName("-sn")
        self.sNetListLbl.stateChanged.connect(self.onChecked)

        self.taxamapLbl = QCheckBox(
            "Gene tree / species tree taxa association:", self)
        self.taxamapLbl.setObjectName("-tm")
        self.taxamapLbl.stateChanged.connect(self.onChecked)

        self.pseudoLbl = QCheckBox(
            "Use pseudo likelihood instead of full likelihood to reduce runtime", self)

        # Optional parameter inputs
        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)
        self.numProcEdit.setPlaceholderText("1")

        self.tempListEdit = QLineEdit()
        self.tempListEdit.setDisabled(True)
        self.tempListEdit.setPlaceholderText("(1.0)")

        self.sNetListEdit = QLineEdit()
        self.sNetListEdit.setDisabled(True)

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)     

        # Layouts
        # Layouts of each parameter and inputs

        numProcLayout = QHBoxLayout()
        numProcLayout.addWidget(self.numProcLbl)
        numProcLayout.addStretch(1)
        numProcLayout.addWidget(self.numProcEdit)

        tempListLayout = QHBoxLayout()
        tempListLayout.addWidget(self.tempListLbl)
        tempListLayout.addWidget(self.tempListEdit)

        sNetListLayout = QHBoxLayout()
        sNetListLayout.addWidget(self.sNetListLbl)
        sNetListLayout.addWidget(self.sNetListEdit)

        taxamapLayout = QHBoxLayout()
        taxamapLayout.addWidget(self.taxamapLbl)
        taxamapLayout.addStretch(1)
        taxamapLayout.addWidget(self.taxamapEdit)

        pseudoLayout = QHBoxLayout()
        pseudoLayout.addWidget(self.pseudoLbl)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)    

        # Main Layout tab three

        tabThreeLayout = QVBoxLayout()
        tabThreeLayout.addWidget(optionalLabelA)
        tabThreeLayout.addLayout(numProcLayout)
        tabThreeLayout.addLayout(tempListLayout)
        tabThreeLayout.addLayout(sNetListLayout)
        tabThreeLayout.addLayout(taxamapLayout)
        tabThreeLayout.addLayout(pseudoLayout)

        tabThreeLayout.addLayout(btnLayout)
        tabThree.setLayout(tabThreeLayout)          

        #add tabthree
        self.tabWidget.addTab(tabThree, 'Generate')

        #disable tab bar, initially   
        self.tabWidget.tabBar().setDisabled(True)
        self.tabWidget.tabBar().setToolTip("This a mandatory input. Complete it to enable the tab bar")

        #add widget to page layout
        pageLayout.addWidget(self.tabWidget)
        self.setLayout(pageLayout)

    def inspectInput(self):
        """
        Inspects whether mandatory field have been filled
        emits signal if so
        """
        if self.geneTreesEdit.document().isEmpty():
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
        elif self.sender().objectName() == "-pp":
            if self.ppEdit.isEnabled():
                self.ppEdit.setDisabled(True)
            else:
                self.ppEdit.setDisabled(False)
        elif self.sender().objectName() == "-mr":
            if self.maxRetEdit.isEnabled():
                self.maxRetEdit.setDisabled(True)
            else:
                self.maxRetEdit.setDisabled(False)
        elif self.sender().objectName() == "-pl":
            if self.numProcEdit.isEnabled():
                self.numProcEdit.setDisabled(True)
            else:
                self.numProcEdit.setDisabled(False)
        elif self.sender().objectName() == "-tp":
            if self.tempListEdit.isEnabled():
                self.tempListEdit.setDisabled(True)
            else:
                self.tempListEdit.setDisabled(False)
        elif self.sender().objectName() == "-sn":
            if self.sNetListEdit.isEnabled():
                self.sNetListEdit.setDisabled(True)
            else:
                self.sNetListEdit.setDisabled(False)
        elif self.sender().objectName() == "-tm":
            if self.taxamapEdit.isEnabled():
                self.taxamapEdit.setDisabled(True)
            else:
                self.taxamapEdit.setDisabled(False)
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
            dialog = TaxamapDlg.TaxamapDlg(
                data.taxon_namespace, self.taxamap, self)
            if dialog.exec_():
                self.taxamap = dialog.getTaxamap()
        except emptyFileError:
            QMessageBox.warning(
                self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def generate(self):
        """
        Generate NEXUS file based on user input.
        """
        directory = QFileDialog.getSaveFileName(self, "Save File", "/", "Nexus Files (*.nexus)")
        
        class emptyFileError(Exception):
            pass

        class emptyDesinationError(Exception):
            pass

        try:
            if (not self.nexus.isChecked()) and (not self.newick.isChecked()):
                raise emptyFileError
            if len(self.inputFiles) == 0:
                raise emptyFileError

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
                outputFile.write("MCMC_GT (")
                # Write out all the gene tree names.
                if not self.multiTreesPerLocus:
                    # If there's only one tree per locus, write a comma delimited list of gene tree identifiers.
                    outputFile.write(self.geneTreeNames[0])
                    for genetree in self.geneTreeNames[1:]:
                        outputFile.write(",")
                        outputFile.write(genetree)
                    outputFile.write(")")
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
                    outputFile.write(")")

                # -cl chainLength command
                if self.chainLengthLbl.isChecked():  
                    if self.chainLengthEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -cl ")
                        outputFile.write(str(self.chainLengthEdit.text()))

                # -bl chainLength command
                if self.burnInLengthLbl.isChecked():
                    if self.burnInLengthEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -bl ")
                        outputFile.write(str(self.burnInLengthEdit.text()))

                # -sf sampleFrequency command
                if self.sampleFrequencyLbl.isChecked():
                    if self.sampleFrequencyEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -sf ")
                        outputFile.write(str(self.sampleFrequencyEdit.text()))
                      
                # -sd seed command
                if self.seedLbl.isChecked():
                    if self.seedEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -sd ")
                        outputFile.write(str(self.seedEdit.text()))

                # -pp poissonParameter command
                if self.ppLbl.isChecked():
                    if self.ppEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pp ")
                        outputFile.write(str(self.ppEdit.text()))

                # -mr maximumReticulation command
                if self.maxRetLbl.isChecked():
                    if self.maxRetEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -mr ")
                        outputFile.write(str(self.maxRetEdit.text()))

                # -pl parallelThreads command
                if self.numProcLbl.isChecked():
                    if self.numProcEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.numProcEdit.text()))

                # -tp temperatureList command
                if self.tempListLbl.isChecked():
                    if self.tempListEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -tp ")
                        outputFile.write(str(self.tempListEdit.text()))

                # -sn startingNetworkList command
                if self.sNetListLbl.isChecked():
                    if self.sNetListEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -sn ")
                        outputFile.write(str(self.sNetListEdit.text()))
                        
                # -tm taxa map command
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
                    #clear checkbox
                    self.taxamapLbl.setChecked(False)

                # -pseudo command
                if self.pseudoLbl.isChecked():
                    outputFile.write(" -pseudo")
                    #clear checkbox
                    self.pseudoLbl.setChecked(False)

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
        self.numProcLbl.setChecked(False)
        self.numProcEdit.clear()
        self.tempListLbl.setChecked(False)
        self.tempListEdit.clear()
        self.sNetListLbl.setChecked(False)
        self.sNetListEdit.clear()
        self.taxamapLbl.setChecked(False)
        self.chainLengthLbl.setChecked(False)
        self.chainLengthEdit.clear()
        self.burnInLengthLbl.setChecked(False)
        self.burnInLengthEdit.clear()
        self.sampleFrequencyLbl.setChecked(False)
        self.sampleFrequencyEdit.clear()
        self.seedLbl.setChecked(False)
        self.seedEdit.clear()
        self.ppLbl.setChecked(False)
        self.ppEdit.clear()
        self.maxRetLbl.setChecked(False)
        self.maxRetEdit.clear()
        self.pseudoLbl.setChecked(False)       

    def successMessage(self):
        msg = QDialog()
        msg.setWindowTitle("Phylonet") 
        msg.setWindowIcon(QIcon("imgs/logo.png"))
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
    ex = MCMCGTPage()
    ex.show()
    sys.exit(app.exec_())
