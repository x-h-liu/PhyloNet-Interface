import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtCore

import xml.etree.ElementTree as ET


class MCMCNetworkDisp(QDialog):
    def __init__(self, overallMAP, credibleSet, parent=None):
        """
        overallMAP is a list of two elements. First element is newick string of overall MAP. Second element is MAP score.
        credibleSet is a list of tuples. Each tuple consists of rank, size, percent, and newick string.
        """
        super(MCMCNetworkDisp, self).__init__(parent)

        self.overallMAP = overallMAP
        self.credibleSet = credibleSet

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        # Huge labels
        overallMAPLabel = QLabel("Overall MAP:")
        credibleSetLabel = QLabel("95% credible set of topologies:")

        titleFont = QFont()
        titleFont.setPointSize(24)
        titleFont.setFamily("Copperplate")
        overallMAPLabel.setFont(titleFont)
        credibleSetLabel.setFont(titleFont)

        # Titles for overall map
        overallMAPNetworkTitle = QLabel("Overall MAP network:")
        overallMAPMAPTitle = QLabel("MAP:")
        font = QFont()
        font.setBold(True)
        overallMAPNetworkTitle.setFont(font)
        overallMAPMAPTitle.setFont(font)

        # Contents for overall map
        overallMAPNetworkText = QTextEdit()
        overallMAPNetworkText.setText(self.overallMAP[0])
        overallMAPNetworkText.setMinimumWidth(500)
        overallMAPMAPText = QLabel(self.overallMAP[1])

        # Layout for overall map
        overallMAPNetworkLayout = QHBoxLayout()
        overallMAPNetworkLayout.addWidget(overallMAPNetworkTitle)
        overallMAPNetworkLayout.addWidget(overallMAPNetworkText)

        overallMAPMAPLayout = QHBoxLayout()
        overallMAPMAPLayout.addWidget(overallMAPMAPTitle)
        overallMAPMAPLayout.addWidget(overallMAPMAPText)

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(overallMAPLabel)
        topLevelLayout.addLayout(overallMAPNetworkLayout)
        topLevelLayout.addLayout(overallMAPMAPLayout)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        topLevelLayout.addWidget(line)

        topLevelLayout.addWidget(credibleSetLabel)

        # Display each network in credible set
        for networkTuple in self.credibleSet:
            rankTitle = QLabel("rank:")
            sizeTitle = QLabel("size:")
            percentTitle = QLabel("percent:")
            networkTitle = QLabel("network:")
            dendroTitle = QLabel("visualize in dendroscope:")
            rankTitle.setFont(font)
            sizeTitle.setFont(font)
            percentTitle.setFont(font)
            networkTitle.setFont(font)
            dendroTitle.setFont(font)

            # Contents
            networkText = QTextEdit()
            networkText.setText(networkTuple[3])
            networkText.setMinimumWidth(500)
            rankText = QLabel(networkTuple[0])
            sizeText = QLabel(networkTuple[1])
            percentText = QLabel(networkTuple[2])
            dendroText = QTextEdit()
            dendroText.setText(networkTuple[4])

            # Layouts
            networkLayout = QHBoxLayout()
            networkLayout.addWidget(networkTitle)
            networkLayout.addWidget(networkText)

            rankLayout = QHBoxLayout()
            rankLayout.addWidget(rankTitle)
            rankLayout.addWidget(rankText)

            sizeLayout = QHBoxLayout()
            sizeLayout.addWidget(sizeTitle)
            sizeLayout.addWidget(sizeText)

            percentLayout = QHBoxLayout()
            percentLayout.addWidget(percentTitle)
            percentLayout.addWidget(percentText)

            dendroLayout = QHBoxLayout()
            dendroLayout.addWidget(dendroTitle)
            dendroLayout.addWidget(dendroText)

            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)

            entireLayout = QVBoxLayout()
            entireLayout.addLayout(rankLayout)
            entireLayout.addLayout(sizeLayout)
            entireLayout.addLayout(percentLayout)
            entireLayout.addLayout(networkLayout)
            entireLayout.addLayout(dendroLayout)
            entireLayout.addWidget(line)
            # Add current network display to top layout
            topLevelLayout.addLayout(entireLayout)

        mainLayout = QHBoxLayout()
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(790)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    tree = ET.parse("/Users/liu/Desktop/testdata/xml/seqCredibleSet.xml")
    root = tree.getroot()

    overallmap = [root.find("OverallMAP")[0].text, root.find("OverallMAP")[1].text]

    networks = []
    for network in root.findall("network"):
        networks.append((network[0].text, network[1].text, network[2].text, network[4].text, network[5].text))

    app = QApplication(sys.argv)
    ex = MCMCNetworkDisp(overallmap, networks)
    ex.show()
    sys.exit(app.exec_())