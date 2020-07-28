import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtLocation
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QObject, QTimer, QThread
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
    # run-time-information
    For more information, visit https://pythonhosted.org/PyInstaller/runtime-information.html
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class NetworkMPPage(QWizardPage):
    def __init__(self):

        super(NetworkMPPage, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreeNames
        self.taxamap = taxamap

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """

        # Title (InferNetwork_MP)
        titleLabel = titleHeader("InferNetwork_MP")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MP">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")

        # Mandatory parameter labels
        instructionLabel = QLabel()
        instructionLabel.setText("Input data: Please Upload Gene tree files.")
        instructionLabel.setObjectName("instructionLabel")

        numReticulationsLbl = QLabel("Maximum number of reticulations to add:")
        self.nexus = QCheckBox(".nexus")
        self.nexus.setObjectName("nexus")
        self.newick = QCheckBox(".newick")
        self.newick.setObjectName("newick")
        self.nexus.stateChanged.connect(self.format)
        self.newick.stateChanged.connect(self.format)  # Implement mutually exclusive check boxes

        # Mandatory parameter inputs
        self.geneTreesEditMP = QTextEdit()
        self.geneTreesEditMP.setReadOnly(True)
        self.registerField("geneTreesEditMP*", self.geneTreesEditMP,
                           "plainText", self.geneTreesEditMP.textChanged)

        fileSelctionBtn = QToolButton()
        fileSelctionBtn.setText("Browse")
        fileSelctionBtn.clicked.connect(self.selectFile)

        self.numReticulationsEditMP = QLineEdit()
        self.numReticulationsEditMP.setValidator(NumValidator())
        self.numReticulationsEditMP.setToolTip("Please enter a non-negative integer")
        self.registerField("numReticulationsEditMP*", self.numReticulationsEditMP)

        # Layouts
        # Layout of each parameter (label and input)
        fileFormatLayout = QVBoxLayout()
        fileFormatLayout.addWidget(instructionLabel)
        fileFormatLayout.addWidget(self.nexus)
        fileFormatLayout.addWidget(self.newick)
        geneTreeDataLayout = QHBoxLayout()
        geneTreeDataLayout.addWidget(self.geneTreesEditMP)
        geneTreeDataLayout.addWidget(fileSelctionBtn)

        geneTreeFileLayout = QVBoxLayout()
        geneTreeFileLayout.addLayout(fileFormatLayout)
        geneTreeFileLayout.addLayout(geneTreeDataLayout)

        numReticulationsLayout = QHBoxLayout()
        numReticulationsLayout.addWidget(numReticulationsLbl)
        numReticulationsLayout.addWidget(self.numReticulationsEditMP)

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
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes under MDC criterion "
                    "using parsimony-based method. The reticulation nodes in the inferred network will have inferred "
                    "inheritance probabilities associated with them. To find the optimal network, steepest descent is "
                    "used. The species network and gene trees must be specified in the Rich Newick Format. However, "
                    "only topologies of them are used in the method.")
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
                self.geneTreesEditMP.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
            else:
                self.newick.setChecked(False)
                
        elif self.sender().objectName() == "newick":
            if not self.newick.isChecked():
                self.geneTreesEditMP.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}

            else:
                self.nexus.setChecked(False)
                self.newick.setChecked(True)

    def clear(self):
        self.geneTreesEditMP.clear()
        self.numReticulationsEditMP.clear()
        self.nexus.setChecked(False)
        self.newick.setChecked(False)

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
                self.registerField("fileTypeMP", self.fileType)

                if self.nexus.isChecked():
                    if fileType != 'Nexus files (*.nexus *.nex)':
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus or .nex files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            self.geneTreesEditMP.append(onefname)
                            self.inputFiles.append(str(onefname))

                elif self.newick.isChecked():
                    if fileType != 'Newick files (*.newick)':
                        QMessageBox.warning(self, "Warning", "Please upload only .newick files", QMessageBox.Ok)
                    else:
                        for onefname in fname[0]:
                            self.geneTreesEditMP.append(onefname)
                            self.inputFiles.append(str(onefname))
                else:
                    return
                #Update global attribute
                inputFiles = self.inputFiles

class NetworkMPPage2(QWizardPage):
    def initializePage(self):
        self.fileType = self.field("fileTypeMP")

    def __init__(self):

        super(NetworkMPPage2, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreeNames
        self.taxamap = taxamap

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """

        # Title (InferNetwork_MP)
        titleLabel = titleHeader("InferNetwork_MP")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MP">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")

        optionalLabel = QLabel()
        optionalLabel.setObjectName("instructionLabel")
        optionalLabel.setText("Input Options")

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
        self.registerField("thresholdEditMP", self.thresholdEdit)

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setObjectName("taxamapEdit")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)
        self.registerField("sNetEditMP", self.sNetEdit)

        self.nNetRetEdit = QLineEdit()
        self.nNetRetEdit.setDisabled(True)
        self.nNetRetEdit.setPlaceholderText("1")
        self.registerField("nNetRetEditMP", self.nNetRetEdit)

        self.nNetExamEdit = QLineEdit()
        self.nNetExamEdit.setDisabled(True)
        self.nNetExamEdit.setValidator(QDoubleValidator(0, float("inf"), 0, self))
        self.nNetExamEdit.setPlaceholderText("infinity")
        self.nNetExamEdit.setToolTip("For infinity, leave the field unfilled")
        self.registerField("nNetExamEditMP", self.nNetExamEdit)

        self.maxDiaEdit = QLineEdit()
        self.maxDiaEdit.setDisabled(True)
        self.maxDiaEdit.setValidator(QDoubleValidator(0, float("inf"), 0, self))
        self.maxDiaEdit.setPlaceholderText("infinity")
        self.maxDiaEdit.setToolTip("For infinity, leave the field unfilled")
        self.registerField("maxDiaEditMP", self.maxDiaEdit)

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

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addWidget(optionalLabel)
        topLevelLayout.addLayout(thresholdLayout)
        topLevelLayout.addLayout(taxamapLayout)
        topLevelLayout.addLayout(sNetLayout)
        topLevelLayout.addLayout(nNetRetLayout)
        topLevelLayout.addLayout(nNetExamLayout)
        topLevelLayout.addLayout(maxDiaLayout)

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
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes under MDC criterion "
                    "using parsimony-based method. The reticulation nodes in the inferred network will have inferred "
                    "inheritance probabilities associated with them. To find the optimal network, steepest descent is "
                    "used. The species network and gene trees must be specified in the Rich Newick Format. However, "
                    "only topologies of them are used in the method.")
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
        else:
            pass

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    def clear(self):
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


