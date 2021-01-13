def style():
    return """
        QMainWindow{
            background-color: white;
        }
        QDialog{
            background-color: white;
        }
        QDialog#successMessage{
            min-width: 200px;
            min-height: 200px;
        }
        QTableWidget{
            min-width: 1000px;
            min-height: 1200px;
        }
        QTabWidget::pane { 
            border: 0; 
        }
        QTabBar::tab{
            padding: 12px 0;  
            width: 330px; 
            border-bottom: 3px solid;
        }
        QTabWidget QTabBar QToolTip{ 
            padding: 22px;
        }    
        QTabBar::tab:selected{
            background-color: #aaeeff; 
            color: white;
        }
        QTableWidget, QToolButton#outDirBtn{
            color: Black;
            min-height: 22px;
            
            padding: 18px 0px;
        }
        QLabel#mainHeader{
            margin-bottom: 20px;
        }
        QLabel#version{
            margin-top: 20px;
        }
         QLabel#introQuestion{
            margin-top: 20px;
            font-size: 13pt; 
            color: #666;
        }
        QLabel#instructionLabel{
            font-size: 15pt;
            color: #2196f3;
        }
        QLabel#detailsLink{
            padding-top: 12px;
            border: 0px solid;
            border-bottom: 3px solid black;
        }
        QLabel#titleLabel{
            font-size : 26pt;
            font-weight: 800;
            color: black;
            border: 0px solid;
            border-bottom: 3px solid black;
            border-right: 3px solid #ccc;
            qproperty-alignment: AlignRight;
        }
        QLabel#questionLabel{            
            font-size: 24pt;
            qproperty-alignment: AlignCenter;
            color: Black;
            font-weight: 600;
        }
        QPushButton{
            color: Black;

            padding: 7px 21px;        
            border: 4px solid; 
            border-color: #2196f3;
            border-radius: 7px; 
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
        QPushButton#inputBtn, QPushButton#outputBtn{
            width: 615px;
            padding: 48px 10px;
            border-color: transparent;
        }
        QPushButton#inputBtn{
            background-color:#aaeeff;
        }
               QPushButton#outputBtn{
            background-color: #00ccff;
        }
        QPushButton#inputBtn:hover, QPushButton#outputBtn:hover{
            border: 6px solid black;
        }
        QPushButton#infoButton{
            border: none;
        }
        QRadioButton{
            padding: 20px;
            border: 3px solid; 
            border-color: #2196f3;
            border-radius: 6px; 
        }
        """
