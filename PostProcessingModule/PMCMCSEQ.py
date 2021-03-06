import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtCore
import xml.etree.ElementTree as ET

import Traceplot
import MCMCNetworkDisp


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


class PMCMCSEQPage(QDialog):
    def __init__(self, fname, credibleSet, parent=None):
        """
        fname and credibleSet are file names for the two xml files generated by PhyloNet.
        """
        super(PMCMCSEQPage, self).__init__(parent)

        self.file = fname
        self.credibleSet = credibleSet

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        # Read in xml structure.
        tree = ET.parse(self.file)
        root = tree.getroot()

        if root.find("command").text != "MCMC_SEQ":
            raise RuntimeError

        # Titles and font
        commandTitle = QLabel("Command executed:")
        timeTitle = QLabel("Starting Time:")
        parameterTitle = QLabel("Parameters:")
        summarizationTitle = QLabel("Summarization:")
        operationsTitle = QLabel("Operations:")

        font = QFont()
        font.setBold(True)
        commandTitle.setFont(font)
        timeTitle.setFont(font)
        parameterTitle.setFont(font)
        summarizationTitle.setFont(font)
        operationsTitle.setFont(font)

        # Values
        commandText = QLabel("MCMC_SEQ")
        timeText = QLabel(root.find("date").text)

        # Read all the user-specified parameters and create labels for each pair of tag and value.
        parameters = []
        titleFont = QFont()
        titleFont.setItalic(True)
        titleFont.setBold(True)
        for param in root.find("parameters"):
            if param.tag == "diploid":
                title = QLabel("Diploid species list:")
            elif param.tag == "tm":
                title = QLabel("Gene tree / species tree taxa association:")
            elif param.tag == "cl":
                title = QLabel("The length of the MCMC chain:")
            elif param.tag == "bl":
                title = QLabel("The number of iterations in burn-in period:")
            elif param.tag == "sf":
                title = QLabel("The sample frequency:")
            elif param.tag == "sd":
                title = QLabel("The random seed:")
            elif param.tag == "pl":
                title = QLabel("The number of threads running in parallel:")
            elif param.tag == "dir":
                title = QLabel("The absolute path to store the output files:")
            elif param.tag == "mc3":
                title = QLabel("The list of temperatures for the Metropolis-coupled MCMC chains:")
            elif param.tag == "mr":
                title = QLabel("The maximum number of reticulation nodes in the sampled phylogenetic networks:")
            elif param.tag == "fixps":
                title = QLabel("Fix the population sizes associated with all branches of the network to:")
            elif param.tag == "varyps":
                title = QLabel("Vary the population sizes across all branches:")
            elif param.tag == "pp":
                title = QLabel("The Poisson parameter in the prior on the number of reticulation nodes:")
            elif param.tag == "dd":
                title = QLabel("Disable the prior on the diameters of hybridizations:")
            elif param.tag == "ee":
                title = QLabel("Enable the Exponential(10) prior on the divergence times of nodes in the network:")
            elif param.tag == "sgt":
                title = QLabel("Specify the starting gene trees for each locus:")
            elif param.tag == "snet":
                title = QLabel("Specify the starting network:")
            elif param.tag == "sps":
                title = QLabel("The starting population size:")
            elif param.tag == "pre":
                title = QLabel("The number of iterations for pre burn-in:")
            elif param.tag == "gtr":
                title = QLabel("Substitution model:")
            else:
                continue
            title.setFont(titleFont)
            val = QLabel(param.text)
            val.setWordWrap(True)
            parameters.append((title, val))

        # MCMC chain summary
        summaryParams = []

        burnInLabel = QLabel("Burn-in:")
        burnInLabel.setFont(titleFont)
        burnInVal = QLabel(root.find("summarization").find("BurnIn").text)
        summaryParams.append((burnInLabel, burnInVal))

        chainLengthLabel = QLabel("Chain length:")
        chainLengthLabel.setFont(titleFont)
        chainLengthVal = QLabel(root.find("summarization").find("ChainLength").text)
        summaryParams.append((chainLengthLabel, chainLengthVal))

        sampleSizeLabel = QLabel("Sample size:")
        sampleSizeLabel.setFont(titleFont)
        sampleSizeVal = QLabel(root.find("summarization").find("SampleSize").text)
        summaryParams.append((sampleSizeLabel, sampleSizeVal))

        acRateLabel = QLabel("Acceptance rate:")
        acRateLabel.setFont(titleFont)
        acRateVal = QLabel(root.find("summarization").find("AcceptanceRate").text)
        summaryParams.append((acRateLabel, acRateVal))

        # Layouts
        commandLayout = QHBoxLayout()
        commandLayout.addWidget(commandTitle)
        commandLayout.addWidget(commandText)

        timeLayout = QHBoxLayout()
        timeLayout.addWidget(timeTitle)
        timeLayout.addWidget(timeText)

        valuesLayout = QVBoxLayout()  # Layouts for each parameter
        for item in parameters:
            singleLayout = QHBoxLayout()
            singleLayout.addWidget(item[0])
            singleLayout.addWidget(item[1])
            valuesLayout.addLayout(singleLayout)
        parametersLayout = QHBoxLayout()
        parametersLayout.addWidget(parameterTitle)
        parametersLayout.addLayout(valuesLayout)

        summarizationParamLayout = QVBoxLayout()  # Layout for mcmc summarization
        for item in summaryParams:
            singleLayout = QHBoxLayout()
            singleLayout.addWidget(item[0])
            singleLayout.addWidget(item[1])
            summarizationParamLayout.addLayout(singleLayout)
        summarizationLayout = QHBoxLayout()
        summarizationLayout.addWidget(summarizationTitle)
        summarizationLayout.addLayout(summarizationParamLayout)

        operationsLayout = QVBoxLayout()  # Layout for proposal operations
        for op in root.find("operations"):
            operationsLayout.addWidget(QLabel(op.text))
        opLayout = QHBoxLayout()
        opLayout.addWidget(operationsTitle)
        opLayout.addLayout(operationsLayout)

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

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addLayout(commandLayout)
        topLevelLayout.addWidget(line1)
        topLevelLayout.addLayout(timeLayout)
        topLevelLayout.addWidget(line2)
        topLevelLayout.addLayout(parametersLayout)
        topLevelLayout.addWidget(line3)
        topLevelLayout.addLayout(summarizationLayout)
        topLevelLayout.addWidget(line4)
        topLevelLayout.addLayout(opLayout)

        mainLayout = QHBoxLayout()
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(790)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)

        self.showPlot()
        self.showNetworks()

    def showPlot(self):
        # Read in xml structure.
        tree = ET.parse(self.file)
        root = tree.getroot()

        posteriorX = []
        posteriorY = []
        posteriorIndex = 1
        for point in root.find("posterior"):
            posteriorX.append(posteriorIndex)
            posteriorY.append(float(point.text))
            posteriorIndex += 1

        likelihoodX = []
        likelihoodY = []
        likelihoodIndex = 1
        for point in root.find("likelihood"):
            likelihoodX.append(likelihoodIndex)
            likelihoodY.append(float(point.text))
            likelihoodIndex += 1

        priorX = []
        priorY = []
        priorIndex = 1
        for point in root.find("prior"):
            priorX.append(priorIndex)
            priorY.append(float(point.text))
            priorIndex += 1

        numRet = []
        for point in root.find("numReticulation"):
            numRet.append(int(point.text))

        traceplot = Traceplot.Traceplot((posteriorX, posteriorY), (likelihoodX, likelihoodY), (priorX, priorY),
                                             numRet, self)
        traceplot.show()

    def showNetworks(self):
        # Read in xml structure.
        tree = ET.parse(self.credibleSet)
        root = tree.getroot()

        overallmap = [root.find("OverallMAP")[0].text, root.find("OverallMAP")[1].text]

        networks = []
        for network in root.findall("network"):
            networks.append((network[0].text, network[1].text, network[2].text, network[4].text, network[5].text))

        self.disp = MCMCNetworkDisp.MCMCNetworkDisp(overallmap, networks)
        self.disp.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PMCMCSEQPage("/Users/liu/MCMC_SEQ.xml", "/Users/liu/CredibleSet.xml")
    ex.show()
    sys.exit(app.exec_())