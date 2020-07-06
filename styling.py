# css styling
def style():
    return """
        QDialog{
            background-color: #323642;

            min-width: 1300px;
            min-height: 800px;
        }
        QMainWindow{
            background-color: #323642;
        }
        QWizard{
            background-color: white;
        }
        QWizardPage{
            background-color: #323642;
            width: 100%;
            height: 100%;
        }
        QFrame{
            background-color: #323642;
        }
        QFrame#topFrame{            
            max-width: 750px;
            max-height: 450px;

            margin-left: 170px; 
            margin-bottom: 50px;
        }
        QFrame#line{
            background-color: #77ACE1;
        }
        QFrame#optionFrame{
            color: white;

            height: 100%;

            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QLabel#image{
            height: 16px;
            width: 16px;
        }
        QLabel#phylonetLabel{
            color: white;
            font-size : 48pt;
            font-weight: 400;

            margin: 30px;
        }
        QLabel#titleLabel{
            font-size : 30px;
            font-weight: 400;
            color: white;
            
            height: 100px;
            qproperty-alignment: AlignCenter;
        }
        QLabel#instructionInput, QLabel#instructionMCMC, QLabel#instructionInference, QLabel#instructionPrior, QLabel#instructionLabelStarting{
            font-size : 18px;
            font-weight: 400;
            color: white;
            padding: 10px;
        }
        QLabel#questionLabel{            
            font-family: Arial, Helvetica, Sans-serif;
            font-size : 24px;
            qproperty-alignment: AlignCenter;
            color: white;

            height: 100%;
            width: 100%;
            border: 20px;
            padding: 20px;
        }
        QPushButton#gtrEdit, QPushButton#diploidEdit, QPushButton#taxamapEdit{
            background-color: white;
            font-size: 14pt;
            color: #323642;
            min-width: 100px;
            min-height: 20px;
            
            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QPushButton#infoButton{
            font-size: 24px;

            background-color: #323642;
            color: white;
            
            height: 25px;
            width: 25px;
            margin: 0;

            border: 3px solid #77ACE1;
            border-radius: 12.5px;
        }
        QPushButton#questionButton{
            font-size: 24px;

            background-color: #323642;
            color: white;
            
            height: 25px;
            width: 25px;
            margin: 0;

            border: 3px solid #77ACE1;
            border-radius: 12.5px;
        }
        QPushButton#cancel, QPushButton#set{
            font-size: 20pt;
            background-color: #323642;
            color: white;

            max-width: 150px;
            max-height: 100px;
            margin-bottom: 50px;

            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QPushButton{
            font-size: 20pt;
            background-color: #323642;
            color: white;

            max-width: 450px;
            max-height: 450px;
            margin-bottom: 50px;

            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QPushButton:hover, QRadioButton:hover, QToolButton#fileSelctionBtn:hover{
            background-color: #69718A;
        }
        QMessageBox{           
            background-color: #323642;
            color: white; 

            font-family: Arial, Helvetica, sans-serif;
            font-size: 16px;
        }
        QRadioButton{
            font-size: 20pt;
            color: white;

            max-width: 700px;
            margin-left: 150px;
            padding: 20px;
            
            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QToolButton#fileSelctionBtn, QPushButton#launchBtn{
            font-size: 20pt;
            color: white;

            width: 1200px; 
            height: 75px;
                        
            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QTextEdit, QLineEdit{
            background-color: white;
            color: #323642;

            min-height: 20px;
            margin: 5px;
        }
        QTableWidget, QLabel, QCheckBox, QToolButton#outDirBtn{
            color: white;
            min-height: 20px;
            margin: 5px;
        }
        """
