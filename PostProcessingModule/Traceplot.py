import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolBar


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


class Traceplot(QDialog):
    def __init__(self, posterior, likelihood, prior, numReticulation, parent=None):
        """
        posterior, likelihood, and prior are tuples. First element is x axis. Second element is y axis.
        numReticulation is a list of numbers.
        """
        super(Traceplot, self).__init__(parent)

        self.posterior = posterior
        self.likelihood = likelihood
        self.prior = prior
        self.numReticulation = numReticulation

        self.initUI()

    def initUI(self):
        # plot figures
        self.figure = plt.figure(figsize=(15, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolBar = NavigationToolBar(self.canvas, self)

        # buttons for selecting different plots
        posteriorBtn = QPushButton("Posterior")
        posteriorBtn.clicked.connect(self.plotPosterior)
        likelihoodBtn = QPushButton("Likelihood")
        likelihoodBtn.clicked.connect(self.plotLikelihood)
        priorBtn = QPushButton("Prior")
        priorBtn.clicked.connect(self.plotPrior)
        numRetBtn = QPushButton("Number of reticulations")
        numRetBtn.clicked.connect(self.plotNumRet)

        # layouts
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(posteriorBtn)
        btnLayout.addWidget(likelihoodBtn)
        btnLayout.addWidget(priorBtn)
        btnLayout.addWidget(numRetBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.toolBar)
        mainLayout.addWidget(self.canvas)
        mainLayout.addLayout(btnLayout)

        self.setWindowTitle("Trace plots")
        self.setLayout(mainLayout)

    def plotPosterior(self):
        plt.cla()
        ax = self.figure.add_subplot(111)
        x = self.posterior[0]
        y = self.posterior[1]
        ax.plot(x, y)
        ax.set_title("Posterior trace plot")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Probability")
        self.canvas.draw()

    def plotLikelihood(self):
        plt.cla()
        ax = self.figure.add_subplot(111)
        x = self.likelihood[0]
        y = self.likelihood[1]
        ax.plot(x, y)
        ax.set_title("Likelihood trace plot")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Likelihood")
        self.canvas.draw()

    def plotPrior(self):
        plt.cla()
        ax = self.figure.add_subplot(111)
        x = self.prior[0]
        y = self.prior[1]
        ax.plot(x, y)
        ax.set_title("Prior trace plot")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Probability")
        self.canvas.draw()

    def plotNumRet(self):
        plt.cla()
        ax = self.figure.add_subplot(111)
        x = self.numReticulation
        ax.hist(x)
        ax.set_title("Number of reticulations histogram")
        ax.set_xlabel("Number of reticulations")
        ax.set_ylabel("Number of appearances")
        self.canvas.draw()


if __name__ == '__main__':
    tree = ET.parse("/Users/liu/MCMC_SEQ.xml")
    root = tree.getroot()

    x_1 = []
    y_1 = []
    ind = 0

    for point in root.find("posterior"):
        x_1.append(ind)
        y_1.append(float(point.text))
        ind += 1

    x_2 = []
    y_2 = []
    ind_2 = 0
    for point in root.find("likelihood"):
        x_2.append(ind_2)
        y_2.append(float(point.text))
        ind_2 += 1

    x_3 = []
    y_3 = []
    ind_3 = 0
    for point in root.find("prior"):
        x_3.append(ind_3)
        y_3.append(float(point.text))
        ind_3 += 1

    x_4 = []
    for point in root.find("numReticulation"):
        x_4.append(int(point.text))

    app = QApplication(sys.argv)
    ex = Traceplot((x_1, y_1), (x_2, y_2), (x_3, y_3), x_4, None)
    ex.show()
    sys.exit(app.exec_())