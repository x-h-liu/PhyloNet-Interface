import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import dendropy
import datetime
import subprocess
import shutil

from module import TaxamapDlg


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


class NetworkMPPage(QMainWindow):
    def __init__(self):
        super(NetworkMPPage, self).__init__()

        self.inputFiles = []
        self.geneTreeNames = []
        self.taxamap = {}

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        wid = QWidget()
        scroll = QScrollArea()
        self.setCentralWidget(scroll)

        # Menubar and action
        aboutAction = QAction('About', self)
        aboutAction.triggered.connect(self.aboutMessage)
        aboutAction.setShortcut("Ctrl+A")

        menubar = self.menuBar()
        menuMenu = menubar.addMenu('Menu')
        menuMenu.addAction(aboutAction)

        # Title (InferNetwork_MP)
        titleLabel = QLabel()
        titleLabel.setText("InferNetwork_MP")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/InferNetwork_MP">'
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

        # Two subtitles (mandatory and optional commands)
        mandatoryLabel = QLabel()
        mandatoryLabel.setText("Mandatory commands")
        optionalLabel = QLabel()
        optionalLabel.setText("Optional commands")

        subTitleFont = QFont()
        subTitleFont.setPointSize(18)
        subTitleFont.setFamily("Times New Roman")
        subTitleFont.setBold(True)
        mandatoryLabel.setFont(subTitleFont)
        optionalLabel.setFont(subTitleFont)

        # Mandatory parameter labels
        geneTreeFileLbl = QLabel("Gene tree files:")
        self.nexus = QCheckBox(".nexus")
        self.nexus.setObjectName("nexus")
        self.newick = QCheckBox(".newick")
        self.newick.setObjectName("newick")
        self.nexus.stateChanged.connect(self.format)
        self.newick.stateChanged.connect(self.format)  # Implement mutually exclusive check boxes

        numReticulationsLbl = QLabel("Maximum number of reticulations to add:")

        # Mandatory parameter inputs
        self.geneTreesEdit = QTextEdit()
        self.geneTreesEdit.setFixedHeight(50)
        self.geneTreesEdit.setReadOnly(True)

        fileSelctionBtn = QToolButton()
        fileSelctionBtn.setText("...")
        fileSelctionBtn.clicked.connect(self.selectFile)

        self.numReticulationsEdit = QLineEdit()

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

        self.nNetExamLbl = QCheckBox("Maximum number of network topologies to examine:", self)
        self.nNetExamLbl.setObjectName("-m")
        self.nNetExamLbl.stateChanged.connect(self.onChecked)

        self.maxDiaLbl = QCheckBox("Maximum diameter to make an arrangement during network search:", self)
        self.maxDiaLbl.setObjectName("-d")
        self.maxDiaLbl.stateChanged.connect(self.onChecked)

        self.hybridLbl = QCheckBox("A set of specified hybrid species:", self)
        self.hybridLbl.setObjectName("-h")
        self.hybridLbl.stateChanged.connect(self.onChecked)

        self.wetOpLbl = QCheckBox("Weights of operations for network arrangement during the network search:", self)
        self.wetOpLbl.setObjectName("-w")
        self.wetOpLbl.stateChanged.connect(self.onChecked)

        self.maxFLbl = QCheckBox("The maximum number of consecutive failures before the search terminates:", self)
        self.maxFLbl.setObjectName("-f")
        self.maxFLbl.stateChanged.connect(self.onChecked)

        self.numRunLbl = QCheckBox("The number of runs of the search:", self)
        self.numRunLbl.setObjectName("-x")
        self.numRunLbl.stateChanged.connect(self.onChecked)

        self.numProcLbl = QCheckBox("Number of processors:", self)
        self.numProcLbl.setObjectName("-pl")
        self.numProcLbl.stateChanged.connect(self.onChecked)

        self.diLbl = QCheckBox("Output Rich Newick string that can be read by Dendroscope.")
        self.diLbl.stateChanged.connect(self.onChecked)

        self.fileDestLbl = QCheckBox("Specify file destination for command output:")
        self.fileDestLbl.setObjectName("resultOutputFile")
        self.fileDestLbl.stateChanged.connect(self.onChecked)

        # Optional parameter inputs
        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setDisabled(True)

        self.taxamapEdit = QPushButton("Set taxa map")
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
        self.fileDestBtn.setText("...")
        self.fileDestBtn.setDisabled(True)
        self.fileDestBtn.clicked.connect(self.selectDest)

        # Inputs for where the NEXUS file should be generated.
        outDestLbl = QLabel("Please specify destination for generated nexus file:")
        self.outDestEdit = QLineEdit()
        self.outDestEdit.setReadOnly(True)
        self.outDestBtn = QToolButton()
        self.outDestBtn.setText("...")
        self.outDestBtn.clicked.connect(self.selectNEXDest)

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        # Layouts
        # Layout of each parameter (label and input)
        fileFormatLayout = QVBoxLayout()
        fileFormatLayout.addWidget(geneTreeFileLbl)
        fileFormatLayout.addWidget(self.nexus)
        fileFormatLayout.addWidget(self.newick)
        geneTreeFileLayout = QHBoxLayout()
        geneTreeFileLayout.addLayout(fileFormatLayout)
        geneTreeFileLayout.addWidget(self.geneTreesEdit)
        geneTreeFileLayout.addWidget(fileSelctionBtn)

        numReticulationsLayout = QHBoxLayout()
        numReticulationsLayout.addWidget(numReticulationsLbl)
        numReticulationsLayout.addWidget(self.numReticulationsEdit)

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

        diLayout = QHBoxLayout()
        diLayout.addWidget(self.diLbl)

        fileDestLayout = QHBoxLayout()
        fileDestLayout.addWidget(self.fileDestLbl)
        fileDestLayout.addWidget(self.fileDestEdit)
        fileDestLayout.addWidget(self.fileDestBtn)

        outDestLayout = QHBoxLayout()
        outDestLayout.addWidget(outDestLbl)
        outDestLayout.addWidget(self.outDestEdit)
        outDestLayout.addWidget(self.outDestBtn)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(launchBtn)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addWidget(line1)
        topLevelLayout.addWidget(mandatoryLabel)
        topLevelLayout.addLayout(geneTreeFileLayout)
        topLevelLayout.addLayout(numReticulationsLayout)

        topLevelLayout.addWidget(line2)
        topLevelLayout.addWidget(optionalLabel)
        topLevelLayout.addLayout(thresholdLayout)
        topLevelLayout.addLayout(taxamapLayout)
        topLevelLayout.addLayout(sNetLayout)
        topLevelLayout.addLayout(nNetRetLayout)
        topLevelLayout.addLayout(nNetExamLayout)
        topLevelLayout.addLayout(maxDiaLayout)
        topLevelLayout.addLayout(hybridLayout)
        topLevelLayout.addLayout(wetOpLayout)
        topLevelLayout.addLayout(maxFLayout)
        topLevelLayout.addLayout(numRunLayout)
        topLevelLayout.addLayout(numProcLayout)
        topLevelLayout.addLayout(diLayout)
        topLevelLayout.addLayout(fileDestLayout)

        topLevelLayout.addWidget(line3)
        topLevelLayout.addLayout(outDestLayout)
        topLevelLayout.addLayout(btnLayout)

        # Scroll bar
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(695)
        scroll.setMinimumHeight(750)

        menubar.setNativeMenuBar(False)
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
        elif self.sender().objectName() == "resultOutputFile":
            if self.fileDestEdit.isEnabled():
                self.fileDestEdit.setDisabled(True)
                self.fileDestBtn.setDisabled(True)
            else:
                self.fileDestEdit.setDisabled(False)
                self.fileDestBtn.setDisabled(False)
        else:
            pass

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
                pass
            else:
                self.newick.setChecked(False)
                self.geneTreesEdit.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}
        elif self.sender().objectName() == "newick":
            if not self.newick.isChecked():
                pass
            else:
                self.nexus.setChecked(False)
                self.newick.setChecked(True)
                self.geneTreesEdit.clear()
                self.inputFiles = []
                self.geneTreeNames = []
                self.taxamap = {}

    def selectFile(self):
        """
        Store all the user uploaded gene tree files.
        Execute when file selection button is clicked.
        """
        if (not self.newick.isChecked()) and (not self.nexus.isChecked()):
            QMessageBox.warning(self, "Warning", "Please select a file type.", QMessageBox.Ok)
        else:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '/')
            if fname:
                extension = os.path.splitext(str(fname))[1]
                if self.nexus.isChecked():
                    if extension != ".nexus" and extension != ".nex":
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus files!", QMessageBox.Ok)
                    else:
                        self.geneTreesEdit.append(fname)
                        self.inputFiles.append(str(fname))
                else:
                    if extension != ".newick":
                        QMessageBox.warning(self, "Warning", "Please upload only .newick files!", QMessageBox.Ok)
                    else:
                        self.geneTreesEdit.append(fname)
                        self.inputFiles.append(str(fname))

    def selectDest(self):
        """
        Select and store destination for PhyloNet output.
        """
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/')
        if fname:
            self.fileDestEdit.setText(fname)

    def selectNEXDest(self):
        """
        Select and display the absolute output path for NEXUS file generated by this program.
        The NEXUS file will be generated at the path as displayed on QLineEdit.
        """
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if directory:
            self.outDestEdit.setText(directory)

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
            if self.numReticulationsEdit.text().isEmpty():
                raise emptyNumReticulationError
            if self.outDestEdit.text().isEmpty():
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
            path = str(self.outDestEdit.text()) + "/" + str(datetime.datetime.now().strftime('%H-%M-%S')) + ".nexus"
            data.write(path=path, schema="nexus", suppress_taxa_blocks=True, unquoted_underscores=True)

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
                numReticulations = str(self.numReticulationsEdit.text())
                outputFile.write(numReticulations)

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
                    if self.thresholdEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -b ")
                        outputFile.write(str(self.thresholdEdit.text()))

                # -s startingNetwork command
                if self.sNetLbl.isChecked():
                    if self.sNetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -s ")
                        outputFile.write(str(self.sNetEdit.text()))

                # -n numNetReturned command
                if self.nNetRetLbl.isChecked():
                    if self.nNetRetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -n ")
                        outputFile.write(str(self.nNetRetEdit.text()))

                # -m maxNetExamined command
                if self.nNetExamLbl.isChecked():
                    if self.nNetExamEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -m ")
                        outputFile.write(str(self.nNetExamEdit.text()))

                # -d maxDiameter command
                if self.maxDiaLbl.isChecked():
                    if self.maxDiaEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -rd ")
                        outputFile.write(str(self.maxDiaEdit.text()))

                # -h {s1 [, s2...]} command
                if self.hybridLbl.isChecked():
                    if self.hybridEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -h ")
                        outputFile.write(str(self.hybridEdit.text()))

                # -w (w1, ..., w6) command
                if self.wetOpLbl.isChecked():
                    if self.wetOpEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -w ")
                        outputFile.write(str(self.wetOpEdit.text()))

                # -f maxFailure command
                if self.maxFLbl.isChecked():
                    if self.maxFEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -f ")
                        outputFile.write(str(self.maxFEdit.text()))

                # -x numRuns command
                if self.numRunLbl.isChecked():
                    if self.numRunEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -x ")
                        outputFile.write(str(self.numRunEdit.text()))

                # -pl numProcessors command
                if self.numProcLbl.isChecked():
                    if self.numProcEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.numProcEdit.text()))

                # -di command
                if self.diLbl.isChecked():
                    outputFile.write(" -di")

                # resultOutputFile command
                if self.fileDestLbl.isChecked():
                    if self.fileDestEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" ")
                        outputFile.write('"')
                        outputFile.write(self.fileDestEdit.text())
                        outputFile.write('"')

                # End of NEXUS
                outputFile.write(";\n\n")
                outputFile.write("END;")

            self.geneTreeNames = []
            self.inputFiles = []
            self.taxamap = {}
            self.geneTreesEdit.clear()

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
            self.geneTreesEdit.clear()
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def validateFile(self, filePath):
        """
        After the .nexus file is generated, validate the file by feeding it to PhyloNet.
        Specify -checkParams on command line to make sure PhyloNet checks input without executing the command.
        """
        try:
            subprocess.check_output(
                ["java", "-jar", resource_path("testphylonet.jar"),
                 filePath, "checkParams"], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # If an error is encountered, delete the generated file and display the error to user.
            os.remove(filePath)
            QMessageBox.warning(self, "Warning", e.output, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NetworkMPPage()
    ex.show()
    sys.exit(app.exec_())