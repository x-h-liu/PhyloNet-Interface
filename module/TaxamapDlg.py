import sys
from PyQt4.QtGui import *
from PyQt4 import QtCore
import dendropy

import GuessDlg


class TaxamapDlg(QDialog):
    """
    The dialog for setting gene / species taxa association.
    First argument is taxon namespace, which will be displayed on table.
    Second argument is the current taxa association passed in by caller.
    """
    def __init__(self, namespace, currentMap, parent=None):
        super(TaxamapDlg, self).__init__(parent)

        self.namespace = namespace
        self.taxamap = {}
        for taxon in self.namespace:
            self.taxamap[taxon.label] = currentMap[taxon.label]

        # the current taxa map to display
        self.currentMap = currentMap

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        # A table for mapping
        self.table = QTableWidget()
        self.table.setRowCount(len(self.namespace))
        self.table.setColumnCount(2)
        header = self.table.horizontalHeader()
        header.setResizeMode(0, QHeaderView.ResizeToContents)
        header.setResizeMode(1, QHeaderView.Stretch)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem("taxon"))
        self.table.setHorizontalHeaderItem(1, QTableWidgetItem("species"))

        # Set the initial mapping from the information passed in by caller
        for i in range(len(self.namespace)):
            self.table.setItem(i, 0, QTableWidgetItem(self.namespace[i].label))
            self.table.setItem(i, 1, QTableWidgetItem(self.currentMap[self.namespace[i].label]))

        # Main layout
        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(self.table)

        # Buttons
        guess = QPushButton("Guess")
        cancel = QPushButton("Cancel")
        set = QPushButton("Set")
        set.setDefault(True)
        guess.clicked.connect(self.guess)
        set.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(guess)
        btnLayout.addWidget(cancel)
        btnLayout.addWidget(set)

        topLevelLayout.addLayout(btnLayout)

        self.setLayout(topLevelLayout)

    def guess(self):
        """
        Set species names according to user's specification.
        User's input comes from GuessDlg.
        """
        dialog = GuessDlg.GuessDlg(parent=self)
        if dialog.exec_():
            info = dialog.getInfo()
            if info[2] == "white space":
                delimiter = " "
            else:
                delimiter = info[2]

            # Split taxon names according to user specified delimiter.
            if info[0] == "before":
                if info[1] == "first":
                    for taxonName in self.taxamap:
                        self.taxamap[taxonName] = taxonName.split(delimiter, 1)[0]
                else:
                    for taxonName in self.taxamap:
                        self.taxamap[taxonName] = taxonName.rsplit(delimiter, 1)[0]
            else:
                if info[1] == "first":
                    for taxonName in self.taxamap:
                        self.taxamap[taxonName] = taxonName.split(delimiter, 1)[1] if \
                            len(taxonName.split(delimiter, 1)) == 2 else taxonName
                else:
                    for taxonName in self.taxamap:
                        self.taxamap[taxonName] = taxonName.rsplit(delimiter, 1)[1] if \
                            len(taxonName.rsplit(delimiter, 1)) == 2 else taxonName

            # Display result on table.
            for i in range(len(self.namespace)):
                self.table.item(i, 1).setText(self.taxamap[str(self.table.item(i, 0).text())])

    def accept(self):
        """
        When user clicks "Set", update the internal taxa map based on what user
        enters in table.
        """
        try:
            for i in range(len(self.namespace)):
                if str(self.table.item(i, 1).text()) == "":
                    # If user omits a taxon, throw a warning
                    raise Exception
                else:
                    # Set taxa map
                    self.taxamap[str(self.table.item(i, 0).text())] = str(self.table.item(i, 1).text())
            QDialog.accept(self)
        except Exception:
            QMessageBox.warning(self, "Warning", "Please map all taxon.", QMessageBox.Ok)

    def getTaxamap(self):
        """
        Return the current taxa map to caller.
        """
        return self.taxamap


if __name__ == '__main__':
    newick_trees = dendropy.TreeList()
    newick_trees.read(path="/Users/liu/Desktop/testdata/genetrees/genetrees.newick", schema="newick")

    map = {}

    for taxon in newick_trees.taxon_namespace:
        map[taxon.label] = taxon.label

    app = QApplication(sys.argv)
    ex = TaxamapDlg(newick_trees.taxon_namespace, map, parent=None)
    ex.show()
    sys.exit(app.exec_())

