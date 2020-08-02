
# css styling
def style():
    return """
        QMainWindow{
            background-color: white;
            font-family: "Arial", Sans-serif;
            padding: 30px 50px 30px 30px;
        }
        QDialog{
            background-color: white;
            min-width: 1300px;
            min-height: 800px;
        }
        QDialog#aboutMessage{
            min-width: 500px;
            min-height: 500px;
            width: 100%;
            height: 100%;
            font-size: 14px;
        }
        QDialog#successMessage{
            min-height: 500px;
            min-width: 500px;
        }
        QWizard{
            color: black;
            background-color: white;
            font-family: "Arial", Sans-serif;
        }
        QWizardPage{
            background-color: white;
            font-family: "Arial", Sans-serif;
        }
        QWidget{
            font-family: "Arial", Sans-serif;            
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
            font-size: 12px;

            background-color: white;
            color: Black;

            min-height: 40px;
            margin: 5px;
        }
        QCheckBox{
            font-size: 22px;
        }
        QTableWidget, QToolButton#outDirBtn{
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
            font-size: 24px;
            color: black;
            font-family: "Arial", Sans-serif;
        }
        QLabel#introQuestion{
            font-size: 24px; 
            color: #666;
        }
        QLabel#instructionLabel{
            font-size: 18px;
            color: #2196f3;
        }
        QLabel#detailsLink{
            border-bottom: 2px solid #ccc;
        }
        QLabel#titleLabel{
            font-size : 54px;
            font-weight: 600;
            height: 100px;
            width: 100px;
            color: Black;
            qproperty-alignment: AlignCenter;

        }
        QLabel#instructionInput, QLabel#instructionMCMC, QLabel#instructionInference, QLabel#instructionPrior, QLabel#instructionLabelStarting{
            font-size : 18px;
            font-weight: 400;
            color: Black;
            padding: 10px;
        }
        QLabel#questionLabel{            
            font-size: 36px;
            qproperty-alignment: AlignCenter;
            color: Black;

            width: 100%;
            font-weight: 600;
            font-family: "Arial", Sans-serif;
        }
        QLabel{
            font-size: 18px;
            padding: 20px;
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
            font-size: 12px;
            text-align: center;
        }
        QPushButton#inputBtn, QPushButton#outputBtn{
            padding: 20px 10px;
            font-size: 24px;
            border-color: transparent;
            min-height: 50px;
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
            font-size: 28px;
            color: Black;

            max-width: 150px;
            max-height: 100px;
            margin-bottom: 50px;

            border: 3px solid; 
            border-color: #77ACE1;
            border-radius: 6px; 
        }
        QPushButton{
            font-size: 24px;
            color: Black;

            margin-bottom: 35px;
            min-height: 50px;

            padding: 5px 20px;        
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }
        QMessageBox{           
            background-color: white;
            color: Black; 

            font-family: Arial, Helvetica, sans-serif;
            font-size: 36px;
        }
        QRadioButton{
            font-size: 24px;
            
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

# css styling


def dark_style():
    return """
        QDialog{
            background-color: #323642;

            min-width: 1300px;
            min-height: 800px;
        }
        QMainWindow{
            background-color: #323642;
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
            min-height: 50px;
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
        QLabel#detailsLink{
            border-bottom: 2px solid #ccc;
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
            
            min-height: 50px;
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
