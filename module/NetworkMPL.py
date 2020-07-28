import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import dendropy
import datetime
import subprocess
import shutil

from Validator import NumValidator
from module import TaxamapDlg
from functions import *

inputFiles = []
geneTreesNames = []
taxamap = {}

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

class NetworkMPLPage(QWizardPage):
    def __init__(self):
        super(NetworkMPLPage, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreesNames
        self.taxamap = taxamap
        self.multiTreesPerLocus = False

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # Title (InferNetwork_MPL)
        titleLabel = titleHeader("InferNetwork_MPL")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_ML">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")

        # Mandatory parameter labels
        instructionLabel = QLabel()
        instructionLabel.setText("Input data: Please Upload Gene tree files:\n(one file per locus)")
        instructionLabel.setObjectName("instructionLabel")

        self.nexus = QCheckBox(".nexus")
        self.nexus.setObjectName("nexus")
        self.newick = QCheckBox(".newick")
        self.newick.setObjectName("newick")
        self.nexus.stateChanged.connect(self.format)
        self.newick.stateChanged.connect(self.format)  # Implement mutually exclusive check boxes
        numReticulationsLbl = QLabel("Maximum number of reticulations to add:")

        # Mandatory parameter inputs
        self.geneTreesEditMPL = QTextEdit()
        self.geneTreesEditMPL.setReadOnly(True)
        self.registerField("geneTreesEditMPL*", self.geneTreesEditMPL, "plainText", self.geneTreesEditMPL.textChanged)

        fileSelctionBtn = QToolButton()
        fileSelctionBtn.setText("Browse")
        fileSelctionBtn.clicked.connect(self.selectFile)
        fileSelctionBtn.setToolTip("All trees in one file are considered to be from one locus.")

        self.numReticulationsEditMPL = QLineEdit()
        self.numReticulationsEditMPL.setValidator(NumValidator())
        self.numReticulationsEditMPL.setToolTip("Please enter a non-negative integer")
        self.registerField("numReticulationsEditMPL*", self.numReticulationsEditMPL)

        # Layouts
        # Layout of each parameter (label and input)
        fileFormatLayout = QVBoxLayout()
        fileFormatLayout.addWidget(instructionLabel)
        fileFormatLayout.addWidget(self.nexus)
        fileFormatLayout.addWidget(self.newick)
        geneTreeDataLayout = QHBoxLayout()
        geneTreeDataLayout.addWidget(self.geneTreesEditMPL)
        geneTreeDataLayout.addWidget(fileSelctionBtn)

        geneTreeFileLayout = QVBoxLayout()
        geneTreeFileLayout.addLayout(fileFormatLayout)
        geneTreeFileLayout.addLayout(geneTreeDataLayout)

        numReticulationsLayout = QHBoxLayout()
        numReticulationsLayout.addWidget(numReticulationsLbl)
        numReticulationsLayout.addWidget(self.numReticulationsEditMPL)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addLayout(geneTreeFileLayout)
        topLevelLayout.addLayout(numReticulationsLayout)

        self.setLayout(topLevelLayout)

    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes using maximum likelihood."
                    " The returned species network(s) will have inferred branch lengths and inheritance probabilities. "
                    "During the search, branch lengths and inheritance probabilities of a proposed species network can "
                    "be either sampled or optimized. For the first case, after the search, users can ask the program to "
                    "further optimize those parameters of the inferred network. To optimize the branch lengths and "
                    "inheritance probabilities to obtain the maximum likelihood for that species network, we use "
                    "Richard Brent's algorithm (from his book \"Algorithms for Minimization without Derivatives\", "
                    "p. 79). The species network and gene trees must be specified in the Rich Newick Format."
                    "\n\nThe inference can be made using only topologies of gene trees, or using both topologies and "
                    "branch lengths of gene trees. The latter one requires the input gene trees to be ultrametric. ")
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

    def format(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        if self.sender().objectName() == "nexus":
            if not self.nexus.isChecked():
                self.geneTreesEditMPL.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
            else:
                self.newick.setChecked(False)

        elif self.sender().objectName() == "newick":
            if not self.newick.isChecked():
                self.geneTreesEditMPL.clear()
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
        #initialize global attribute
        global inputFiles
        inputFiles.clear()
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
                self.fileType = QLineEdit(fname[1])
                self.registerField("fileTypeMPL", self.fileType)

                if self.nexus.isChecked():
                    if fileType != 'Nexus files (*.nexus *.nex)':
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus or .nex files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            self.geneTreesEditMPL.append(onefname)
                            self.inputFiles.append(str(onefname))

                elif self.newick.isChecked():
                    if fileType != 'Newick files (*.newick)':
                        QMessageBox.warning(self, "Warning", "Please upload only .newick files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            self.geneTreesEditMPL.append(onefname)
                            self.inputFiles.append(str(onefname))
                else:
                    return
                #Update global attribute
                inputFiles = self.inputFiles
       
class NetworkMPLPage2(QWizardPage):
    def initializePage(self):
        self.fileType = self.field("fileTypeMPL")
        self.geneTreesEditMPL = self.field("geneTreesEditMPL")
        self.numReticulationsEditMPL = self.field("numReticulationsEditMPL")
    def __init__(self):
        super(NetworkMPLPage2, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreesNames
        self.taxamap = taxamap
        self.multiTreesPerLocus = False

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # Title (InferNetwork_ML)
        titleLabel = titleHeader("InferNetwork_MPL")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MPL">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName('detailsLink')

        optionalLabel = QLabel()
        optionalLabel.setObjectName("instructionLabel")
        optionalLabel.setText("Input Options")

        # Optional parameter labels
        self.thresholdLbl = QCheckBox("Gene trees bootstrap threshold:", self)
        self.thresholdLbl.setObjectName("-b")
        self.thresholdLbl.stateChanged.connect(self.onChecked)

        self.taxamapLbl = QCheckBox("Gene tree / species tree taxa association:", self)
        self.taxamapLbl.setObjectName("-a")
        self.taxamapLbl.stateChanged.connect(self.onChecked)

        self.sNetLbl = QCheckBox("The network to start search:", self)
        self.sNetLbl.setObjectName("-s")
        self.sNetLbl.stateChanged.connect(self.onChecked)

        self.nNetRetLbl = QCheckBox("Number of optimal networks to return:", self)
        self.nNetRetLbl.setObjectName("-n")
        self.nNetRetLbl.stateChanged.connect(self.onChecked)

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
        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setDisabled(True)
        self.registerField("thresholdEditMPL", self.thresholdEdit)

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)
        self.taxamapEdit.setObjectName("taxamapEdit")

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)
        self.registerField("sNetEditMPL", self.sNetEdit)

        self.nNetRetEdit = QLineEdit()
        self.nNetRetEdit.setDisabled(True)
        self.nNetRetEdit.setPlaceholderText("1")
        self.registerField("nNetRetEditMPL", self.nNetRetEdit)

        self.hybridEdit = QLineEdit()
        self.hybridEdit.setDisabled(True)
        self.registerField("hybridEditMPL", self.hybridEdit)

        self.wetOpEdit = QLineEdit()
        self.wetOpEdit.setDisabled(True)
        self.wetOpEdit.setPlaceholderText("(0.1,0.1,0.15,0.55,0.15,0.15,2.8)")
        self.wetOpEdit.setMinimumWidth(200)
        self.registerField("wetOpEditMPL", self.wetOpEdit)

        self.numRunEdit = QLineEdit()
        self.numRunEdit.setDisabled(True)
        self.numRunEdit.setPlaceholderText("5")
        self.registerField("numRunEditMPL", self.numRunEdit)

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

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addWidget(optionalLabel)
        topLevelLayout.addLayout(thresholdLayout)
        topLevelLayout.addLayout(taxamapLayout)
        topLevelLayout.addLayout(sNetLayout)
        topLevelLayout.addLayout(nNetRetLayout)
        topLevelLayout.addLayout(hybridLayout)
        topLevelLayout.addLayout(wetOpLayout)
        topLevelLayout.addLayout(numRunLayout)

        self.setLayout(topLevelLayout)

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
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes using maximum likelihood."
                    " The returned species network(s) will have inferred branch lengths and inheritance probabilities. "
                    "During the search, branch lengths and inheritance probabilities of a proposed species network can "
                    "be either sampled or optimized. For the first case, after the search, users can ask the program to "
                    "further optimize those parameters of the inferred network. To optimize the branch lengths and "
                    "inheritance probabilities to obtain the maximum likelihood for that species network, we use "
                    "Richard Brent's algorithm (from his book \"Algorithms for Minimization without Derivatives\", "
                    "p. 79). The species network and gene trees must be specified in the Rich Newick Format."
                    "\n\nThe inference can be made using only topologies of gene trees, or using both topologies and "
                    "branch lengths of gene trees. The latter one requires the input gene trees to be ultrametric. ")
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

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
        #initialize global attribute
        global taxamap
        taxamap.clear()
        #update shared attribute
        self.inputFiles = inputFiles

        class emptyFileError(Exception):
            pass

        try:
            if len(self.inputFiles) == 0:
                raise emptyFileError

            # Read files
            if self.fileType == 'Nexus files (*.nexus *.nex)':
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

