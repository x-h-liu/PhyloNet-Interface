import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import dendropy


class DiploidListDlg(QDialog):
    """
    The dialog for setting diploid species list.
    First argument is a taxon_namespace object. The GUI will
    display a checkbox for each taxon.
    Second argument is a list of current selected diploid species,
    which is used to pre-select checkboxes.
    """
    def __init__(self, namespace, currentList, parent=None):
        super(DiploidListDlg, self).__init__(parent)

        self.namespace = namespace
        self.diploidSpecies = list(currentList)

        self.initUI()

    def initUI(self):
        """
        Initialize GUI.
        """
        species = QVBoxLayout()

        titleLabel = QLabel("Please select diploid species:")
        species.addWidget(titleLabel)
        titleFont = QFont()
        titleFont.setFamily("Helvetica")
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)

        # Set one checkbox for each taxon.
        for taxon in self.namespace:
            checkBox = QCheckBox(taxon.label)
            checkBox.setObjectName(taxon.label)
            if taxon.label in self.diploidSpecies:
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

        topLevelLayout = QVBoxLayout()
        topLevelLayout.addLayout(species)
        topLevelLayout.addLayout(btnLayout)

        self.setLayout(topLevelLayout)

    def onChecked(self):
        """
        If a taxon is checked, add that taxon to diploid species list.
        If a taxon is de-checked, remove that taxon from diploid species list.
        """
        if self.sender().isChecked():
            self.diploidSpecies.append(str(self.sender().objectName()))
        else:
            self.diploidSpecies.remove(str(self.sender().objectName()))

    def getDiploidSpeciesList(self):
        """
        Return diploid species list to caller.
        """
        return self.diploidSpecies


if __name__ == '__main__':
    dna = dendropy.DnaCharacterMatrix.get(path="/Users/liu/Desktop/testdata/sequences/yeast28/YAL053W.nexus",
                                          schema="nexus")
    app = QApplication(sys.argv)
    ex = DiploidListDlg(dna.taxon_namespace, ["Scer", "Spar"], parent=None)
    ex.show()
    sys.exit(app.exec_())




