import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import xml.etree.ElementTree as ET


class MPNetworkDisp(QDialog):
    def __init__(self, inferredNetworks, parent=None):
        super(MPNetworkDisp, self).__init__(parent)

        self.networks = inferredNetworks

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        topLevelLayout = QVBoxLayout()

        font = QFont()
        font.setBold(True)

        index = 1
        for networkTuple in self.networks:
            # Two titles for each network
            networkTitle = QLabel("Inferred Network #%d:" % index)
            extraLineagesTitle = QLabel("Total number of extra lineages:")
            networkTitle.setFont(font)
            extraLineagesTitle.setFont(font)
            # Contents of network and extra lineages
            networkText = QTextEdit()
            networkText.setText(networkTuple[0])
            networkText.setMinimumWidth(500)
            extraLineagesText = QLabel(networkTuple[1])
            # Layouts
            networkLayout = QHBoxLayout()
            networkLayout.addWidget(networkTitle)
            networkLayout.addWidget(networkText)

            extraLineagesLayout = QHBoxLayout()
            extraLineagesLayout.addWidget(extraLineagesTitle)
            extraLineagesLayout.addWidget(extraLineagesText)

            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)

            entireLayout = QVBoxLayout()
            entireLayout.addLayout(networkLayout)
            entireLayout.addLayout(extraLineagesLayout)
            entireLayout.addWidget(line)
            # Add current network display to top layout
            topLevelLayout.addLayout(entireLayout)
            index += 1

        mainLayout = QHBoxLayout()
        wid.setLayout(topLevelLayout)
        scroll.setWidget(wid)
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(790)
        mainLayout.addWidget(scroll)
        self.setLayout(mainLayout)





        # # Two titles
        # networkTitle = QLabel("Inferred Network:")
        # extraLineagesTitle = QLabel("Total number of extra lineages:")
        #
        # # Font of titles
        # font = QFont()
        # font.setBold(True)
        # networkTitle.setFont(font)
        # extraLineagesTitle.setFont(font)
        #
        # # Results from PhyloNet
        # networkText = QTextEdit()
        # networkText.setText(self.newickString)
        # networkText.setMinimumWidth(500)
        # extraLineagesText = QLabel(self.extraLineages)
        #
        # # Layouts
        # networkLayout = QHBoxLayout()
        # networkLayout.addWidget(networkTitle)
        # networkLayout.addWidget(networkText)
        #
        # extraLineagesLayout = QHBoxLayout()
        # extraLineagesLayout.addWidget(extraLineagesTitle)
        # extraLineagesLayout.addWidget(extraLineagesText)
        #
        # # Main layout
        # topLevelLayout = QVBoxLayout()
        # topLevelLayout.addLayout(networkLayout)
        # topLevelLayout.addLayout(extraLineagesLayout)
        #
        # self.setLayout(topLevelLayout)


if __name__ == '__main__':
    tree = ET.parse("/Users/liu/Desktop/testdata/xml/test.xml")
    root = tree.getroot()

    networks = []
    for network in root.findall("network"):
        networks.append((network[0].text, network[1].text))

    app = QApplication(sys.argv)
    ex = MPNetworkDisp(networks)
    ex.show()
    sys.exit(app.exec_())