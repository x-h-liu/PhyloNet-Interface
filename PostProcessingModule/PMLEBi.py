import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtCore
import xml.etree.ElementTree as ET

import MLEBiNetworkDisp


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


class PMLEBiPage(QDialog):
    def __init__(self, fname, parent=None):
        super(PMLEBiPage, self).__init__(parent)

        self.file = fname

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        # Read in xml structure.
        tree = ET.parse(self.file)
        root = tree.getroot()

        if root.find("command").text != "MLE_BiMarkers":
            raise RuntimeError

        # Titles and font
        commandTitle = QLabel("Command executed:")
        timeTitle = QLabel("Starting Time:")
        parameterTitle = QLabel("Parameters:")

        font = QFont()
        font.setBold(True)
        commandTitle.setFont(font)
        timeTitle.setFont(font)
        parameterTitle.setFont(font)

        # Values
        commandText = QLabel("MLE_BiMarkers")
        timeText = QLabel(root.find("date").text)

        # Read all the user-specified parameters and create labels for each pair of tag and value.
        parameters = []
        titleFont = QFont()
        titleFont.setItalic(True)
        titleFont.setBold(True)
        for param in root.find("parameters"):
            if param.tag == "pseudo":
                title = QLabel("Use pseudolikelihood:")
            elif param.tag == "diploid":
                title = QLabel("Sequence sampled from diploids:")
            elif param.tag == "dominant":
                title = QLabel("Dominant marker:")
            elif param.tag == "op":
                title = QLabel("Ignore all monomorphic sites:")
            elif param.tag == "taxa":
                title = QLabel("The taxa used for inference:")
            elif param.tag == "pl":
                title = QLabel("The number of threads running in parallel:")
            elif param.tag == "mno":
                title = QLabel("The number of optimal networks to print:")
            elif param.tag == "mnr":
                title = QLabel("The number of iterations of simulated annealing:")
            elif param.tag == "mf":
                title = QLabel("The maximum allowed times of failures to accept a new state during one iteration:")
            elif param.tag == "mec":
                title = QLabel("The maximum allowed times of examining a state during one iteration:")
            elif param.tag == "mr":
                title = QLabel("The maximum number of reticulation nodes in the sampled phylogenetic networks:")
            elif param.tag == "tm":
                title = QLabel("Gene tree / species tree taxa association:")
            elif param.tag == "fixtheta":
                title = QLabel("Fix the population mutation rates associated with all branches to:")
            elif param.tag == "varytheta":
                title = QLabel("The population mutation rates across all branches may be different:")
            elif param.tag == "esptheta":
                title = QLabel("Estimate the mean value of prior of population mutation rates:")
            elif param.tag == "thetawindow":
                title = QLabel("The starting value of population mutation rate:")
            elif param.tag == "snet":
                title = QLabel("Starting network:")
            elif param.tag == "ptheta":
                title = QLabel("The mean value of prior of population mutation rate:")
            else:
                continue
            title.setFont(titleFont)
            val = QLabel(param.text)
            val.setWordWrap(True)
            parameters.append((title, val))

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

        # Separation lines
        line1 = QFrame(self)
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame(self)
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addLayout(commandLayout)
        topLevelLayout.addWidget(line1)
        topLevelLayout.addLayout(timeLayout)
        topLevelLayout.addWidget(line2)
        topLevelLayout.addLayout(parametersLayout)

        mainLayout = QHBoxLayout()
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(790)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)

        runs = []
        # Display results of each run
        for run in root.find("result"):
            runs.append((run.find("State").text, run.find("Topology").text, run.find("GammaMean").text,
                         run.find("Likelihood").text, run.find("dendroscope").text, run.find("OptimalNetworks").text))

        disp = MLEBiNetworkDisp.MLEBiNetworkDisp(runs, self)
        disp.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PMLEBiPage("/Users/liu/Desktop/testdata/xml/MLE_BiMarkers.xml")
    ex.show()
    sys.exit(app.exec_())