class NetworkMPLPage3(QWizardPage):

    def __init__(self):
        super(NetworkMPLPage3, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreesNames
        self.taxamap = taxamap
        self.multiTreesPerLocus = False

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # Title (InferNetwork_MP)
        titleLabel = titleHeader("InferNetwork_MPL")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MPL">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")

        # Optional parameter labels
        self.nNetExamLbl = QCheckBox("Maximum number of network topologies to examine:", self)
        self.nNetExamLbl.setObjectName("-m")
        self.nNetExamLbl.stateChanged.connect(self.onChecked)

        self.maxDiaLbl = QCheckBox("Maximum diameter to make an arrangement during network search:", self)
        self.maxDiaLbl.setObjectName("-md")
        self.maxDiaLbl.stateChanged.connect(self.onChecked)

        self.retDiaLbl = QCheckBox("Maximum diameter for a reticulation event:", self)
        self.retDiaLbl.setObjectName("-rd")
        self.retDiaLbl.stateChanged.connect(self.onChecked)

        self.maxFLbl = QCheckBox("Maximum consecutive number of failures for hill climbing:", self)
        self.maxFLbl.setObjectName("-f")
        self.maxFLbl.stateChanged.connect(self.onChecked)

        self.oLabel = QCheckBox("Optimize branch lengths and inheritance probabilities for every proposed species "
                                "network during the search", self)
        self.registerField("oLabelMPL", self.oLabel)

        self.poLabel = QCheckBox("Optimize branch lengths and inheritance probabilities for returned species networks "
                                 "after the search", self)
        self.registerField("poLabelMPL", self.poLabel)

        self.stopCriterionLbl = QCheckBox("The original stopping criterion of Brent's algorithm:", self)
        self.stopCriterionLbl.setObjectName("-p")
        self.stopCriterionLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.nNetExamEdit = QLineEdit()
        self.nNetExamEdit.setDisabled(True)
        self.nNetExamEdit.setValidator(QDoubleValidator(0, float("inf"), 0, self))
        self.nNetExamEdit.setPlaceholderText("infinity")
        self.nNetExamEdit.setToolTip("For infinity, leave the field unfilled")
        self.registerField("nNetExamEditMPL", self.nNetExamEdit)

        self.maxDiaEdit = QLineEdit()
        self.maxDiaEdit.setDisabled(True)
        self.maxDiaEdit.setValidator(QDoubleValidator(0, float("inf"), 0, self))
        self.maxDiaEdit.setPlaceholderText("infinity")
        self.maxDiaEdit.setToolTip("For infinity, leave the field unfilled")
        self.registerField("maxDiaEditMPL", self.maxDiaEdit)

        self.retDiaEdit = QLineEdit()
        self.retDiaEdit.setDisabled(True)
        self.retDiaEdit.setValidator(QDoubleValidator(0, float("inf"), 0, self))
        self.retDiaEdit.setPlaceholderText("infinity")
        self.retDiaEdit.setToolTip("For infinity, leave the field unfilled")
        self.registerField("retDiaEditMPL", self.retDiaEdit)       

        self.maxFEdit = QLineEdit()
        self.maxFEdit.setDisabled(True)
        self.maxFEdit.setPlaceholderText("100")
        self.registerField("maxFEditMPL", self.maxFEdit)

        self.stopCriterionEdit = QLineEdit()
        self.stopCriterionEdit.setDisabled(True)
        self.stopCriterionEdit.setPlaceholderText("(0.01, 0.001)")
        self.registerField("stopCriterionEditMPL", self.stopCriterionEdit)

        # Layouts
        # Layout of each parameter (label and input)
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

        maxFLayout = QHBoxLayout()
        maxFLayout.addWidget(self.maxFLbl)
        maxFLayout.addStretch(1)
        maxFLayout.addWidget(self.maxFEdit)

        oLayout = QHBoxLayout()
        oLayout.addWidget(self.oLabel)

        poLayout = QHBoxLayout()
        poLayout.addWidget(self.poLabel)

        stopCriterionLayout = QHBoxLayout()
        stopCriterionLayout.addWidget(self.stopCriterionLbl)
        stopCriterionLayout.addStretch(1)
        stopCriterionLayout.addWidget(self.stopCriterionEdit)


        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addLayout(nNetExamLayout)
        topLevelLayout.addLayout(maxDiaLayout)
        topLevelLayout.addLayout(retDiaLayout)
        topLevelLayout.addLayout(maxFLayout)
        topLevelLayout.addLayout(oLayout)
        topLevelLayout.addLayout(poLayout)
        topLevelLayout.addLayout(stopCriterionLayout)

        self.setLayout(topLevelLayout)

    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes using maximum likelihood."
                    " The returned species network(s) will have inferred branch lengths and inheritance probabilities. "
                    "During the search, branch lengths and inheritance probabilities of a proposed species network can "
                    "be either sampled or optimized. For the first case, after the search, users can ask the program to "
                    "further optimize those parameters of the inferred network. To optimize the branch lengths and "
                    "inheritance probabilities to obtain the maximum likelihood for that species network, we use "
                    "Richard Brent's algorithm (from his book \"Algorithms for Minimization without Derivatives\", "
                    "p. 79). The species network and gene trees must be specified in the Rich Newick Format."
                    "\n\nThe inference can be made using only topologies of gene trees, or using both topologies and "
                    "branch lengths of gene trees. The latter one requires the input gene trees to be ultrametric. ")
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

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

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))


