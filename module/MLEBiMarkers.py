import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtCore
import dendropy
import datetime
import subprocess
import shutil

import TaxamapDlg
import taxaList


class MLEBiMarkersPage(QMainWindow):
    def __init__(self):
        super(MLEBiMarkersPage, self).__init__()

        self.data = None
        self.taxaList = []
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

        # Title (MLE_BiMarkers)
        titleLabel = QLabel()
        titleLabel.setText("MLE_BiMarkers")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MLE_BiMarkers">'
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
        dataTypeLbl = QLabel("Data Type:")
        dataFormatLbl = QLabel("Data Format:")
        sequenceFileLbl = QLabel("Upload sequence files:")
        taxaListLbl = QLabel("Select taxa used for inference:")

        # Mandatory parameter inputs
        self.dataTypeEdit = QComboBox(self)
        self.dataTypeEdit.addItem("phased data")
        self.dataTypeEdit.addItem("unphased data")
        self.dataTypeEdit.addItem("bi-allelic markers data")
        self.dataTypeEdit.currentIndexChanged.connect(self.cleanData)

        self.dataFormatEdit = QComboBox(self)
        self.dataFormatEdit.addItem(".nexus")
        self.dataFormatEdit.addItem(".fasta")
        self.dataFormatEdit.currentIndexChanged.connect(self.cleanData)

        self.sequenceFileEdit = QLineEdit()
        self.sequenceFileEdit.setReadOnly(True)

        fileSelectionBtn = QToolButton()
        fileSelectionBtn.setText("...")
        fileSelectionBtn.clicked.connect(self.selectFile)

        taxaListBtn = QPushButton("Select")
        taxaListBtn.clicked.connect(self.getTaxaList)

        # Optional parameter labels
        MLSettingLbl = QLabel("ML Settings")
        settingLblFont = QFont()
        settingLblFont.setPointSize(13)
        settingLblFont.setFamily("Times New Roman")
        settingLblFont.setBold(True)
        settingLblFont.setItalic(True)
        MLSettingLbl.setFont(settingLblFont)

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

        inferenceSettingLbl = QLabel("Inference Settings")
        inferenceSettingLbl.setFont(settingLblFont)

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

        startingStateLbl = QLabel("Starting State Settings")
        startingStateLbl.setFont(settingLblFont)

        self.sNetLbl = QCheckBox("Specify the starting network:")
        self.sNetLbl.setObjectName("-snet")
        self.sNetLbl.stateChanged.connect(self.onChecked)

        self.startingThetaPriorLbl = QCheckBox("Specify the mean value of prior of population mutation rate:")
        self.startingThetaPriorLbl.setObjectName("-ptheta")
        self.startingThetaPriorLbl.stateChanged.connect(self.onChecked)

        dataRelatedSettingLbl = QLabel("Data related settings")
        dataRelatedSettingLbl.setFont(settingLblFont)

        self.diploidLbl = QCheckBox("Sequence sampled from diploids.")

        self.dominantMarkerLbl = QCheckBox("Specify which marker is dominant if the data is dominant:")
        self.dominantMarkerLbl.setObjectName("-dominant")
        self.dominantMarkerLbl.stateChanged.connect(self.onChecked)

        self.opLbl = QCheckBox("Ignore all monomorphic sites.")

        # Optional parameter inputs
        self.numRunEdit = QLineEdit()
        self.numRunEdit.setDisabled(True)
        self.numRunEdit.setPlaceholderText("100")

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

        self.maxRetEdit = QLineEdit()
        self.maxRetEdit.setDisabled(True)
        self.maxRetEdit.setPlaceholderText("4")

        self.taxamapEdit = QPushButton("Set taxa map")
        self.taxamapEdit.setDisabled(True)
        self.taxamapEdit.clicked.connect(self.getTaxamap)

        self.thetaEdit = QLineEdit()
        self.thetaEdit.setDisabled(True)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)

        self.startingThetaPriorEdit = QLineEdit()
        self.startingThetaPriorEdit.setDisabled(True)
        self.startingThetaPriorEdit.setPlaceholderText("0.036")

        self.dominantMarkerEdit = QComboBox(self)
        self.dominantMarkerEdit.addItem("0")
        self.dominantMarkerEdit.addItem("1")
        self.dominantMarkerEdit.setDisabled(True)

        # Launch button
        launchBtn = QPushButton("Generate", self)
        launchBtn.clicked.connect(self.generate)

        # Layouts
        typeLayout = QHBoxLayout()
        typeLayout.addWidget(dataTypeLbl)
        typeLayout.addWidget(self.dataTypeEdit)

        formatLayout = QHBoxLayout()
        formatLayout.addWidget(dataFormatLbl)
        formatLayout.addWidget(self.dataFormatEdit)

        typeFormatLayout = QHBoxLayout()
        typeFormatLayout.addStretch(1)
        typeFormatLayout.addLayout(typeLayout)
        typeFormatLayout.addStretch(1)
        typeFormatLayout.addLayout(formatLayout)
        typeFormatLayout.addStretch(1)

        fileLayout = QHBoxLayout()
        fileLayout.addWidget(sequenceFileLbl)
        fileLayout.addWidget(self.sequenceFileEdit)
        fileLayout.addWidget(fileSelectionBtn)

        taxaListLayout = QHBoxLayout()
        taxaListLayout.addWidget(taxaListLbl)
        taxaListLayout.addStretch(1)
        taxaListLayout.addWidget(taxaListBtn)

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

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(hyperlink)
        topLevelLayout.addWidget(line1)
        topLevelLayout.addWidget(mandatoryLabel)

        topLevelLayout.addLayout(typeFormatLayout)
        topLevelLayout.addLayout(fileLayout)
        topLevelLayout.addLayout(taxaListLayout)

        topLevelLayout.addWidget(line2)
        topLevelLayout.addWidget(optionalLabel)

        topLevelLayout.addWidget(MLSettingLbl)
        topLevelLayout.setAlignment(MLSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(numRunLayout)
        topLevelLayout.addLayout(maxExamLayout)
        topLevelLayout.addLayout(numOptimumsLayout)
        topLevelLayout.addLayout(maxFailuresLayout)
        topLevelLayout.addLayout(parThreadLayout)

        topLevelLayout.addWidget(inferenceSettingLbl)
        topLevelLayout.setAlignment(inferenceSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(pseudoLayout)
        topLevelLayout.addLayout(maxRetLayout)
        topLevelLayout.addLayout(taxamapLayout)
        topLevelLayout.addLayout(thetaLayout)
        topLevelLayout.addLayout(espThetaLayout)

        topLevelLayout.addWidget(startingStateLbl)
        topLevelLayout.setAlignment(startingStateLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(sNetLayout)
        topLevelLayout.addLayout(startingThetaPriorLayout)

        topLevelLayout.addWidget(dataRelatedSettingLbl)
        topLevelLayout.setAlignment(dataRelatedSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(diploidLayout)
        topLevelLayout.addLayout(dominantMarkerLayout)
        topLevelLayout.addLayout(opLayout)

        topLevelLayout.addLayout(btnLayout)

        # Scroll bar
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(695)
        scroll.setMinimumHeight(750)

        menubar.setNativeMenuBar(False)
        self.setWindowTitle('PhyloNetNEXGenerator')
        self.setWindowIcon(QIcon("imgs/logo.png"))

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
        QMessageBox.information(self, "About PhyloNet", "I should put something here.")

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

    def link(self, linkStr):
        """
        Open the website of PhyloNet if user clicks on the hyperlink.
        """
        QDesktopServices.openUrl(QtCore.QUrl(linkStr))

    def cleanData(self):
        """
        Clean all internal data for new input.
        Execute when user changes input data format or successfully generates a file.
        """
        self.data = None
        self.taxaList = []
        self.sequenceFileEdit.clear()
        self.taxamap = {}

    def selectFile(self):
        """
        Once user uploads a file, read it in as a DNA character matrix.
        Execute when file selection button is clicked
        """
        try:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '/')
            if fname:
                extension = os.path.splitext(str(fname))[1]
                if str(self.dataFormatEdit.currentText()) == ".nexus":
                    if extension != ".nexus":
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus files!", QMessageBox.Ok)
                    else:
                        # Bi-allelic marker data should be read in as Standard Character Matrix
                        if str(self.dataTypeEdit.currentText()) == "bi-allelic markers data":
                            self.data = dendropy.StandardCharacterMatrix.get(path=str(fname), schema="nexus",
                                                                             preserve_underscores=True)
                            self.sequenceFileEdit.setText(fname)
                        # Other data are DNA Character Matrix
                        else:
                            self.data = dendropy.DnaCharacterMatrix.get(path=str(fname), schema="nexus",
                                                                        preserve_underscores=True)
                            self.sequenceFileEdit.setText(fname)
                else:
                    if extension != ".fasta":
                        QMessageBox.warning(self, "Warning", "Please upload only .fasta files!", QMessageBox.Ok)
                    else:
                        # Bi-allelic marker data should be read in as Standard Character Matrix
                        if str(self.dataTypeEdit.currentText()) == "bi-allelic markers data":
                            self.data = dendropy.StandardCharacterMatrix.get(path=str(fname), schema="fasta")
                            self.sequenceFileEdit.setText(fname)
                        # Other data are DNA Character Matrix
                        else:
                            self.data = dendropy.DnaCharacterMatrix.get(path=str(fname), schema="fasta")
                            self.sequenceFileEdit.setText(fname)
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def getTaxaList(self):
        """
        When user clicks "Select", open up taxaList dialog for user to select taxa used for inference.
        Update self.taxaList based on user input.
        """
        class emptyFileError(Exception):
            pass

        try:
            if self.data is None:
                raise emptyFileError

            # For unphased data, the number of taxa should double because of phasing.
            if str(self.dataTypeEdit.currentText()) == "unphased data":
                taxa = dendropy.TaxonNamespace()
                # Turn each taxon into two.
                for taxon in self.data.taxon_namespace:
                    taxa.add_taxon(dendropy.Taxon(taxon.label + "_0"))
                    taxa.add_taxon(dendropy.Taxon(taxon.label + "_1"))
                # Default is all taxa are used for inference.
                if len(self.taxaList) == 0:
                    for taxon in taxa:
                        self.taxaList.append(taxon.label)

                dialog = taxaList.TaxaListDlg(taxa, self.taxaList, self)
                if dialog.exec_():
                    self.taxaList = dialog.getTaxaList()
            else:
                # Default is all taxa are used for inference.
                if len(self.taxaList) == 0:
                    for taxon in self.data.taxon_namespace:
                        self.taxaList.append(taxon.label)

                dialog = taxaList.TaxaListDlg(self.data.taxon_namespace, self.taxaList, self)
                if dialog.exec_():
                    self.taxaList = dialog.getTaxaList()
        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please upload data first!", QMessageBox.Ok)
            return

    def getTaxamap(self):
        """
        When user clicks "Set taxa map", open up TaxamapDlg for user input
        and update taxa map.
        """
        class emptyFileError(Exception):
            pass

        try:
            if self.data is None:
                raise emptyFileError

            # For unphased data, the number of taxa should double because of phasing.
            if str(self.dataTypeEdit.currentText()) == "unphased data":
                taxa = dendropy.TaxonNamespace()
                # Turn each taxon into two.
                for taxon in self.data.taxon_namespace:
                    taxa.add_taxon(dendropy.Taxon(taxon.label + "_0"))
                    taxa.add_taxon(dendropy.Taxon(taxon.label + "_1"))
                # Default is only one individual for each species.
                if len(self.taxamap) == 0:
                    for taxon in taxa:
                        self.taxamap[taxon.label] = taxon.label

                dialog = TaxamapDlg.TaxamapDlg(taxa, self.taxamap, self)
                if dialog.exec_():
                    self.taxamap = dialog.getTaxamap()
            else:
                # Default is only one individual for each species.
                if len(self.taxamap) == 0:
                    for taxon in self.data.taxon_namespace:
                        self.taxamap[taxon.label] = taxon.label

                dialog = TaxamapDlg.TaxamapDlg(self.data.taxon_namespace, self.taxamap, self)
                if dialog.exec_():
                    self.taxamap = dialog.getTaxamap()

        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please upload data first!", QMessageBox.Ok)
            return

    def __phasing(self, dnaMatrix):
        """
        Convert unphased data into phased data.
        :param dnaMatrix: a DnaCharacterMatrix object for unphased data
        :return: phased, a dictionary from taxon to sequence for phased data
        """
        ambiguity_code = {
            "M": ["A", "C"],
            "R": ["A", "G"],
            "W": ["A", "T"],
            "S": ["C", "G"],
            "Y": ["C", "T"],
            "K": ["G", "T"]
        }

        # Ignore the entire column if the column contains these symbols.
        ignore_code = ["V", "H", "D", "B", "N", "-"]

        phased = {}
        # Split each taxon into two.
        for taxon in dnaMatrix.taxon_namespace:
            phased[taxon.label + "_0"] = ""
            phased[taxon.label + "_1"] = ""

        # Iterate through each column.
        for i in range(len(dnaMatrix[0])):
            nucleotides = set([])
            for taxon in dnaMatrix:
                nucleotides.add(str(dnaMatrix[taxon][i]))
            # If column contains any symbol that should be ignored, continue to next iteration
            if any(x in ignore_code for x in nucleotides):
                continue
            else:
                # Assign a value to this site of each taxon.
                for taxon in dnaMatrix:
                    # If no ambiguity code, copy the original nucleotide.
                    if str(dnaMatrix[taxon][i]) not in ambiguity_code:
                        phased[taxon.label + "_0"] += str(dnaMatrix[taxon][i])
                        phased[taxon.label + "_1"] += str(dnaMatrix[taxon][i])
                    else:
                        # If there is an ambiguity symbol, randomly assign one nucleotide belonging to that ambiguity
                        # code to each taxon.
                        phased[taxon.label + "_0"] += ambiguity_code[str(dnaMatrix[taxon][i])][0]
                        phased[taxon.label + "_1"] += ambiguity_code[str(dnaMatrix[taxon][i])][1]

        return phased

    def __phasedToBi(self, dnaMatrix):
        """
        Convert phased data into bi-allelic markers.
        :param dnaMatrix: a DnaCharacterMatrix object for phased data
        :return: bimarkers, a dictionary from taxon to bi-allelic markers
        """
        bimarkers = {}
        # Initialie each taxon to empty sequence.
        for taxon in dnaMatrix.taxon_namespace:
            bimarkers[taxon.label] = ""
        # Iterate through each column.
        for i in range(len(dnaMatrix[0])):
            nucleotides = set([])
            for taxon in dnaMatrix:
                nucleotides.add(str(dnaMatrix[taxon][i]))
            # If there are only two kinds of nucleotides in this column, an indication of bi-allelic marker.
            if len(nucleotides) == 2 and "-" not in nucleotides:
                uniqueNucleotides = list(nucleotides)
                # Randomly assign 0 or 1 to each of the nucleotides.
                zero = uniqueNucleotides[0]
                for taxon in dnaMatrix:
                    if str(dnaMatrix[taxon][i]) == zero:
                        bimarkers[taxon.label] += "0"
                    else:
                        bimarkers[taxon.label] += "1"

        return bimarkers

    def generate(self):
        """
        Generate NEXUS file based on user input.
        """
        class emptyFileError(Exception):
            pass

        class taxaListEmptyError(Exception):
            pass

        try:
            if self.data is None:
                raise emptyFileError

            if len(self.taxaList) == 0:
                raise taxaListEmptyError

            if str(self.dataTypeEdit.currentText()) == "unphased data":
                maximum = len(self.data) * 2 + 1
            else:
                maximum = len(self.data) + 1

            progress = QProgressDialog("Generating NEXUS file...", "", 0, maximum, self)
            progress.setCancelButton(None)
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.show()
            current = 0

            path = "intermediate/" + str(datetime.datetime.now().strftime('%H-%M-%S')) + ".nexus"

            with open(path, "a") as outputFile:
                outputFile.write("#NEXUS\n")
                outputFile.write("Begin data;\n")
                outputFile.write("Dimensions ntax=")

                # If data is unphased, number of taxa should double because of phasing.
                if str(self.dataTypeEdit.currentText()) == "unphased data":
                    outputFile.write(str(2 * len(self.data.taxon_namespace)))
                else:
                    outputFile.write(str(len(self.data.taxon_namespace)))

                outputFile.write(" nchar=")
                outputFile.write(str(len(self.data[0])))
                outputFile.write(";\n")
                outputFile.write('Format datatype=dna symbols="012" missing=? gap=-;\n')
                outputFile.write("Matrix\n\n")

                QApplication.processEvents()

                # If data is bi-allelic markers, simply write out the data.
                if str(self.dataTypeEdit.currentText()) == "bi-allelic markers data":
                    for taxon in self.data:
                        outputFile.write(taxon.label)
                        outputFile.write(" ")
                        outputFile.write(str(self.data[taxon]))
                        outputFile.write("\n")

                        current += 1
                        progress.setValue(current)
                        QApplication.processEvents()
                # If data is phased, convert into bi-allelic markers, and then write out.
                elif str(self.dataTypeEdit.currentText()) == "phased data":
                    bimarkers = self.__phasedToBi(self.data)
                    for taxon in bimarkers:
                        outputFile.write(taxon)
                        outputFile.write(" ")
                        outputFile.write(bimarkers[taxon])
                        outputFile.write("\n")

                        current += 1
                        progress.setValue(current)
                        QApplication.processEvents()
                # If data is unphased, convert into phased data first, then convert the phased data into
                # bi-allelic markers, and then write out.
                elif str(self.dataTypeEdit.currentText()) == "unphased data":
                    phased = self.__phasing(self.data)
                    bimarkers = self.__phasedToBi(dendropy.DnaCharacterMatrix.from_dict(phased))
                    for taxon in bimarkers:
                        outputFile.write(taxon)
                        outputFile.write(" ")
                        outputFile.write(bimarkers[taxon])
                        outputFile.write("\n")

                        current += 1
                        progress.setValue(current)
                        QApplication.processEvents()

                outputFile.write(";End;\n\n")

                # Write PHYLONET block.
                outputFile.write("BEGIN PHYLONET;\n")
                outputFile.write("MLE_BiMarkers")
                # Write taxa list used for inference.
                outputFile.write(" -taxa (")
                outputFile.write(self.taxaList[0])
                for taxon in self.taxaList[1:]:
                    outputFile.write(",")
                    outputFile.write(taxon)
                outputFile.write(")")

                # Write optional commands based on user selection.
                if self.pseudoLbl.isChecked():
                    outputFile.write(" -pseudo")

                if self.numRunLbl.isChecked():
                    if self.numRunEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -mnr ")
                        outputFile.write(str(self.numRunEdit.text()))

                if self.maxExamLbl.isChecked():
                    if self.maxRetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -mec ")
                        outputFile.write(str(self.maxExamEdit.text()))

                if self.numOptimumsLbl.isChecked():
                    if self.numOptimumsEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -mno ")
                        outputFile.write(str(self.numOptimumsEdit.text()))

                if self.maxFailuresLbl.isChecked():
                    if self.maxFailuresEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -mf ")
                        outputFile.write(str(self.maxFailuresEdit.text()))

                if self.parThreadLbl.isChecked():
                    if self.parThreadEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.parThreadEdit.text()))

                if self.maxRetLbl.isChecked():
                    if self.maxRetEdit.text().isEmpty():
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

                if self.thetaLbl.isChecked():
                    if self.thetaEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -fixtheta ")
                        outputFile.write(str(self.thetaEdit.text()))

                if self.espThetaLbl.isChecked():
                    outputFile.write(" -esptheta")

                if self.sNetLbl.isChecked():
                    if self.sNetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -snet ")
                        outputFile.write(str(self.sNetEdit.text()))

                if self.startingThetaPriorLbl.isChecked():
                    if self.startingThetaPriorEdit.text().isEmpty():
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

            # Clear all data after one write.
            self.cleanData()
            # Validate the generated file.
            self.validateFile(path)

            current += 1
            progress.setValue(current)
            QApplication.processEvents()

        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please upload data first!", QMessageBox.Ok)
            return
        except taxaListEmptyError:
            QMessageBox.warning(self, "Warning", "Please select taxa used for inference!", QMessageBox.Ok)
            return
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def validateFile(self, filePath):
        """
        After the .nexus file is generated, validate the file by feeding it to PhyloNet.
        Specify -checkParams on command line to make sure PhyloNet checks the input
        without executing the command.
        """
        try:
            subprocess.check_output(
                ["java", "-jar", "testphylonet.jar",
                 filePath, "checkParams"], stderr=subprocess.STDOUT)
            # If no problem, move the generated file to output directory
            shutil.move(filePath, "output/" + os.path.basename(filePath))
        except subprocess.CalledProcessError as e:
            # If an error is encountered, display the error to user.
            QMessageBox.warning(self, "Warning", e.output, QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MLEBiMarkersPage()
    ex.show()
    sys.exit(app.exec_())
