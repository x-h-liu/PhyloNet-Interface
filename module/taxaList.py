import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import dendropy


class TaxaListDlg(QDialog):
    """
    The dialog for setting taxa list for inference using bi-allelic markers.
    First argument is a taxon_namespace object. The GUI will
    display a checkbox for each taxon.
    Second argument is a list of current selected taxa,
    which is used to pre-select checkboxes.
    """
    def __init__(self, namespace, currentList, parent=None):
        super(TaxaListDlg, self).__init__(parent)

        self.namespace = namespace
        self.taxa = list(currentList)

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        wid = QWidget()
        scroll = QScrollArea()

        titleLabel = QLabel("Please select taxa used for inference:")
        titleFont = QFont()
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        # Layout for list of species.
        species = QVBoxLayout()

        # Set one checkbox for each taxon.
        for taxon in self.namespace:
            checkBox = QCheckBox(taxon.label)
            checkBox.setObjectName(taxon.label)
            if taxon.label in self.taxa:
                checkBox.setChecked(True)
            checkBox.stateChanged.connect(self.onChecked)
            species.addWidget(checkBox)

        # Buttons
        cancel = QPushButton("Cancel")
        set = QPushButton("Set")
        set.setDefault(True)
        set.clicked.connect(self.accept)
        cancel.clicked.connect(self.reject)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(cancel)
        btnLayout.addWidget(set)

        # List should be scrollable
        wid.setLayout(species)
        scroll.setWidget(wid)

        topLevelLayout = QVBoxLayout()
        topLevelLayout.addWidget(titleLabel)
        topLevelLayout.addWidget(scroll)
        topLevelLayout.addLayout(btnLayout)

        self.setLayout(topLevelLayout)

    def onChecked(self):
        """
        If a taxon is checked, add that taxon to taxa list.
        If a taxon is de-checked, remove that taxon from taxa list.
        """
        if self.sender().isChecked():
            self.taxa.append(str(self.sender().objectName()))
        else:
            self.taxa.remove(str(self.sender().objectName()))

    def getTaxaList(self):
        """
        Return taxa list to caller.
        """
        return self.taxa


if __name__ == '__main__':
    dna = dendropy.DnaCharacterMatrix.get(path="/Users/liu/Desktop/testdata/sequences/yeast28/YAL053W.nexus",
                                          schema="nexus")
    app = QApplication(sys.argv)
    ex = TaxaListDlg(dna.taxon_namespace, ["Scer", "Spar"], parent=None)
    ex.show()
    sys.exit(app.exec_())