class NetworkMPPage3(QWizardPage):

    def initializePage(self):
        self.geneTreesEditMP = self.field("geneTreesEditMP")
        self.numReticulationsEditMP = self.field("numReticulationsEditMP")
        self.thresholdEdit = self.field("thresholdEditMP")
        self.sNetEdit = self.field("sNetEditMP")
        self.nNetRetEdit = self.field("nNetRetEditMP")
        self.nNetExamEdit = self.field("nNetExamEditMP")
        self.maxDiaEdit = self.field("maxDiaEditMP")
        self.fileType = self.field("fileTypeMP")

    def __init__(self):

        super(NetworkMPPage3, self).__init__()

        self.inputFiles = inputFiles
        self.geneTreeNames = geneTreeNames
        self.taxamap = taxamap
        #self.isComplete = False

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        #isComplete = QtCore.pyqtSignal(bool)
        # Title (InferNetwork_MP)
        titleLabel = titleHeader("InferNetwork_MP")

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MP">'
                          'here</a>.')
        hyperlink.linkActivated.connect(self.link)
        hyperlink.setObjectName("detailsLink")

        optionalLabel = QLabel()
        optionalLabel.setObjectName("instructionLabel")
        optionalLabel.setText("Input Options")

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

        # Inputs
        self.hybridEdit = QLineEdit()
        self.hybridEdit.setDisabled(True)
        self.registerField("hybridEditMP", self.hybridEdit)

        self.wetOpEdit = QLineEdit()
        self.wetOpEdit.setDisabled(True)
        self.wetOpEdit.setPlaceholderText("(0.1,0.1,0.15,0.55,0.15,0.15)")
        self.wetOpEdit.setMinimumWidth(200)
        self.registerField("wetOpEditMP", self.wetOpEdit)

        self.maxFEdit = QLineEdit()
        self.maxFEdit.setDisabled(True)
        self.maxFEdit.setPlaceholderText("100")
        self.registerField("maxFEditMP", self.maxFEdit)

        self.numRunEdit = QLineEdit()
        self.numRunEdit.setDisabled(True)
        self.numRunEdit.setPlaceholderText("5")
        self.registerField("numRunEditMP", self.numRunEdit)

        self.numProcEdit = QLineEdit()
        self.numProcEdit.setDisabled(True)
        self.numProcEdit.setPlaceholderText("1")
        self.registerField("numProcEditMP", self.numProcEdit)

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

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)


        #main level layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addLayout(hybridLayout)
        topLevelLayout.addLayout(wetOpLayout)
        topLevelLayout.addLayout(maxFLayout)
        topLevelLayout.addLayout(numRunLayout)
        topLevelLayout.addLayout(numProcLayout)
        topLevelLayout.addLayout(diLayout)
        topLevelLayout.addLayout(btnLayout)
        self.setLayout(topLevelLayout)

    def aboutMessage(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Infers a species network(s) with a specified number of reticulation nodes under MDC criterion "
                    "using parsimony-based method. The reticulation nodes in the inferred network will have inferred "
                    "inheritance probabilities associated with them. To find the optimal network, steepest descent is "
                    "used. The species network and gene trees must be specified in the Rich Newick Format. However, "
                    "only topologies of them are used in the method.")
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
        else:
            pass

    def format(self):
        """
        Process checkbox's stateChanged signal to implement mutual exclusion.
        """
        if self.sender().objectName() == "nexus":
            if not self.nexus.isChecked():
                self.geneTreesEditMP.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
            else:
                self.newick.setChecked(False)
        elif self.sender().objectName() == "newick":
            if not self.newick.isChecked():
                self.geneTreesEditMP.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
            else:
                self.nexus.setChecked(False)
                self.newick.setChecked(True)

    def generate(self):
        """
        Generate NEXUS file based on user input.
        """
        #update shared attributes
        self.inputFiles = inputFiles
        self.taxamap = taxamap

        directory = QFileDialog.getSaveFileName(
            self, "Save File", "/", "Nexus Files (*.nexus)")

        class emptyFileError(Exception):
            pass

        class emptyNumReticulationError(Exception):
            pass

        class emptyDesinationError(Exception):
            pass

        try:
            if len(self.inputFiles) == 0:
                raise emptyFileError
            if self.numReticulationsEditMP == "":
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
                outputFile.write(self.numReticulationsEditMP)

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

                # -m maxNetExamined command              
                if self.nNetExamEdit == "":
                    pass
                else:
                    outputFile.write(" -m ")
                    outputFile.write(self.nNetExamEdit)
                    #clear field
                    self.nNetExamEdit = ""

                # -d maxDiameter command
                if self.maxDiaEdit == "":
                    pass
                else:
                    outputFile.write(" -rd ")
                    outputFile.write(self.maxDiaEdit)
                    #clear field
                    self.maxDiaEdit = ""

                # -h {s1 [, s2...]} command
                if self.hybridLbl.isChecked():
                    if self.hybridLbl.text() == "":
                        pass
                    else:
                        outputFile.write(" -h ")
                        outputFile.write(str(self.hybridEdit.text()))
                        #clear text
                        self.hybridEdit.clear()
                    #clear checkbox
                    self.hybridLbl.setChecked(False)

                # -w (w1, ..., w6) command
                if self.wetOpLbl.isChecked():
                    if self.wetOpEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -w ")
                        outputFile.write(str(self.wetOpEdit.text()))
                        #clear text
                        self.wetOpEdit.clear()
                    #clear checkbox
                    self.wetOpLbl.setChecked(False)
                    
                # -f maxFailure command
                if self.maxFLbl.isChecked():
                    if self.maxFEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -f ")
                        outputFile.write(str(self.maxFEdit.text()))
                        #clear text
                        self.maxFEdit.clear()
                    #clear checkbox
                    self.maxFLbl.setChecked(False)

                # -x numRuns command
                if self.numRunLbl.isChecked():
                    if self.numRunEdit.text() == "":
                        pass
                    else:
                        outputFile.write(" -x ")
                        outputFile.write(str(self.numRunEdit.text()))
                        #clear text
                        self.numRunEdit.clear()
                    #clear checkbox
                    self.numRunLbl.setChecked(False)

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
                    #clear field
                    self.diLbl.setChecked(False)

                # End of NEXUS
                outputFile.write(";\n\n")
                outputFile.write("END;")

            self.geneTreeNames = []
            self.inputFiles = []
            self.taxamap = {}
            self.geneTreesEditMP = ""
            #self.isComplete = True
            #self.isComplete.emit(True)

            self.successMessage()
            # Validate the generated file.
            self.validateFile(path)

        except emptyFileError:
            QMessageBox.warning(
                self, "Warning", "Please select a file type and upload data!", QMessageBox.Ok)
            return
        except emptyNumReticulationError:
            QMessageBox.warning(
                self, "Warning", "Please enter the maximum number of reticulations.", QMessageBox.Ok)
            return
        except emptyDesinationError:
            QMessageBox.warning(
                self, "Warning", "Please specify destination for generated NEXUS file.", QMessageBox.Ok)
            return
        except Exception as e:
            self.geneTreeNames = []
            self.inputFiles = []
            self.taxamap = {}
            self.geneTreesEditMP = ""
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
           # os.remove(filePath)
            QMessageBox.warning(self, "Warning", e.output, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkMPPage()
    ex.show()
    sys.exit(app.exec_())
