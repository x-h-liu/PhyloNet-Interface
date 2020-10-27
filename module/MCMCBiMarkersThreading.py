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
from module import taxaList

# Test to see if committing + pushing is working
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


class MCMCBiMarkersPage(QMainWindow):
    """
    A Multi-threading version of MCMC_BiMarkers page.
    """
    def __init__(self):
        super(MCMCBiMarkersPage, self).__init__()

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

        # Title (MCMC_BiMarkers)
        titleLabel = QLabel()
        titleLabel.setText("MCMC_BiMarkers")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        hyperlink = QLabel()
        hyperlink.setText('Details of this method can be found '
                          '<a href="https://wiki.rice.edu/confluence/display/PHYLONET/MCMC_BiMarkers">'
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
        dataTypeLbl = QLabel("Data Type:")
        dataFormatLbl = QLabel("Data Format:")
        sequenceFileLbl = QLabel("Upload sequence file:")
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
        MCMCSettingLbl = QLabel("MCMC Settings")
        settingLblFont = QFont()
        settingLblFont.setPointSize(13)
        settingLblFont.setFamily("Times New Roman")
        settingLblFont.setBold(True)
        settingLblFont.setItalic(True)
        MCMCSettingLbl.setFont(settingLblFont)

        self.chainLengthLbl = QCheckBox("The length of the MCMC chain:")
        self.chainLengthLbl.setObjectName("-cl")
        self.chainLengthLbl.stateChanged.connect(self.onChecked)

        self.burnInLbl = QCheckBox("The number of iterations in burn-in period:")
        self.burnInLbl.setObjectName("-bl")
        self.burnInLbl.stateChanged.connect(self.onChecked)

        self.sampleFrequencyLbl = QCheckBox("The sample frequency:")
        self.sampleFrequencyLbl.setObjectName("-sf")
        self.sampleFrequencyLbl.stateChanged.connect(self.onChecked)

        self.seedLbl = QCheckBox("The random seed:")
        self.seedLbl.setObjectName("-sd")
        self.seedLbl.stateChanged.connect(self.onChecked)

        self.parThreadLbl = QCheckBox("The number of threads running in parallel:")
        self.parThreadLbl.setObjectName("-pl")
        self.parThreadLbl.stateChanged.connect(self.onChecked)

        MC3SettingLbl = QLabel("MC3 Settings")
        MC3SettingLbl.setFont(settingLblFont)

        self.tempListLbl = QCheckBox("The list of temperatures for the Metropolis-coupled MCMC chains:")
        self.tempListLbl.setObjectName("-mc3")
        self.tempListLbl.stateChanged.connect(self.onChecked)

        inferenceSettingLbl = QLabel("Inference Settings")
        inferenceSettingLbl.setFont(settingLblFont)

        self.maxRetLbl = QCheckBox("The maximum number of reticulation nodes in the sampled phylogenetic networks:")
        self.maxRetLbl.setObjectName("-mr")
        self.maxRetLbl.stateChanged.connect(self.onChecked)

        self.taxamapLbl = QCheckBox("Gene tree / species tree taxa association:")
        self.taxamapLbl.setObjectName("-tm")
        self.taxamapLbl.stateChanged.connect(self.onChecked)

        self.thetaLbl = QCheckBox("Fix the population mutation rates associated with all branches to this given value:")
        self.thetaLbl.setObjectName("-fixtheta")
        self.thetaLbl.stateChanged.connect(self.onChecked)

        self.varyThetaLbl = QCheckBox("The population mutation rates across all branches may be different.")

        self.espThetaLbl = QCheckBox("Estimate the mean value of prior of population mutation rates.")

        priorSettingLbl = QLabel("Prior Settings")
        priorSettingLbl.setFont(settingLblFont)

        self.ppLbl = QCheckBox("The Poisson parameter in the prior on the number of reticulation nodes:")
        self.ppLbl.setObjectName("-pp")
        self.ppLbl.stateChanged.connect(self.onChecked)

        self.ddLbl = QCheckBox("Disable the prior on the diameters of hybridizations.")

        self.eeLbl = QCheckBox("The Exponential parameter in the prior on the divergence times of nodes in the "
                               "phylogenetic network:")
        self.eeLbl.setObjectName("-ee")
        self.eeLbl.stateChanged.connect(self.onChecked)

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

        self.eeEdit = QLineEdit()
        self.eeEdit.setDisabled(True)

        self.sNetEdit = QLineEdit()
        self.sNetEdit.setDisabled(True)

        self.startingThetaPriorEdit = QLineEdit()
        self.startingThetaPriorEdit.setDisabled(True)
        self.startingThetaPriorEdit.setPlaceholderText("0.036")

        self.dominantMarkerEdit = QComboBox(self)
        self.dominantMarkerEdit.addItem("0")
        self.dominantMarkerEdit.addItem("1")
        self.dominantMarkerEdit.setDisabled(True)

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

        chainLengthLayout = QHBoxLayout()
        chainLengthLayout.addWidget(self.chainLengthLbl)
        chainLengthLayout.addStretch(1)
        chainLengthLayout.addWidget(self.chainLengthEdit)

        burnInLayout = QHBoxLayout()
        burnInLayout.addWidget(self.burnInLbl)
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

        diploidLayout = QHBoxLayout()
        diploidLayout.addWidget(self.diploidLbl)

        dominantMarkerLayout = QHBoxLayout()
        dominantMarkerLayout.addWidget(self.dominantMarkerLbl)
        dominantMarkerLayout.addStretch(1)
        dominantMarkerLayout.addWidget(self.dominantMarkerEdit)

        opLayout = QHBoxLayout()
        opLayout.addWidget(self.opLbl)

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

        topLevelLayout.addLayout(typeFormatLayout)
        topLevelLayout.addLayout(fileLayout)
        topLevelLayout.addLayout(taxaListLayout)

        topLevelLayout.addWidget(line2)
        topLevelLayout.addWidget(optionalLabel)

        topLevelLayout.addWidget(MCMCSettingLbl)
        topLevelLayout.setAlignment(MCMCSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(chainLengthLayout)
        topLevelLayout.addLayout(burnInLayout)
        topLevelLayout.addLayout(sampleFrequencyLayout)
        topLevelLayout.addLayout(seedLayout)
        topLevelLayout.addLayout(parThreadLayout)

        topLevelLayout.addWidget(MC3SettingLbl)
        topLevelLayout.setAlignment(MC3SettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(tempListLayout)

        topLevelLayout.addWidget(inferenceSettingLbl)
        topLevelLayout.setAlignment(inferenceSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(maxRetLayout)
        topLevelLayout.addLayout(taxamapLayout)
        topLevelLayout.addLayout(thetaLayout)
        topLevelLayout.addLayout(varyThetaLayout)
        topLevelLayout.addLayout(espThetaLayout)

        topLevelLayout.addWidget(priorSettingLbl)
        topLevelLayout.setAlignment(priorSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(ppLayout)
        topLevelLayout.addLayout(ddLayout)
        topLevelLayout.addLayout(eeLayout)

        topLevelLayout.addWidget(startingStateLbl)
        topLevelLayout.setAlignment(startingStateLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(sNetLayout)
        topLevelLayout.addLayout(startingThetaPriorLayout)

        topLevelLayout.addWidget(dataRelatedSettingLbl)
        topLevelLayout.setAlignment(dataRelatedSettingLbl, QtCore.Qt.AlignCenter)
        topLevelLayout.addLayout(diploidLayout)
        topLevelLayout.addLayout(dominantMarkerLayout)
        topLevelLayout.addLayout(opLayout)

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

    def inverseMapping(self, map):
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
        msg.setText("Bayesian estimation of the posterior distribution of phylogenetic networks given bi-allelic "
                    "genetic markers (SNPs, AFLPs, etc).")
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
                    if extension != ".nexus" and extension != ".nex":
                        QMessageBox.warning(self, "Warning", "Please upload only .nexus files!", QMessageBox.Ok)
                    else:
                        # Bi-allelic marker data should be read in as Standard Character Matrix
                        if str(self.dataTypeEdit.currentText()) == "bi-allelic markers data":
                            self.data = dendropy.StandardCharacterMatrix.get(path=str(fname), schema="nexus",
                                                                             preserve_underscores=True)
                            self.sequenceFileEdit.setText(fname)
                            self.taxaList = []
                            self.taxamap = {}
                        # Other data are DNA Character Matrix
                        else:
                            self.data = dendropy.DnaCharacterMatrix.get(path=str(fname), schema="nexus",
                                                                        preserve_underscores=True)
                            self.sequenceFileEdit.setText(fname)
                            self.taxaList = []
                            self.taxamap = {}
                else:
                    if extension != ".fasta":
                        QMessageBox.warning(self, "Warning", "Please upload only .fasta files!", QMessageBox.Ok)
                    else:
                        # Bi-allelic marker data should be read in as Standard Character Matrix
                        if str(self.dataTypeEdit.currentText()) == "bi-allelic markers data":
                            self.data = dendropy.StandardCharacterMatrix.get(path=str(fname), schema="fasta")
                            self.sequenceFileEdit.setText(fname)
                            self.taxaList = []
                            self.taxamap = {}
                        # Other data are DNA Character Matrix
                        else:
                            self.data = dendropy.DnaCharacterMatrix.get(path=str(fname), schema="fasta")
                            self.sequenceFileEdit.setText(fname)
                            self.taxaList = []
                            self.taxamap = {}
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)
            return

    def selectNEXDest(self):
        """
        Select and display the absolute output path for NEXUS file generated by this program.
        The NEXUS file will be generated at the path as displayed on QLineEdit.
        """
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if directory:
            self.outDestEdit.setText(directory)

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

    def phasing(self, dnaMatrix):
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

    def phasedToBi(self, dnaMatrix):
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

        class emptyDesinationError(Exception):
            pass

        try:
            if self.data is None:
                raise emptyFileError

            if len(self.taxaList) == 0:
                raise taxaListEmptyError

            if self.outDestEdit.text().isEmpty():
                raise emptyDesinationError

            self.path = str(self.outDestEdit.text()) + "/" + \
                        str(datetime.datetime.now().strftime('%H-%M-%S')) + ".nexus"

            # Create worker thread.
            self.worker = Worker(self, self.path)
            self.worker.finished.connect(self.finishWork)
            self.worker.exception.connect(self.failWork)
            self.worker.start()
            # Main thread displays progress bar.
            self.progress.show()

        except emptyFileError:
            QMessageBox.warning(self, "Warning", "Please upload data first!", QMessageBox.Ok)
            return
        except taxaListEmptyError:
            QMessageBox.warning(self, "Warning", "Please select taxa used for inference!", QMessageBox.Ok)
            return
        except emptyDesinationError:
            QMessageBox.warning(self, "Warning", "Please specify destination for generated NEXUS file.", QMessageBox.Ok)
            return
        except Exception as e:
            os.remove(self.path)
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

    def finishWork(self):
        """
        When worker thread finishes writing, it will emit a finished() signal.
        This method catches this signal to validate the generated file and close the progress bar.
        """
        self.validateFile(self.path)
        self.progress.cancel()

    def failWork(self, e):
        """
        When worker thread encounters an exception, it will emit an exception(e) signal.
        This method catches this signal to display the error message on GUI.
        """
        self.cleanData()
        QMessageBox.warning(self, "Warning", str(e), QMessageBox.Ok)


class Worker(QtCore.QThread):
    """
    Worker thread for writing output file. Take in the entire gui class and a path to write.
    """
    # Signal to emit when encounters an exception.
    exception = QtCore.pyqtSignal(Exception)

    def __init__(self, gui, path):
        QtCore.QThread.__init__(self)
        self.gui = gui
        self.path = path

    def run(self):
        """
        Execute the thread. Generate NEXUS file based on user input in GUI.
        """
        try:
            with open(self.path, "a") as outputFile:
                outputFile.write("#NEXUS\n")
                outputFile.write("Begin data;\n")
                outputFile.write("Dimensions ntax=")

                # If data is unphased, number of taxa should double because of phasing.
                if str(self.gui.dataTypeEdit.currentText()) == "unphased data":
                    outputFile.write(str(2 * len(self.gui.data.taxon_namespace)))
                else:
                    outputFile.write(str(len(self.gui.data.taxon_namespace)))

                outputFile.write(" nchar=")

                # number of characters depends on data type
                if str(self.gui.dataTypeEdit.currentText()) == "bi-allelic markers data":
                    # If data is bi-alelic, number of characters should equal the original length of sequences.
                    length = len(self.gui.data[0])
                elif str(self.gui.dataTypeEdit.currentText()) == "phased data":
                    bimarkers = self.gui.phasedToBi(self.gui.data)
                    length = len(bimarkers.values()[0])
                elif str(self.gui.dataTypeEdit.currentText()) == "unphased data":
                    phased = self.gui.phasing(self.gui.data)
                    bimarkers = self.gui.phasedToBi(dendropy.DnaCharacterMatrix.from_dict(phased))
                    length = len(bimarkers.values()[0])

                outputFile.write(str(length))
                outputFile.write(";\n")
                outputFile.write('Format datatype=dna symbols="012" missing=? gap=-;\n')
                outputFile.write("Matrix\n\n")

                # If data is bi-allelic markers, simply write out the data.
                if str(self.gui.dataTypeEdit.currentText()) == "bi-allelic markers data":
                    for taxon in self.gui.data:
                        outputFile.write(taxon.label)
                        outputFile.write(" ")
                        outputFile.write(str(self.gui.data[taxon]))
                        outputFile.write("\n")
                # If data is phased, convert into bi-allelic markers, and then write out.
                elif str(self.gui.dataTypeEdit.currentText()) == "phased data":
                    for taxon in bimarkers:
                        outputFile.write(taxon)
                        outputFile.write(" ")
                        outputFile.write(bimarkers[taxon])
                        outputFile.write("\n")
                # If data is unphased, convert into phased data first, then convert the phased data into
                # bi-allelic markers, and then write out.
                elif str(self.gui.dataTypeEdit.currentText()) == "unphased data":
                    for taxon in bimarkers:
                        outputFile.write(taxon)
                        outputFile.write(" ")
                        outputFile.write(bimarkers[taxon])
                        outputFile.write("\n")

                outputFile.write(";End;\n\n")

                # Write PHYLONET block.
                outputFile.write("BEGIN PHYLONET;\n")
                outputFile.write("MCMC_BiMarkers")
                # Write taxa list used for inference.
                outputFile.write(" -taxa (")
                outputFile.write(self.gui.taxaList[0])
                for taxon in self.gui.taxaList[1:]:
                    outputFile.write(",")
                    outputFile.write(taxon)
                outputFile.write(")")

                # Write optional commands based on user selection.
                if self.gui.chainLengthLbl.isChecked():
                    if self.gui.chainLengthEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -cl ")
                        outputFile.write(str(self.gui.chainLengthEdit.text()))

                if self.gui.burnInLbl.isChecked():
                    if self.gui.burnInEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -bl ")
                        outputFile.write(str(self.gui.burnInEdit.text()))

                if self.gui.sampleFrequencyLbl.isChecked():
                    if self.gui.sampleFrequencyEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -sf ")
                        outputFile.write(str(self.gui.sampleFrequencyEdit.text()))

                if self.gui.parThreadLbl.isChecked():
                    if self.gui.parThreadEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -pl ")
                        outputFile.write(str(self.gui.parThreadEdit.text()))

                if self.gui.tempListLbl.isChecked():
                    if self.gui.tempListEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -mc3 ")
                        outputFile.write(str(self.gui.tempListEdit.text()))

                if self.gui.maxRetLbl.isChecked():
                    if self.gui.maxRetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -mr ")
                        outputFile.write(str(self.gui.maxRetEdit.text()))

                if self.gui.taxamapLbl.isChecked():
                    if len(self.gui.taxamap) == 0:
                        pass
                    else:
                        # Get a mapping from species to taxon.
                        speciesToTaxonMap = self.gui.inverseMapping(self.gui.taxamap)
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

                if self.gui.thetaLbl.isChecked():
                    if self.gui.thetaEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -fixtheta ")
                        outputFile.write(str(self.gui.thetaEdit.text()))

                if self.gui.varyThetaLbl.isChecked():
                    outputFile.write(" -varytheta")

                if self.gui.espThetaLbl.isChecked():
                    outputFile.write(" -esptheta")

                if self.gui.ppLbl.isChecked():
                    if self.gui.ppEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -pp ")
                        outputFile.write(str(self.gui.ppEdit.text()))

                if self.gui.ddLbl.isChecked():
                    outputFile.write(" -dd")

                if self.gui.eeLbl.isChecked():
                    if self.gui.eeEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -ee ")
                        outputFile.write(str(self.gui.eeEdit.text()))

                if self.gui.sNetLbl.isChecked():
                    if self.gui.sNetEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -snet ")
                        outputFile.write(str(self.gui.sNetEdit.text()))

                if self.gui.startingThetaPriorLbl.isChecked():
                    if self.gui.startingThetaPriorEdit.text().isEmpty():
                        pass
                    else:
                        outputFile.write(" -ptheta ")
                        outputFile.write(str(self.gui.startingThetaPriorEdit.text()))

                if self.gui.diploidLbl.isChecked():
                    outputFile.write(" -diploid")

                if self.gui.dominantMarkerLbl.isChecked():
                    outputFile.write(" -dominant ")
                    outputFile.write(str(self.gui.dominantMarkerEdit.currentText()))

                if self.gui.opLbl.isChecked():
                    outputFile.write(" -op")

                outputFile.write(";\n")
                outputFile.write("END;")

            # Clear all data after one write.
            self.gui.cleanData()
        except Exception as e:
            self.exception.emit(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MCMCBiMarkersPage()
    ex.show()
    sys.exit(app.exec_())
