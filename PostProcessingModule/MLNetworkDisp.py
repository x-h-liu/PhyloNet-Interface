import sys
import os
from PyQt4.QtGui import *
from PyQt4 import QtCore

import xml.etree.ElementTree as ET


class MLNetworkDisp(QDialog):
    def __init__(self, inferredNetworks, parent=None):
        super(MLNetworkDisp, self).__init__(parent)

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
            logProbTitle = QLabel("Total log probability:")
            networkTitle.setFont(font)
            logProbTitle.setFont(font)
            # Contents of network and log probability
            networkText = QTextEdit()
            networkText.setText(networkTuple[0])
            networkText.setMinimumWidth(500)
            logProbText = QLabel(networkTuple[1])
            # Layouts
            networkLayout = QHBoxLayout()
            networkLayout.addWidget(networkTitle)
            networkLayout.addWidget(networkText)

            logProbLayout = QHBoxLayout()
            logProbLayout.addWidget(logProbTitle)
            logProbLayout.addWidget(logProbText)

            line = QFrame(self)
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)

            entireLayout = QVBoxLayout()
            entireLayout.addLayout(networkLayout)
            entireLayout.addLayout(logProbLayout)
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
        # logProbTitle = QLabel("Total log probability:")
        #
        # # Font of titles
        # font = QFont()
        # font.setBold(True)
        # networkTitle.setFont(font)
        # logProbTitle.setFont(font)
        #
        # # Results from PhyloNet
        # networkText = QTextEdit()
        # networkText.setText(self.newickString)
        # networkText.setMinimumWidth(500)
        # logProbText = QLabel(self.logProb)
        #
        # # Layouts
        # networkLayout = QHBoxLayout()
        # networkLayout.addWidget(networkTitle)
        # networkLayout.addWidget(networkText)
        #
        # logProbLayout = QHBoxLayout()
        # logProbLayout.addWidget(logProbTitle)
        # logProbLayout.addWidget(logProbText)
        #
        # # Main layout
        # topLevelLayout = QVBoxLayout()
        # topLevelLayout.addLayout(networkLayout)
        # topLevelLayout.addLayout(logProbLayout)
        #
        # self.setLayout(topLevelLayout)


if __name__ == '__main__':
    tree = ET.parse("/Users/liu/Desktop/testdata/xml/InferNetwork_MPL.xml")
    root = tree.getroot()

    networks = []
    for network in root.findall("network"):
        networks.append((network[0].text, network[1].text))

    app = QApplication(sys.argv)
    ex = MLNetworkDisp(networks)
    ex.show()
    sys.exit(app.exec_())