class NetworkMPLPage4(QWizardPage):
    def initializePage(self):
        self.fileType = self.field("fileTypeMPL")
        self.geneTreesEditMPL = self.field("geneTreesEditMPL")
        self.numReticulationsEditMPL = self.field("numReticulationsEditMPL")
        self.thresholdEdit = self.field("thresholdEditMPL")
        self.sNetEdit = self.field("sNetEditMPL")
        self.nNetRetEdit = self.field("nNetRetEditMPL")
        self.hybridEdit = self.field("hybridEditMPL")
        self.wetOpEdit = self.field("wetOpEditMPL")
        self.numRunEdit = self.field("numRunEditMPL")

        self.nNetExamEdit = self.field("nNetExamEditMPL")
        self.maxDiaEdit = self.field("maxDiaEditMPL")
        self.maxFEdit = self.field("maxFEditMPL")
        self.retDiaEdit = self.field("retDiaEditMPL")
        self.stopCriterionEdit = self.field("stopCriterionEditMPL")
        self.oLabel = self.field("oLabelMPL")
        self.poLabel = self.field("poLabelMPL")

    def __init__(self):
        super(NetworkMPLPage4, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreesNames
        self.taxamap = taxamap
        self.multiTreesPerLocus = False

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # Title (InferNetwork_MP)
        titleLabel = titleHeader("InferNetwork_MPL")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MPL">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")

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
        #self.registerField("maxRoundEdit", self.maxRoundEdit)

        self.maxTryPerBrEdit = QLineEdit()
        self.maxTryPerBrEdit.setDisabled(True)
        self.maxTryPerBrEdit.setPlaceholderText("100")
        #self.registerField("maxTryPerBrEdit", self.maxTryPerBrEdit)

        self.improveThresEdit = QLineEdit()
        self.improveThresEdit.setDisabled(True)
        self.improveThresEdit.setPlaceholderText("0.001")
        #self.registerField("improveThresEdit", self.improveThresEdit)

        self.maxBlEdit = QLineEdit()
        self.maxBlEdit.setDisabled(True)
        self.maxBlEdit.setPlaceholderText("6")
        #self.registerField("maxBlEdit", self.maxBlEdit)

        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)
        self.numProcEdit.setPlaceholderText("1")
        #self.registerField("numProcEdit", self.numProcEdit)

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

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addLayout(maxRoundLayout)
        topLevelLayout.addLayout(maxTryPerBrLayout)
        topLevelLayout.addLayout(improveThresLayout)
        topLevelLayout.addLayout(maxBlLayout)
        topLevelLayout.addLayout(numProcLayout)
        topLevelLayout.addLayout(diLayout)
        topLevelLayout.addLayout(btnLayout)

        self.setLayout(topLevelLayout)

    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes using maximum likelihood."
                    " The returned species network(s) will have inferred branch lengths and inheritance probabilities. "
                    "During the search, branch lengths and inheritance probabilities of a proposed species network can "
                    "be either sampled or optimized. For the first case, after the search, users can ask the program to "
                    "further optimize those parameters of the inferred network. To optimize the branch lengths and "
                    "inheritance probabilities to obtain the maximum likelihood for that species network, we use "
                    "Richard Brent's algorithm (from his book \"Algorithms for Minimization without Derivatives\", "
                    "p. 79). The species network and gene trees must be specified in the Rich Newick Format."
                    "\n\nThe inference can be made using only topologies of gene trees, or using both topologies and "
                    "branch lengths of gene trees. The latter one requires the input gene trees to be ultrametric. ")
        font = QFont()
        font.setPointSize(13)
        font.setFamily("Times New Roman")
        font.setBold(False)

        msg.setFont(font)
        msg.exec_()

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

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

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
    def generate(self):
        """
        Generate NEXUS file based on user input.
        """ 
        #update shared attributes
        self.inputFiles = inputFiles
        self.taxamap = taxamap
        directory = QFileDialog.getSaveFileName(self, "Save File", "/", "Nexus Files (*.nexus)")

        class emptyFileError(Exception):
            pass

        class emptyNumReticulationError(Exception):
            pass

        class emptyDesinationError(Exception):
            pass

        try:
            if len(self.inputFiles) == 0:
                raise emptyFileError
            if self.numReticulationsEditMPL == "":
                raise emptyNumReticulationError
            if directory[0] == "":
                raise emptyDesinationError

            # the file format to read

            if self.fileType == 'Nexus files (*.nexus *.nex)':
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
                outputFile.write("InferNetwork_MPL (")
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
                numReticulations = self.numReticulationsEditMPL
                outputFile.write(numReticulations)

                # -a taxa map command
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
                if self.thresholdEdit == "":
                    pass
                else:
                    outputFile.write(" -b ")
                    outputFile.write(self.thresholdEdit)
                    #clear field
                    self.thresholdEdit = ""

                # -s startingNetwork command
                if self.sNetEdit == "":
                    pass
                else:
                    outputFile.write(" -s ")
                    outputFile.write(self.sNetEdit)
                    #clear field
                    self.sNetEdit = ""

                # -n numNetReturned command
                if self.nNetRetEdit == "":
                    pass
                else:
                    outputFile.write(" -n ")
                    outputFile.write(self.nNetRetEdit)
                    #clear field
                    self.nNetRetEdit = ""

                # -h {s1 [, s2...]} command
                if self.hybridEdit == "":
                    pass
                else:
                    outputFile.write(" -h ")
                    outputFile.write(self.hybridEdit)
                    #clear field
                    self.hybridEdit = ""

                # -w (w1, ..., w6) command
                if self.wetOpEdit == "":
                    pass
                else:
                    outputFile.write(" -w ")
                    outputFile.write(self.wetOpEdit)
                    #clear field
                    self.wetOpEdit = ""

                # -x numRuns command
                if self.numRunEdit == "":
                    pass
                else:
                    outputFile.write(" -x ")
                    outputFile.write(self.numRunEdit)
                    #clear field
                    self.numRunEdit = ""

                # -m maxNetExamined command
                if self.nNetExamEdit == "":
                    pass
                else:
                    outputFile.write(" -m ")
                    outputFile.write(self.nNetExamEdit)
                    #clear text
                    self.nNetExamEdit = ""

                # -md maxDiameter command
                if self.maxDiaEdit == "":
                    pass
                else:
                    outputFile.write(" -md ")
                    outputFile.write(self.maxDiaEdit)
                    #clear text
                    self.maxDiaEdit = ""

                # -rd reticulationDiameter command
                if self.retDiaEdit == "":
                    pass
                else:
                    outputFile.write(" -rd ")
                    outputFile.write(self.retDiaEdit)
                    #clear text
                    self.retDiaEdit = ""

                # -f maxFailure command
                if self.maxFEdit == "":
                    pass
                else:
                    outputFile.write(" -f ")
                    outputFile.write(self.maxFEdit)
                    #clear text
                    self.maxFEdit = ""

                # -o command
                if self.oLabel:
                    outputFile.write(" -o")
                    #clear checkbox
                    self.oLabel = (False)

                # -po command
                if self.poLabel:
                    outputFile.write(" -po")
                    #clear checkbox
                    self.poLabel = False

                # -p command
                if self.stopCriterionEdit == "":
                    pass
                else:
                    outputFile.write(" -p ")
                    outputFile.write(self.stopCriterionEdit)
                    #clear text
                    self.stopCriterionEdit = ""

                # -r command
                if self.maxRoundLbl.isChecked():
                    if self.maxRoundEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -r ")
                        outputFile.write(str(self.maxRoundEdit.text()))
                        #clear text
                        self.maxRoundEdit.clear()
                    #clear checkbox
                    self.maxRoundLbl.setChecked(False)

                # -t command
                if self.maxTryPerBrLbl.isChecked():
                    if self.maxTryPerBrEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -t ")
                        outputFile.write(str(self.maxTryPerBrEdit.text()))
                        #clear text
                        self.maxTryPerBrEdit.clear()
                    #clear checkbox
                    self.maxTryPerBrLbl.setChecked(False)

                # -i command
                if self.improveThresLbl.isChecked():
                    if self.maxTryPerBrEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -i ")
                        outputFile.write(str(self.improveThresEdit.text()))
                        #clear text
                        self.improveThresEdit.clear()
                    #clear checkbox
                    self.improveThresLbl.setChecked(False)

                # -l command
                if self.maxBlLbl.isChecked():
                    if self.maxBlEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -l ")
                        outputFile.write(str(self.maxBlEdit.text()))
                        #clear text
                        self.maxBlEdit.clear
                    #clear checkbox
                    self.maxBlLbl.setChecked(False)

                # -pl numProcessors command
                if self.numProcLbl.isChecked():
                    if self.numProcEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.numProcEdit.text()))
                        #clear text
                        self.numProcEdit.clear()
                    #clear checkbox
                    self.numProcLbl.setChecked(False)

                # -di command
                if self.diLbl.isChecked():
                    outputFile.write(" -di")
                    #clear checkbox
                    self.diLbl.setChecked()

                # End of NEXUS
                outputFile.write(";\n\n")
                outputFile.write("END;")

            self.geneTreeNames = []
            self.inputFiles = []
            self.taxamap = {}
            self.geneTreesEditMPL = ""
            self.multiTreesPerLocus = False
            self.successMessage()

            # Validate the generated file.
            self.validateFile(path)

        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except emptyNumReticulationError:
            QMessageBox.warning(self, "Warning", "Please enter the maximum number of reticulations.", QMessageBox.Ok)
            return
        except emptyDesinationError:
            QMessageBox.warning(self, "Warning", "Please specify destination for generated NEXUS file.", QMessageBox.Ok)
            return
        except Exception as e:
            self.geneTreeNames = []
            self.inputFiles = []
            self.taxamap = {}
            self.geneTreesEditMPL = ""
            self.multiTreesPerLocus = False
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def successMessage(self):
        msg = QDialog()
        msg.setStyleSheet("QDialog{min-width: 500px; min-height: 500px;}")
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
        except subprocess.CalledProcessError as e:
            # If an error is encountered, delete the generated file and display the error to user.
            print("Error generated by validatefile")
            os.remove(filePath)
            QMessageBox.warning(self, "Warning", e.output, QMessageBox.Ok)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkMPLPage()
    ex.show()
    sys.exit(app.exec_())
