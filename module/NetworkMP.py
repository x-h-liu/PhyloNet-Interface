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

"""
inputFiles = []
geneTreeNames = []
taxamap = {}
"""
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

class NetworkMPPage(QWizardPage):
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
        super(NetworkMPPage, self).__init__()
        
        self.inputFiles = []
        self.geneTreeNames = []
        self.taxamap = {}

        self.TABS = 3

        self.isValidated = False
        self.initUI()

    def initUI(self):
        titleLabel = titleHeader("InferNetwork_MP")

        hyperlink = QLabel()
        hyperlink.setText('For more details '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MP">'
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

        self.nNetRetLbl = QCheckBox(
            "Number of optimal networks to return:", self)
        self.nNetRetLbl.setObjectName("-n")
        self.nNetRetLbl.stateChanged.connect(self.onChecked)

        self.nNetExamLbl = QCheckBox(
            "Maximum number of network topologies to examine:", self)
        self.nNetExamLbl.setObjectName("-m")
        self.nNetExamLbl.stateChanged.connect(self.onChecked)

        self.maxDiaLbl = QCheckBox(
            "Maximum diameter to make an arrangement during network search:", self)
        self.maxDiaLbl.setObjectName("-d")
        self.maxDiaLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setDisabled(True)

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setObjectName("taxamapEdit")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)

        self.nNetRetEdit = QLineEdit()
        self.nNetRetEdit.setDisabled(True)
        self.nNetRetEdit.setPlaceholderText("1")

        self.nNetExamEdit = QLineEdit()
        self.nNetExamEdit.setDisabled(True)
        self.nNetExamEdit.setPlaceholderText("infinity")

        self.maxDiaEdit = QLineEdit()
        self.maxDiaEdit.setDisabled(True)
        self.maxDiaEdit.setPlaceholderText("infinity")
 
        # Layouts
        # Layout of each parameter (label and input)
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

        nNetRetLayout = QHBoxLayout()
        nNetRetLayout.addWidget(self.nNetRetLbl)
        nNetRetLayout.addStretch(1)
        nNetRetLayout.addWidget(self.nNetRetEdit)

        nNetExamLayout = QHBoxLayout()
        nNetExamLayout.addWidget(self.nNetExamLbl)
        nNetExamLayout.addStretch(1)
        nNetExamLayout.addWidget(self.nNetExamEdit)

        maxDiaLayout = QHBoxLayout()
        maxDiaLayout.addWidget(self.maxDiaLbl)
        maxDiaLayout.addStretch(1)
        maxDiaLayout.addWidget(self.maxDiaEdit)

        # Main Layout tab two
        tabTwoLayout = QVBoxLayout()
        tabTwoLayout.addWidget(optionalLabel)

        tabTwoLayout.addLayout(thresholdLayout)
        tabTwoLayout.addLayout(taxamapLayout)
        tabTwoLayout.addLayout(sNetLayout)
        tabTwoLayout.addLayout(nNetRetLayout)
        tabTwoLayout.addLayout(nNetExamLayout)
        tabTwoLayout.addLayout(maxDiaLayout)
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

        self.hybridLbl = QCheckBox("A set of specified hybrid species:", self)
        self.hybridLbl.setObjectName("-h")
        self.hybridLbl.stateChanged.connect(self.onChecked)

        self.wetOpLbl = QCheckBox(
            "Weights of operations for network arrangement during the network search:", self)
        self.wetOpLbl.setObjectName("-w")
        self.wetOpLbl.stateChanged.connect(self.onChecked)

        self.maxFLbl = QCheckBox(
            "The maximum number of consecutive failures before the search terminates:", self)
        self.maxFLbl.setObjectName("-f")
        self.maxFLbl.stateChanged.connect(self.onChecked)

        self.numRunLbl = QCheckBox("The number of runs of the search:", self)
        self.numRunLbl.setObjectName("-x")
        self.numRunLbl.stateChanged.connect(self.onChecked)

        self.numProcLbl = QCheckBox("Number of processors:", self)
        self.numProcLbl.setObjectName("-pl")
        self.numProcLbl.stateChanged.connect(self.onChecked)

                
        self.diLbl = QCheckBox(
            "Output Rich Newick string that can be read by Dendroscope.")
        self.diLbl.stateChanged.connect(self.onChecked)
  
        self.fileDestLbl = QCheckBox("Specify file destination for command output:")
        self.fileDestLbl.setObjectName("resultOutputFile")
        self.fileDestLbl.stateChanged.connect(self.onChecked)


        # Inputs
        self.hybridEdit = QLineEdit()
        self.hybridEdit.setDisabled(True)

        self.wetOpEdit = QLineEdit()
        self.wetOpEdit.setDisabled(True)
        self.wetOpEdit.setPlaceholderText("(0.1,0.1,0.15,0.55,0.15,0.15)")
        self.wetOpEdit.setMinimumWidth(200)

        self.maxFEdit = QLineEdit()
        self.maxFEdit.setDisabled(True)
        self.maxFEdit.setPlaceholderText("100")

        self.numRunEdit = QLineEdit()
        self.numRunEdit.setDisabled(True)
        self.numRunEdit.setPlaceholderText("5")

        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)
        self.numProcEdit.setPlaceholderText("1")

        self.fileDestEdit = QLineEdit()
        self.fileDestEdit.setDisabled(True)
        self.fileDestBtn = QToolButton()
        self.fileDestBtn.setText("Browse")
        self.fileDestBtn.setDisabled(True)
        self.fileDestBtn.clicked.connect(self.selectDest)

        #Layouts
        hybridLayout = QHBoxLayout()
        hybridLayout.addWidget(self.hybridLbl)
        hybridLayout.addWidget(self.hybridEdit)

        wetOpLayout = QHBoxLayout()
        wetOpLayout.addWidget(self.wetOpLbl)
        wetOpLayout.addStretch(1)
        wetOpLayout.addWidget(self.wetOpEdit)

        maxFLayout = QHBoxLayout()
        maxFLayout.addWidget(self.maxFLbl)
        maxFLayout.addStretch(1)
        maxFLayout.addWidget(self.maxFEdit)

        numRunLayout = QHBoxLayout()
        numRunLayout.addWidget(self.numRunLbl)
        numRunLayout.addStretch(1)
        numRunLayout.addWidget(self.numRunEdit)

        numProcLayout = QHBoxLayout()
        numProcLayout.addWidget(self.numProcLbl)
        numProcLayout.addStretch(1)
        numProcLayout.addWidget(self.numProcEdit)

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        diLayout = QHBoxLayout()
        diLayout.addWidget(self.diLbl)

        fileDestLayout = QHBoxLayout()
        fileDestLayout.addWidget(self.fileDestLbl)
        fileDestLayout.addWidget(self.fileDestEdit)
        fileDestLayout.addWidget(self.fileDestBtn)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)   

        # Main Layout tab three

        tabThreeLayout = QVBoxLayout()
        tabThreeLayout.addWidget(optionalLabelA)
        tabThreeLayout.addLayout(hybridLayout)
        tabThreeLayout.addLayout(wetOpLayout)
        tabThreeLayout.addLayout(maxFLayout)
        tabThreeLayout.addLayout(numRunLayout)
        tabThreeLayout.addLayout(numProcLayout)
        tabThreeLayout.addLayout(diLayout)
        tabThreeLayout.addLayout(fileDestLayout)
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
        elif self.sender().objectName() == "-n":
            if self.nNetRetEdit.isEnabled():
                self.nNetRetEdit.setDisabled(True)
            else:
                self.nNetRetEdit.setDisabled(False)
        elif self.sender().objectName() == "-m":
            if self.nNetExamEdit.isEnabled():
                self.nNetExamEdit.setDisabled(True)
            else:
                self.nNetExamEdit.setDisabled(False)
        elif self.sender().objectName() == "-d":
            if self.maxDiaEdit.isEnabled():
                self.maxDiaEdit.setDisabled(True)
            else:
                self.maxDiaEdit.setDisabled(False)
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
        elif self.sender().objectName() == "-f":
            if self.maxFEdit.isEnabled():
                self.maxFEdit.setDisabled(True)
            else:
                self.maxFEdit.setDisabled(False)
        elif self.sender().objectName() == "-x":
            if self.numRunEdit.isEnabled():
                self.numRunEdit.setDisabled(True)
            else:
                self.numRunEdit.setDisabled(False)
        elif self.sender().objectName() == "-pl":
            if self.numProcEdit.isEnabled():
                self.numProcEdit.setDisabled(True)
            else:
                self.numProcEdit.setDisabled(False)
        elif self.sender().objectName() == "resultOutputFile":
            if self.fileDestEdit.isEnabled():
                self.fileDestEdit.setDisabled(True)
                self.fileDestBtn.setDisabled(True)
            else:
                self.fileDestEdit.setDisabled(False)
                self.fileDestBtn.setDisabled(False)
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

    def selectDest(self):
        """
        Select and store destination for PhyloNet output.
        """
        fname = str(QFileDialog.getExistingDirectory(self, 'Open file', '/'))
        if fname:
            self.fileDestEdit.setText(fname)

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
                currentFile.read(path=file, schema=schema,
                                 preserve_underscores=True)
                counter = 0
                for tree in currentFile:
                    # rename gene trees
                    tree.label = fileName + str(counter)
                    self.geneTreeNames.append(tree.label)
                    counter += 1
                data.extend(currentFile)

            # Raise exception is found no tree data.
            if len(data) == 0:
                raise Exception("No tree data found in data file")

            # Write out TREES block.
            path = str(directory[0])
            data.write(path=path, schema="nexus",
                       suppress_taxa_blocks=True, unquoted_underscores=True)

            # Ready to write PHYLONET block.
            with open(path, "a") as outputFile:
                outputFile.write("\nBEGIN PHYLONET;\n\n")
                outputFile.write("InferNetwork_MP (")
                # Write out all the gene tree names.
                outputFile.write(self.geneTreeNames[0])
                for genetree in self.geneTreeNames[1:]:
                    outputFile.write(",")
                    outputFile.write(genetree)
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

                # -n numNetReturned command
                if self.nNetRetLbl.isChecked():
                    if self.nNetRetEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -n ")
                        outputFile.write(str(self.nNetRetEdit.text()))

                # -m maxNetExamined command  
                if self.nNetExamLbl.isChecked():            
                    if self.nNetExamEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -m ")
                        outputFile.write(str(self.nNetExamEdit.text()))

                # -d maxDiameter command
                if self.maxDiaLbl.isChecked():
                    if self.maxDiaEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -rd ")
                        outputFile.write(str(self.maxDiaEdit.text()))

                # -h {s1 [, s2...]} command
                if self.hybridLbl.isChecked():
                    if self.hybridLbl.text() == "":
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
                   
                # -f maxFailure command
                if self.maxFLbl.isChecked():
                    if self.maxFEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -f ")
                        outputFile.write(str(self.maxFEdit.text()))

                # -x numRuns command
                if self.numRunLbl.isChecked():
                    if self.numRunEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -x ")
                        outputFile.write(str(self.numRunEdit.text()))

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

                # resultOutputFile command
                if self.fileDestEdit.text() == "":
                    pass
                else:
                    outputFile.write(" ")
                    outputFile.write('"')
                    outputFile.write(self.fileDestEdit.text())
                    outputFile.write('"')
    

                # End of NEXUS
                outputFile.write(";\n\n")
                outputFile.write("END;")

            # Validate the generated file.
            self.validateFile(path)
            #clears inputs if they are validated
            if self.isValidated:
                self.clear()
                self.generated.emit(True)
                successMessage(self)

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
        self.nexus.setChecked(False)
        self.newick.setChecked(False)
        self.geneTreesEdit.clear()
        self.numReticulationsEdit.clear()

        self.thresholdLbl.setChecked(False)
        self.thresholdEdit.clear()
        self.taxamapLbl.setChecked(False)
        self.sNetLbl.setChecked(False)
        self.sNetEdit.clear()
        self.nNetRetLbl.setChecked(False)
        self.nNetRetEdit.clear()
        self.nNetExamLbl.setChecked(False)
        self.nNetExamEdit.clear()
        self.maxDiaLbl.setChecked(False)
        self.maxDiaEdit.clear()
        self.hybridLbl.setChecked(False)
        self.hybridEdit.clear()
        self.wetOpLbl.setChecked(False)
        self.wetOpEdit.clear()
        self.maxFLbl.setChecked(False)
        self.maxFEdit.clear() 
        self.numRunLbl.setChecked(False)
        self.numRunEdit.clear()
        self.numProcLbl.setChecked(False)
        self.numProcEdit.clear()
        self.diLbl.setChecked(False)     

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
    ex = NetworkMPPage()
    ex.show()
    sys.exit(app.exec_())
