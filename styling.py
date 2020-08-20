
# css styling
def style():
    return """
        QMainWindow{
            background-color: white;
            font-family:  "Arial", "Libre Franklin SemiBold", "Arial", Sans-serif;
            padding: 30px 50px 30px 30px;
        }
        QDialog{
            background-color: white;
        }
        QDialog#aboutMessage{
            min-width: 500px;
            min-height: 500px;
            width: 100%;
            height: 100%;
            font-size: 38px;
        }
        QDialog#successMessage{
            min-height: 500px;
            min-width: 500px;
        }
        QWizard{
            color: black;
            background-color: white;
            font-family:  "Arial", "Libre Franklin SemiBold", "Arial", Sans-serif;
        }
        QWizardPage{
            background-color: white;
            font-family:  "Arial", "Libre Franklin SemiBold", "Arial", Sans-serif;
        }
        QWidget{
            font-family:  "Arial", "Libre Franklin SemiBold", "Arial", Sans-serif;            
        }
        QTableWidget{
            min-width: 1000px;
            min-height: 1200px;
        }
        QTabWidget::pane { 
            border: 0; 
        }
        QTabBar::tab{
            font-size: 22px;
            padding: 10px 0;  
            width: 300px; 
            border-bottom: 2px solid;
        }
        QTabWidget QTabBar QToolTip{ 
            padding: 20px;
        }    
        QTabBar::tab:selected{
            background-color: #aaeeff; 
            color: white;
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
            font-size: 26px;
        }
        QLabel{
            font-size: 26px;
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
            font-size: 26px;
            color: black;
            font-family:  "Arial", "Libre Franklin SemiBold", "Arial", Sans-serif;
        }
        QLabel#introQuestion{
            margin-top: 50px;
            font-size: 35px; 
            color: #666;
        }
        QLabel#instructionLabel{
            font-size: 34px;
            color: #2196f3;
        }
        QLabel#detailsLink{
            padding-top: 35px;
            border-bottom: 2px solid;
        }
        QLabel#titleLabel{
            font-size : 50px;
            font-weight: 800;
            border-right: 2px solid #ccc;
            border-bottom: 2px solid;
            color: Black;
            qproperty-alignment: AlignRight;
        }
        QLabel#instructionInput, QLabel#instructionMCMC, QLabel#instructionInference, QLabel#instructionPrior, QLabel#instructionLabelStarting{
            font-size : 20px;
            font-weight: 400;
            color: Black;
        }
        QLabel#questionLabel{            
            font-size: 52px;
            qproperty-alignment: AlignCenter;
            color: Black;

            width: 100%;
            font-weight: 600;
            font-family: "Arial", "Libre Franklin SemiBold", "Arial", Sans-serif;
        }
        QPushButton{
            font-size: 26px;
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
            font-size: 23px;
            padding: 5px;
            text-align: center;
            min-width: 200px;
        }
        QPushButton#inputBtn, QPushButton#outputBtn{
            width: 640px;
            padding: 50px 10px;
            font-size: 32px;
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
            border: none;
        }
        QPushButton#questionButton{
            font-size: 23px;
            color: Black;
            
            height: 25px;
            width: 25px;
            margin: 0;

            border: 3px solid #77ACE1;
            border-radius: 12.5px;
        }
        QPushButton#cancel, QPushButton#set{
            font-size: 19px;
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
            font-size: 35px;
        }
        QRadioButton{
            font-size: 29px;
            
            padding: 20px;
            width: 900px;
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }
        QToolButton#fileSelctionBtn, QPushButton#launchBtn{
            font-size: 19px;
            color: Black;

            width: 1200px; 
            height: 75px;
                        
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }

        """
