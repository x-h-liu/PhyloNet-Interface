import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import xml.etree.ElementTree as ET

import PostProcessingModule.MPNetworkDisp


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


class PNetworkMPPage(QDialog):
    def __init__(self, fname, parent=None):
        super(PNetworkMPPage, self).__init__(parent)

        self.file = fname

        self.initUI()

    def initUI(self):
        wid = QWidget()
        scroll = QScrollArea()

        # Read in xml structure.
        tree = ET.parse(self.file)
        root = tree.getroot()

        if root.find("command").text != "InferNetwork_MP":
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
        commandText = QLabel("InferNetwork_MP")
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
            elif param.tag == "rd":
                title = QLabel("Maximum diameter to make an arrangement during network search:")
            elif param.tag == "n":
                title = QLabel("Number of optimal networks to return:")
            elif param.tag == "m":
                title = QLabel("Maximum number of network topologies to examine:")
            elif param.tag == "s":
                title = QLabel("The network to start search:")
            elif param.tag == "b":
                title = QLabel("Gene trees bootstrap threshold:")
            elif param.tag == "h":
                title = QLabel("A set of specified hybrid species:")
            elif param.tag == "f":
                title = QLabel("The maximum number of consecutive failures before the search terminates:")
            elif param.tag == "pl":
                title = QLabel("Number of processors:")
            elif param.tag == "x":
                title = QLabel("The number of runs of the search:")
            elif param.tag == "w":
                title = QLabel("The weights of operations for network arrangement during the network search:")
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

        disp = MPNetworkDisp.MPNetworkDisp(inferredNetworks, self)
        disp.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PNetworkMPPage("/Users/liu/Desktop/testdata/xml/InferNetwork_MP.xml")
    ex.show()
    sys.exit(app.exec_())
