import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import xml.etree.ElementTree as ET


class MCMCBiNetworkDisp(QDialog):
    def __init__(self, overallMAP, credibleSet, parent=None):
        """
        overallMAP is a list of two elements. First element is newick string of overall MAP. Second element is MAP score.
        credibleSet is a list of tuples. Each tuple consists of rank, size, percent, and newick string.
        """
        super(MCMCBiNetworkDisp, self).__init__(parent)

        self.overallMAP = overallMAP
        self.credibleSet = credibleSet

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        # Huge labels
        overallMAPLabel = QLabel("Overall MAP:")
        credibleSetLabel = QLabel("Top topologies:")

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
            rankTitle = QLabel("Rank:")
            sizeTitle = QLabel("Size:")
            percentTitle = QLabel("Percent:")
            MAPTitle = QLabel("MAP:")
            topologyTitle = QLabel("Topology:")
            networkTitle = QLabel("Network:")
            dendroTitle = QLabel("Visualize in Dendroscope:")
            rankTitle.setFont(font)
            sizeTitle.setFont(font)
            percentTitle.setFont(font)
            MAPTitle.setFont(font)
            topologyTitle.setFont(font)
            networkTitle.setFont(font)
            dendroTitle.setFont(font)

            # Contents
            networkText = QTextEdit()
            networkText.setText(networkTuple[5])
            networkText.setMinimumWidth(500)
            rankText = QLabel(networkTuple[0])
            sizeText = QLabel(networkTuple[1])
            percentText = QLabel(networkTuple[2])
            MAPText = QTextEdit()
            MAPText.setText(networkTuple[3])
            topologyText = QTextEdit()
            topologyText.setText(networkTuple[4])
            dendroText = QTextEdit()
            dendroText.setText(networkTuple[6])

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

            MAPLayout = QHBoxLayout()
            MAPLayout.addWidget(MAPTitle)
            MAPLayout.addWidget(MAPText)

            topologyLayout = QHBoxLayout()
            topologyLayout.addWidget(topologyTitle)
            topologyLayout.addWidget(topologyText)

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
            entireLayout.addLayout(MAPLayout)
            entireLayout.addLayout(topologyLayout)
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
        scroll.setMinimumHeight(450)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)


if __name__ == '__main__':
    tree = ET.parse("/Users/liu/Desktop/testdata/xml/biCredibleSet.xml")
    root = tree.getroot()

    overallmap = [root.find("OverallMAP")[0].text, root.find("OverallMAP")[1].text]

    networks = []
    for network in root.findall("network"):
        networks.append((network[0].text, network[1].text, network[2].text, network[3].text, network[4].text,
                         network[5].text, network[6].text))

    app = QApplication(sys.argv)
    ex = MCMCBiNetworkDisp(overallmap, networks)
    ex.show()
    sys.exit(app.exec_())