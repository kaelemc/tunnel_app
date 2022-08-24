import sys
import fines as f
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# MAIN WINDOW START
class MyApp(QMainWindow):

    # window setup
    def __init__(self):
        super().__init__()
        # window variables
        self.width = 600
        self.height = 250
        self.setWindowTitle("Waterview Speeding System")
        self.setFixedSize(self.width, self.height)
        self._initToolbar()
        self._initLayout()

        # class scope variables for function params
        self.openPath = ""
        self.fines = []
        self.errors = []

        # init settings window
        self.settings = SettingsWindow()
        self.finesWindow = TableWindow(["Plate", "Time In", "Time Out", "Duration", "Speed", "Fine"])
        self.errorsWindow = TableWindow(["Plate", "Time In", "Time Out", "Error/Warning"])

    
    
    def _initToolbar(self):
        menuBar = self.menuBar()

        ################
        # File menu
        ################
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        # actions
        # open file
        self.openAction = QAction("&Open", self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.triggered.connect(self.OpenFile) 
        # save fines
        self.saveFinesAction = QAction("&Save Fines As", self)
        self.saveFinesAction.setShortcut("Ctrl+S")
        self.saveFinesAction.triggered.connect(self.SaveFines)

        # save file
        self.saveErrAction = QAction("&Save Errors As", self)
        self.saveErrAction.setShortcut("Ctrl+Shift+S")
        self.saveErrAction.triggered.connect(self.SaveErrors)
        # put save file here

        # settings
        self.settingsAction = QAction("&Settings", self)
        self.settingsAction.triggered.connect(self.OpenSettings)

        # exit / close 
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(self.close)
        self.exitAction.setShortcut("Ctrl+W") # shortcut

        # add actions to the 'file' menu
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveFinesAction)
        fileMenu.addAction(self.saveErrAction)
        fileMenu.addAction(self.settingsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

    def _initLayout(self):
        self.layout = QGridLayout()
        
        self.genFinesBtn = QPushButton("Generate Data")
        self.genFinesBtn.clicked.connect(self.GenData)
        self.viewFinesBtn = QPushButton("View Fines")
        self.viewFinesBtn.clicked.connect(self.ShowFines)
        self.viewErrsBtn = QPushButton("View Warnings")
        self.viewErrsBtn.clicked.connect(self.ShowWarn)

        # add stuff to the layout
        self.layout.addWidget(self.genFinesBtn, 1, 0, 1, 2)
        self.layout.addWidget(self.viewFinesBtn, 2, 0)
        self.layout.addWidget(self.viewErrsBtn, 2, 1)

        # set main window layout
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(self.layout)

    def OpenFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "","Comma Separated Values (*.csv);;Text Files (*.txt)")
        self.openPath = fileName

    def SaveFines(self):
        fileName = self.SaveFile(self.fines, "Comma Separated Values (*.csv);;Text Files (*.txt)")
        try:
            if fileName.endswith("txt"):
                f.write_txt(fileName, self.fines)
            elif fileName.endswith("csv"):
                f.write_csv(fileName, self.fines)
            else:
                return None
            self.ShowMsgDialog(QMessageBox.Information, "Success!", "Data saved successfully at {}".format(fileName))
        except Exception as exc:
            self.ShowMsgDialog(QMessageBox.Critical, "Error!", "File couldn't be saved"+str(exc))
            pass
    
    def SaveErrors(self):
        fileName = self.SaveFile(self.errors, "Comma Separated Values (*.csv)")
        try:
            if fileName.endswith("csv"):
                f.WriteErrors(fileName, self.errors)
            else: 
                return ""
            self.ShowMsgDialog(QMessageBox.Information, "Success!", "Data saved successfully at {}".format(fileName))
        except Exception as exc:
            self.ShowMsgDialog(QMessageBox.Critical, "Error!", "File couldn't be saved"+str(exc))
            pass
    
    def SaveFile(self, data, saveArgs):
        if not data:
            clicked = self.ShowMsgDialog(QMessageBox.Warning, "Warning!", "It seems there is no data to write, Continue?")
            if clicked:
                pass
            else:
                return ""
        fileName, _ = QFileDialog.getSaveFileName(self, "Open File", "", saveArgs)
        return fileName
    
    def GenData(self):
        if len(self.openPath) < 1:
            self.ShowMsgDialog(QMessageBox.Critical, "Error!", "Please select a file first")
            return True
        generate = f.generate(self.openPath, speedLimit, exitThreshold, entryDist+tLen+exitDist)
        if generate is None:
            self.fines = f.buffer
            self.errors = f.errors
            self.ShowMsgDialog(QMessageBox.Information, "Success!", "Data generated successfully with {} warnings!".format(len(self.errors)))
        else:
            self.ShowMsgDialog(QMessageBox.Critical, "Error!", str(generate))
            self.fines = []
            self.errors = []
    
    def OpenSettings(self):
        self.settings.show()
    
    def ShowFines(self):
        self.finesWindow.updateData(self.fines)
        self.finesWindow.show()

    def ShowWarn(self):
        self.errorsWindow.updateData(self.errors)
        self.errorsWindow.show()
    
    def ShowMsgDialog(self, BoxQIcon, title, text):
        self.mBox = QMessageBox()
        self.mBox.setIcon(BoxQIcon)
        self.mBox.setWindowTitle(title)
        self.mBox.setText(text)
        self.mBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        retVal = self.mBox.exec()
        if retVal == QMessageBox.Ok:
            return True
        else:
            return False

