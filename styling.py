
# css styling
def style():
    return """
        QMainWindow{
            background-color: white;
            font-family:  "Franklin Gothic Medium", "Arial", Sans-serif;
            padding: 30px 50px 30px 30px;
        }
        QDialog{
            background-color: white;

            min-width: 1300px;
            min-height: 1200px;
        }
        QDialog#aboutMessage{
            min-width: 500px;
            min-height: 500px;
            width: 100%;
            height: 100%;
            font-size: 12pt;
        }
        QDialog#successMessage{
            min-height: 500px;
            min-width: 500px;
        }
        QWizard{
            background-color: white;
            font-family:  "Franklin Gothic Medium", "Arial", Sans-serif;
        }
        QWizardPage{
            background-color: white;
            width: 100%;
            height: 100%;
            font-family: "Franklin Gothic Medium", "Arial", Sans-serif;
        }
        QWidget{
            font-family:  "Franklin Gothic Medium", "Arial", Sans-serif;            
        }
        QTableWidget{
            min-width: 1000px;
            min-height: 1200px;
        }
        QFrame{
            background-color: white;
        }
        QFrame#topFrame{            
            max-width: 750px;
            max-height: 450px;

            margin-left: 170px; 
            margin-bottom: 50px;
        }
        QFrame#optionFrame{
            color: Black;

            height: 100%;

            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }
        QTextEdit, QLineEdit{
            background-color: white;
            color: Black;

            min-height: 40px;
            margin: 5px;
        }
        QCheckBox{
            font-size: 10pt;
        }
        QLabel{
            font-size: 10pt;
            padding-bottom: 5px;
        }
        QTableWidget, QLabel, QToolButton#outDirBtn{
            color: Black;
            min-height: 20px;
            
            padding: 15px 0px;
        }
        QLabel#image{
            height: 16px;
            width: 16px;
        }
        QLabel#version{
            margin-top: 20px; 
            font-size: 10pt;
            color: black;
        }
        QLabel#introQuestion{
            font-size: 13pt; 
            color: #666;
        }
        QLabel#instructionLabel{
            font-size: 11pt;
            color: #2196f3;
        }
        QLabel#phylonetLabel{
            color: Black;
            font-size : 30pt;
            font-weight: 600;
            font-family: "Franklin Gothic Medium", Arial;
            min-width: 700px;
            border: 2px solid;
        }
        QLabel#detailsLink{
            border-bottom: 2px solid #ccc;
        }
        QLabel#titleLabel{
            font-size : 20pt;
            font-weight: 500;
            color: Black;
            qproperty-alignment: AlignCenter;
        }
        QLabel#instructionInput, QLabel#instructionMCMC, QLabel#instructionInference, QLabel#instructionPrior, QLabel#instructionLabelStarting{
            font-size : 18px;
            font-weight: 400;
            color: Black;
            padding: 10px;
        }
        QLabel#introLabel{
            font-size: 23pt;
            qproperty-alignment: AlignCenter;
            color: Black;

            width: 100%;
            margin-bottom: 15px;
            margin-top: 10px;
            font-weight: 600;
            font-family: "Franklin Gothic Medium", "Franklin Gothic Heavy", "Franklin Gothic Medium", "Arial", Sans-serif;
        }
        QLabel#questionLabel{            
            font-size: 20pt;
            qproperty-alignment: AlignCenter;
            color: Black;

            width: 100%;
            font-weight: 600;
            font-family: "Segoe UI","Franklin Gothic Heavy", "Franklin Gothic Medium", "Arial", Sans-serif;
        }
        QPushButton{
            font-size: 10pt;
            color: Black;

            margin-bottom: 35px;
            min-height: 50px;

            padding: 5px 20px;        
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }
        QPushButton:disabled{
            color: rgba(148, 152, 155, 0.5);
            background-color: #f1f1f1;
            border-color: rgba(33, 150, 243, 0.5);
        }
        QPushButton:enabled{
            background-color: white;
            color: Black;
        }
        QPushButton:hover{
            background-color: #d5f6ff;
        }
        QPushButton#gtrEdit, QPushButton#diploidEdit, QPushButton#taxamapEdit{
            font-size: 8pt;
            padding: 5px;
            text-align: center;
            min-width: 200px;
        }
        QPushButton#inputBtn, QPushButton#outputBtn{
            width: 640px;
            padding: 50px 10px;
            font-size: 35px;
            border-color: transparent;
        }
        QPushButton#inputBtn{
            background-color: #aaeeff;
        }
        QPushButton#outputBtn{
            background-color: #00ccff;
        }
        QPushButton#inputBtn:hover, QPushButton#outputBtn:hover{
            border: 5px solid black;
        }
        QPushButton#infoButton{
            font-size: 24px;

            background-color: #2196f3;
            color: white;
            
            max-height: 50px;
            max-width: 50px;
            margin-top: 1em;
            padding: 1em;

            border-radius: 25px;
        }
        QPushButton#questionButton{
            font-size: 24px;
            color: Black;
            
            height: 25px;
            width: 25px;
            margin: 0;

            border: 3px solid #77ACE1;
            border-radius: 12.5px;
        }
        QPushButton#cancel, QPushButton#set{
            font-size: 20px;
            color: Black;

            max-width: 150px;
            max-height: 100px;
            margin-bottom: 50px;

            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }

        QMessageBox{           
            background-color: white;
            color: Black; 

            font-family: Arial, Helvetica, sans-serif;
            font-size: 12pt;
        }
        QRadioButton{
            font-size: 30px;
            
            padding: 20px;
            width: 900px;
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }
        QToolButton#fileSelctionBtn, QPushButton#launchBtn{
            font-size: 20px;
            color: Black;

            width: 1200px; 
            height: 75px;
                        
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }

        """
