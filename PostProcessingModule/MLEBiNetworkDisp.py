import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtCore

import xml.etree.ElementTree as ET


class MLEBiNetworkDisp(QDialog):
    def __init__(self, runs, parent=None):
        super(MLEBiNetworkDisp, self).__init__(parent)

        self.runs = runs

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        topLevelLayout = QVBoxLayout()

        font = QFont()
        font.setBold(True)
        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Copperplate")

        index = 1
        for runTuple in self.runs:
            # Huge title of run number
            runTitle = QLabel("Results after run #%d:" % index)
            runTitle.setFont(titleFont)

            # Titles for each result parameter
            stateTitle = QLabel("State:")
            stateTitle.setFont(font)
            topoTitle = QLabel("Topology:")
            topoTitle.setFont(font)
            gammaTitle = QLabel("Gamma mean:")
            gammaTitle.setFont(font)
            likelihoodTitle = QLabel("Likelihood:")
            likelihoodTitle.setFont(font)
            dendroscopeTitle = QLabel("Visualize in Dendroscope:")
            dendroscopeTitle.setFont(font)
            optimalTitle = QLabel("Optimal networks:")
            optimalTitle.setFont(font)

            # Contents
            stateText = QTextEdit()
            stateText.setText(runTuple[0])
            topoText = QLineEdit()
            topoText.setText(runTuple[1])
            gammaText = QLabel(runTuple[2])
            likelihoodText = QLabel(runTuple[3])
            dendroscopeText = QTextEdit()
            dendroscopeText.setText(runTuple[4])
            optimalText = QTextEdit()
            optimalText.setText(runTuple[5])

            optimalFont = optimalText.document().defaultFont()  # Automatic adjust QTextEdit's height according to
            fontMetrics = QFontMetrics(optimalFont)             # text's height
            textSize = fontMetrics.size(0, runTuple[5])
            textHeight = textSize.height() + 30
            optimalText.setMinimumHeight(textHeight)

            # Layouts
            stateLayout = QHBoxLayout()
            stateLayout.addWidget(stateTitle)
            stateLayout.addWidget(stateText)

            topoLayout = QHBoxLayout()
            topoLayout.addWidget(topoTitle)
            topoLayout.addWidget(topoText)

            gammaLayout = QHBoxLayout()
            gammaLayout.addWidget(gammaTitle)
            gammaLayout.addWidget(gammaText)

            likelihoodLayout = QHBoxLayout()
            likelihoodLayout.addWidget(likelihoodTitle)
            likelihoodLayout.addWidget(likelihoodText)

            dendroscopeLayout = QHBoxLayout()
            dendroscopeLayout.addWidget(dendroscopeTitle)
            dendroscopeLayout.addWidget(dendroscopeText)

            optimalLayout = QHBoxLayout()
            optimalLayout.addWidget(optimalTitle)
            optimalLayout.addWidget(optimalText)

            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)

            entireLayout = QVBoxLayout()
            entireLayout.addWidget(runTitle)
            entireLayout.addLayout(stateLayout)
            entireLayout.addLayout(topoLayout)
            entireLayout.addLayout(gammaLayout)
            entireLayout.addLayout(likelihoodLayout)
            entireLayout.addLayout(dendroscopeLayout)
            entireLayout.addLayout(optimalLayout)
            entireLayout.addWidget(line)
            # Add current run to top layout
            topLevelLayout.addLayout(entireLayout)
            index += 1

        mainLayout = QHBoxLayout()
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(790)
        scroll.setMinimumHeight(500)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    tree = ET.parse("/Users/liu/Desktop/testdata/xml/MLE_BiMarkers.xml")
    root = tree.getroot()

    runs = []
    for run in root.find("result"):
        runs.append((run.find("State").text, run.find("Topology").text, run.find("GammaMean").text,
                     run.find("Likelihood").text, run.find("dendroscope").text, run.find("OptimalNetworks").text))

    app = QApplication(sys.argv)
    ex = MLEBiNetworkDisp(runs)
    ex.show()
    sys.exit(app.exec_())