# MAIN WINDOW END



# SETTINGS WINDOW START

# defaults
speedLimit = 80
exitThreshold = 4
entryDist = 185
tLen = 2400
exitDist = 105

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 320
        self.height = 240
        self.setWindowTitle("Settings")
        self.setFixedSize(self.width, self.height)
        self._initLayout()
    
    def _initLayout(self):
        self.mainLayout = QGridLayout()

        # SPEED LIMIT ###################################################
        self.speedLabel = QLabel("Speed Limit (km/h):")

        self.speedSBox = QSpinBox()
        self.speedSBox.setMinimum(0)
        self.speedSBox.setMaximum(400)
        self.speedSBox.setValue(speedLimit)

        self.mainLayout.addWidget(self.speedLabel, 1, 0)
        self.mainLayout.addWidget(self.speedSBox, 1, 1)
        ##################################################################

        # EXIT THRESHOLD #################################################
        self.exitLabel = QLabel("Exit Time Threshold (mins):")

        self.exitSBox = QSpinBox()
        self.exitSBox.setMinimum(0)
        self.exitSBox.setMaximum(60)
        self.exitSBox.setValue(exitThreshold)

        self.mainLayout.addWidget(self.exitLabel, 2 , 0)
        self.mainLayout.addWidget(self.exitSBox, 2, 1)
        ##################################################################

        # CAMERA DISTANCE ################################################
        self.tLengthLabel = QLabel("Tunnel Length (meters):")
        self.entryDistLabel = QLabel("Entrance Camera Distance (meters):")
        self.existDistLabel = QLabel("Exit Camera Distance (meters):")

        self.tLengthSBox = QSpinBox()
        self.tLengthSBox.setMaximum(10000)
        self.tLengthSBox.setValue(tLen)
        
        self.entryDistSBox = QSpinBox()
        self.entryDistSBox.setMaximum(600)
        self.entryDistSBox.setValue(entryDist)

        self.exitDistSBox = QSpinBox()
        self.exitDistSBox.setMaximum(600)
        self.exitDistSBox.setValue(exitDist)

        # add to the grid
        self.mainLayout.addWidget(self.tLengthLabel, 3, 0)
        self.mainLayout.addWidget(self.tLengthSBox, 3, 1)

        self.mainLayout.addWidget(self.entryDistLabel, 4, 0)
        self.mainLayout.addWidget(self.entryDistSBox, 4, 1)

        self.mainLayout.addWidget(self.existDistLabel, 5, 0)
        self.mainLayout.addWidget(self.exitDistSBox, 5, 1)
        ##################################################################

        self.saveBtn = QPushButton("Save")
        self.saveBtn.setToolTip("Save changes and close settings")
        self.saveBtn.clicked.connect(self.AcceptBtnEventHandler)

        self.mainLayout.addWidget(self.saveBtn, 6, 0, 1, 2)
        # set main layout
        self.setLayout(self.mainLayout)
    
    # if save is pressed then update the values
    def AcceptBtnEventHandler(self):
        # LEGB rules
        global speedLimit
        global exitThreshold
        global entryDist
        global tLen
        global exitDist

        speedLimit = self.speedSBox.value()
        exitThreshold = self.exitSBox.value()
        entryDist = self.entryDistSBox.value() 
        tLen = self.tLengthSBox.value()
        exitDist = self.exitDistSBox.value()
        self.close()

# SETTINGS WINDOW END

# TABLE VIEW START
class TableWindow(QWidget):
    def __init__(self, header):
        super().__init__()
        # params
        self.x_coord = 0
        self.y_coord = 0
        self.width = 640
        self.height = 480
        self.setWindowTitle("Waterview Speeding System")
        self.setGeometry(self.x_coord, self.y_coord, self.width, self.height)

        # table variables
        self.data = []
        self.header = header
        self.colCount = len(header)

        # table function
        self._initTable()
    
    def _initTable(self):
        # create the table and layout
        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setRowCount(0)
        self.table.setColumnCount(self.colCount)
        self.table.resizeColumnsToContents()

        # assign headers
        self.table.setHorizontalHeaderLabels(self.header)
        self.header = self.table.horizontalHeader()
        self.header.setSectionResizeMode(QHeaderView.ResizeToContents)   
        # iterate and set each header to uniform stretch    
        for i in range(self.colCount):
            self.header.setSectionResizeMode(i, QHeaderView.Stretch)
    
        # add to layout
        self.layout.addWidget(self.table)
        self.layout.setStretch(1, 1)
        self.setLayout(self.layout)
        

    def updateData(self, data):
        self.table.clearContents()
        self.table.setRowCount(0)
        self.data = data
        for i, row in enumerate(self.data):
            self.table.insertRow(i)
            for x, col in enumerate(row):
                self.table.setItem(i, x, QTableWidgetItem(str(col)))
        self.table.resizeColumnsToContents()

# TABLE VIEW END
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # create an object of class myApp
    appWindow = MyApp()
    # show the window
    MyApp.show(appWindow)
    sys.exit(app.exec_()) 