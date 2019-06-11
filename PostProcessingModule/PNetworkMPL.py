import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import xml.etree.ElementTree as ET

import PostProcessingModule.MLNetworkDisp

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


class PNetworkMPLPage(QDialog):
    def __init__(self, fname, parent=None):
        super(PNetworkMPLPage, self).__init__(parent)

        self.file = fname

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        # Read in xml structure.
        tree = ET.parse(self.file)
        root = tree.getroot()

        if root.find("command").text != "InferNetwork_MPL":
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
        commandText = QLabel("InferNetwork_MPL")
        timeText = QLabel(root.find("date").text)

        # Read all the user-specified parameters and create labels for each pair of tag and value.
        parameters = []
        titleFont = QFont()
        titleFont.setItalic(True)
        titleFont.setBold(True)
        for param in root.find("parameters"):
            if param.tag == "numReticulations":
                title = QLabel("Maximum number of reticulations:")
            elif param.tag == "a":
                title = QLabel("Gene tree / species tree taxa association:")
            elif param.tag == "md":
                title = QLabel("Maximum diameter to make an arrangement during network search:")
            elif param.tag == "rd":
                title = QLabel("Maximum diameter for a reticulation event:")
            elif param.tag == "m":
                title = QLabel("Maximum number of network topologies to examine:")
            elif param.tag == "pl":
                title = QLabel("Number of processors:")
            elif param.tag == "s":
                title = QLabel("The network to start search:")
            elif param.tag == "b":
                title = QLabel("Gene trees bootstrap threshold:")
            elif param.tag == "i":
                title = QLabel("Minimum threshold of improvement to continue the next round of optimization of branch "
                               "lengths:")
            elif param.tag == "r":
                title = QLabel("Maximum number of rounds to optimize branch lengths for a network topology:")
            elif param.tag == "l":
                title = QLabel("Maximum branch lengths considered:")
            elif param.tag == "n":
                title = QLabel("Number of optimal networks to return:")
            elif param.tag == "po":
                title = QLabel("After the search the returned species networks will be optimized for their branch "
                               "lengths and inheritance probabilities under full likelihood:")
            elif param.tag == "o":
                title = QLabel("During the search, for every proposed species network, its branch lengths and "
                               "inheritance probabilities will be optimized to compute its likelihood:")
            elif param.tag == "p":
                title = QLabel("The original stopping criterion of Brent's algorithm:")
            elif param.tag == "w":
                title = QLabel("The weights of operations for network arrangement during the network search:")
            elif param.tag == "h":
                title = QLabel("A set of specified hybrid species:")
            elif param.tag == "t":
                title = QLabel("Maximum number of trial per branch in one round to optimize branch lengths for a "
                               "network topology:")
            elif param.tag == "x":
                title = QLabel("The number of runs of the search:")
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

        inferredNetworks = []
        # Display each inferred network.
        for network in root.findall("network"):
            inferredNetworks.append((network[0].text, network[1].text))

        disp = MLNetworkDisp.MLNetworkDisp(inferredNetworks, self)
        disp.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PNetworkMPLPage("/Users/liu/Desktop/testdata/xml/InferNetwork_MPL3.xml")
    ex.show()
    sys.exit(app.exec_())
