import sys

import qtawesome as qta

from PyQt5.QtGui import QIcon, QColor, QRegExpValidator
from PyQt5.QtCore import Qt, QSize, QTimer, QRegExp, pyqtSlot, QDate
from PyQt5.QtWidgets import *

import parsing, adding, languageDict
import startUp as StartUpPy
import autoUpdate as AutoUpdatePy
import re

def ReadSettings():

    with open('.\Data\Settings.txt', mode='r') as save_file:
        reader = save_file.read()
        for line in reader.split('\n'):
            if line.split(' ')[0] == 'Position':
                gadjetPosition = int(line.split(' ')[1])
            if line.split(' ')[0] == 'Language':
                gadjetLanguage = int(line.split(' ')[1])
            if line.split(' ')[0] == 'Path':
                fileName = line.split(' ')[1]
            if line.split(' ')[0] == 'Freq':
                updateTime = int(line.split(' ')[1])
            if line.split(' ')[0] == 'StartUp':
                startUp = int(line.split(' ')[1])
            if line.split(' ')[0] == 'AutoUpdate':
                autoUpdate = int(line.split(' ')[1])

    return gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate

def SaveSettings(gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate):
    save_text = f"Position {gadjetPosition}\nLanguage {gadjetLanguage}\nPath {fileName}\nFreq {updateTime}\nStartUp {startUp}\nAutoUpdate {autoUpdate}\n"
    with open('.\Data\Settings.txt', mode='w') as save_file:
        writer = save_file.write(save_text)

#GlobalVariable
with open('.\Data\Version.txt', mode='r') as file:
    lines = file.readlines()
    appName = lines[0].split(' ')[0]

gadjetPosition = None
gadjetLanguage = None
fileName = None
updateTime = None
startUp = None
autoUpdate = None

gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate = ReadSettings()
if gadjetPosition == None or gadjetLanguage == None or fileName == None or updateTime == None or startUp == None or autoUpdate == None:
    fileName = '.\Data\Dates.csv'
    updateTime = 7200000
    gadjetLanguage = 0
    gadjetPosition = 3
    startUp = 0
    autoUpdate = 0


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        self.activateWindowEvent = None

        global gadjetLanguage

        self.menu = QMenu(parent)
        self.showAction = QAction(languageDict.LangDict['TrayShow'][gadjetLanguage], parent, triggered=self._show)
        self.hideAction = QAction(languageDict.LangDict['TrayHide'][gadjetLanguage], parent, triggered=self._hide)
        self.exitAction = QAction(languageDict.LangDict['TrayClose'][gadjetLanguage], parent, triggered=self._exit)
        self.menu.addAction(self.showAction)
        self.menu.addAction(self.hideAction)
        self.menu.addAction(self.exitAction)
        self.setContextMenu(self.menu)

        # Перехватываем событие двойного щелчка по иконке в трее
        self.activated.connect(self.onActivated)

    def onActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            # Вызываем пользовательскую функцию при двойном щелчке по иконке в трее
            if self.activateWindowEvent:
                self.activateWindowEvent()

    def _show(self):
        w.show()

    def _hide(self):
        w.hide()

    def _exit(self):
        app.quit()

class PreviewWindow(QWidget):
    windowWidth = 380
    windowHeight = 320

    def __init__(self, parent=None):
        super(PreviewWindow, self).__init__(parent)

        global gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate, appName

        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnBottomHint     # <<<=====<
            #| Qt.CustomizeWindowHint         # Отключает подсказки заголовка окна по умолчанию.
            #| Qt.WindowTitleHint             # Придает окну строку заголовка.
            #| Qt.MSWindowsFixedSizeDialogHint
            | Qt.FramelessWindowHint
            | Qt.Tool
            | Qt.WA_AlwaysShowToolTips
        )

        self.x, self.y = self.PosCount(self.windowWidth, self.windowHeight)

        self.setWindowTitle(appName)
        self.setGeometry(self.x, self.y, 0, 0)
        self.setFixedSize(self.windowWidth, self.windowHeight)


        self.tray_icon = SystemTrayIcon(QIcon('.\Data\icon.png'), self)
        self.tray_icon.setToolTip(appName)
        self.tray_icon.activateWindowEvent = self.toggle_window
        self.tray_icon.show()


        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(7)

        self.table.setHorizontalHeaderLabels([languageDict.LangDict['NameCol'][gadjetLanguage], languageDict.LangDict['DateCol'][gadjetLanguage], languageDict.LangDict['AgeCol'][gadjetLanguage], languageDict.LangDict['DaysCol'][gadjetLanguage]])
        self.table.setVerticalHeaderLabels(["", "", "", "", "", "", ""])

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeaderItem(0).setSizeHint(QSize(135,23))
        self.table.horizontalHeaderItem(1).setSizeHint(QSize(80, 23))
        self.table.horizontalHeaderItem(2).setSizeHint(QSize(60, 23))
        self.table.horizontalHeaderItem(3).setSizeHint(QSize(65, 23))
        
        self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
        self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        self.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
        self.table.horizontalHeaderItem(3).setTextAlignment(Qt.AlignHCenter)

        self.data_input()

        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)

        layout = QVBoxLayout()
        layout.addWidget(IconLabel("fa.birthday-cake", appName))
        layout.addWidget(self.table)
        layout.addWidget(ButtonButton())
        self.setLayout(layout)

        self.auto_update()

    def PosCount(self, Width, Height):

        global gadjetPosition
        # X
        if gadjetPosition == 1 or gadjetPosition == 4 or gadjetPosition == 7:
            x = 10
        elif gadjetPosition == 2 or gadjetPosition == 5 or gadjetPosition == 8:
            x = int((screenWidth / 2) - (Width / 2))
        else:
            x = screenWidth - Width - 10

        # Y
        if gadjetPosition == 1 or gadjetPosition == 2 or gadjetPosition == 3:
            y = 10
        elif gadjetPosition == 4 or gadjetPosition == 5 or gadjetPosition == 6:
            y = int((screenHeight / 2) - (Height / 2))
        else:
            y = screenHeight - Height - 60

        return x, y

    def auto_update(self):
        global updateTime
        self.timer = QTimer()
        self.timer.timeout.connect(self.funktions_for_update)
        self.timer.start(updateTime)

    def funktions_for_update(self):
        self.check_update()
        self.data_input()

    def check_update(self):
        global autoUpdate, gadjetLanguage
        if autoUpdate == 1:
            updateBool = AutoUpdatePy.checkNewVer()
            if updateBool:
                link = 'https://github.com/VaStan96/BirthDays_Gadget.git'
                formattedText = f'<p>{languageDict.LangDict["NewVerText"][gadjetLanguage]} <a href="{link}">{link}</a></p>'

                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText(formattedText)
                msg.setWindowTitle(languageDict.LangDict['NewVerTitle'][gadjetLanguage])
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setFixedWidth(100)
                msg.setGeometry(int(screenWidth/2)-175, int(screenHeight/2)-75, 0, 0)
                msg.exec()


    def data_input(self):
        global fileName, gadjetLanguage
        items = parsing.sort_csv(fileName, gadjetLanguage)
        for x in range(len(items)):
            if items[x][3] < 0:
                for y in range(4):
                    item = QTableWidgetItem(str(items[x][y]))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QColor(255, 209, 209))
                    self.table.setItem(x, y, item)
            elif items[x][3] == 0:
                for y in range(4):
                    item = QTableWidgetItem(str(items[x][y]))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QColor(209, 255, 231))
                    self.table.setItem(x, y, item)
            else:
                for y in range(4):
                    item = QTableWidgetItem(str(items[x][y]))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QColor(209, 240, 255))
                    self.table.setItem(x, y, item)

    def toggle_window(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def closeEvent(self, event):
        self.destroy()

    def restart(self):
        self.destroy()
        self.tray_icon.hide()
        self.__init__()
        self.show()

class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()

        global gadjetPosition, gadjetLanguage, fileName, updateTime, appName

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 300)

        infoFile = languageDict.LangDict['InfoPath'][gadjetLanguage]

        with open(infoFile, mode='r', encoding='utf-8') as info_file:
            self.text = info_file.readlines()

        self.text = ''.join(self.text)
        self.textEdit = QTextEdit(self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setPlainText(self.text)
        self.textEdit.setAlignment(Qt.AlignLeft)
        self.textEdit.setStyleSheet("font: 14px")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.textEdit)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.destroy()

class SettingWindow(QWidget):
    def __init__(self):
        super().__init__()

        global gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate, appName

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 400)

        # self.dict_direct = {'1 Hour': 10000, '2 Hour': 7200000, '6 Hour': 21600000, '12 Hour': 43200000, '1 Day': 86400000}
        # self.dict_reverse = {10000: '1 Hour', 7200000: '2 Hour', 21600000: '6 Hour', 43200000: '12 Hour', 86400000: '1 Day'}
        self.dict_reverse = dict(zip(languageDict.LangDict['UpdateTimeNum'][0], languageDict.LangDict['UpdateTimeWord'][gadjetLanguage]))
        self.dict_direct = dict(zip(languageDict.LangDict['UpdateTimeWord'][gadjetLanguage], languageDict.LangDict['UpdateTimeNum'][0]))

        self.FlagChangedStartUpBox = False

        self.text = languageDict.LangDict['SetLabel'][gadjetLanguage]
        self.firstPunkt = languageDict.LangDict['PathLabel'][gadjetLanguage]
        self.secondPunkt = languageDict.LangDict['TimeLabel'][gadjetLanguage]

        self.WinLabel = QLabel(self)
        self.WinLabel.setText(self.text)
        self.WinLabel.setAlignment(Qt.AlignLeft)
        self.WinLabel.setStyleSheet("font: 24px")

        self.position = QWidget()
        self.layoutP = QGridLayout(self.position)
        self.layoutP.setContentsMargins(0, 0, 0, 0)
        self.layoutP.setVerticalSpacing(5)

        self.PosLabel = QLabel(self)
        self.PosLabel.setText(languageDict.LangDict['PosLabel'][gadjetLanguage])
        self.PosLabel.setAlignment(Qt.AlignLeft)
        self.PosLabel.setStyleSheet("font: 14px")
        self.layoutP.addWidget(self.PosLabel, 0, 0, 1, 3)


        self.radioButtonP1 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP1, 1, 0)
        self.radioButtonP2 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP2, 1, 1)
        self.radioButtonP3 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP3, 1, 2)
        self.radioButtonP4 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP4, 2, 0)
        self.radioButtonP5 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP5, 2, 1)
        self.radioButtonP6 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP6, 2, 2)
        self.radioButtonP7 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP7, 3, 0)
        self.radioButtonP8 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP8, 3, 1)
        self.radioButtonP9 = QRadioButton()
        self.layoutP.addWidget(self.radioButtonP9, 3, 2)

        self.groupPos = QButtonGroup()
        self.groupPos.addButton(self.radioButtonP1, 1)
        self.groupPos.addButton(self.radioButtonP2, 2)
        self.groupPos.addButton(self.radioButtonP3, 3)
        self.groupPos.addButton(self.radioButtonP4, 4)
        self.groupPos.addButton(self.radioButtonP5, 5)
        self.groupPos.addButton(self.radioButtonP6, 6)
        self.groupPos.addButton(self.radioButtonP7, 7)
        self.groupPos.addButton(self.radioButtonP8, 8)
        self.groupPos.addButton(self.radioButtonP9, 9)

        self.setRadioButtonPosition()


        self.language = QWidget()
        self.layoutL = QGridLayout(self.language)
        self.layoutL.setContentsMargins(0, 0, 0, 0)
        self.layoutL.setVerticalSpacing(5)

        self.LanLabel = QLabel(self)
        self.LanLabel.setText(languageDict.LangDict['LangLabel'][gadjetLanguage])
        self.LanLabel.setAlignment(Qt.AlignLeft)
        self.LanLabel.setStyleSheet("font: 14px")
        self.layoutL.addWidget(self.LanLabel, 0, 0)

        self.radioButtonEng = QRadioButton("English")
        self.layoutL.addWidget(self.radioButtonEng, 1, 0)
        self.radioButtonDeu = QRadioButton("Deutsch")
        self.layoutL.addWidget(self.radioButtonDeu, 2, 0)
        self.radioButtonRus = QRadioButton("Русский")
        self.layoutL.addWidget(self.radioButtonRus, 3, 0)

        self.setRadioButtonLanguage()

        self.PosLang = QWidget()
        self.layoutPL = QHBoxLayout(self.PosLang)
        self.layoutPL.setContentsMargins(0, 0, 0, 0)
        self.layoutPL.addWidget(self.position)
        self.layoutPL.addSpacing(30)
        self.layoutPL.addWidget(self.language)

        self.PosLangStackedWidget = QStackedWidget(self)
        self.PosLangStackedWidget.addWidget(self.PosLang)


        self.PathLabel = QLabel(self)
        self.PathLabel.setText(self.firstPunkt)
        self.PathLabel.setAlignment(Qt.AlignLeft)
        self.PathLabel.setStyleSheet("font: 14px")

        self.newFileButton = QPushButton('...')
        self.newFileButton.clicked.connect(self.openFile)
        self.newFileButton.setFixedSize(QSize(30, 25))
        self.newFileButton.setToolTip(languageDict.LangDict['SelectButTip'][gadjetLanguage])

        self.InputString = QLineEdit()
        self.InputString.setText(fileName)
        self.InputString.setFixedSize(QSize(400,25))
        self.InputString.setContentsMargins(0, 0, 0, 0)
        self.InputString.deselect()

        self.input = QWidget()
        self.layoutH = QHBoxLayout(self.input)
        self.layoutH.setContentsMargins(0, 0, 0, 0)
        self.layoutH.setAlignment(Qt.AlignLeft)
        self.layoutH.addWidget(self.InputString)
        self.layoutH.addWidget(self.newFileButton)

        self.pathStackedWidget = QStackedWidget(self)
        self.pathStackedWidget.addWidget(self.input)


        self.UpdateTimeLabel = QLabel(self)
        self.UpdateTimeLabel.setText(self.secondPunkt)
        self.UpdateTimeLabel.setAlignment(Qt.AlignLeft)
        self.UpdateTimeLabel.setStyleSheet("font: 14px")

        self.UpdateTime = QComboBox()
        self.UpdateTime.setFixedSize(QSize(110, 25))
        self.UpdateTime.addItems(languageDict.LangDict['UpdateTimeWord'][gadjetLanguage])
        temp = self.dict_reverse.get(updateTime)
        self.UpdateTime.setCurrentText(temp)

        self.FreqUpdate = QWidget()
        self.layoutFreq = QVBoxLayout(self.FreqUpdate)
        self.layoutFreq.setContentsMargins(0,0,0,0)
        self.layoutFreq.setAlignment(Qt.AlignLeft)
        self.layoutFreq.addWidget(self.UpdateTimeLabel)
        self.layoutFreq.addWidget(self.UpdateTime)

        self.FlagChangedStartUpBox = False
        self.StartUpBox = QCheckBox(languageDict.LangDict['StartUpLabel'][gadjetLanguage])
        self.StartUpBox.setStyleSheet("font: 14px")
        if startUp == 0:
            self.StartUpBox.setChecked(False)
        else:
            self.StartUpBox.setChecked(True)
        self.StartUpBox.stateChanged.connect(lambda: setattr(self, 'FlagChangedStartUpBox', True))

        self.AutoUpdateBox = QCheckBox(languageDict.LangDict['AutoUpdateLabel'][gadjetLanguage])
        self.AutoUpdateBox.setStyleSheet("font: 14px")
        if autoUpdate == 0:
            self.AutoUpdateBox.setChecked(False)
        else:
            self.AutoUpdateBox.setChecked(True)

        self.CheckBoxs = QWidget()
        self.layoutBoxs = QVBoxLayout(self.CheckBoxs)
        self.layoutBoxs.setContentsMargins(0,0,0,0)
        self.layoutBoxs.setAlignment(Qt.AlignLeft)
        self.layoutBoxs.addWidget(self.StartUpBox)
        self.layoutBoxs.addSpacing(10)
        self.layoutBoxs.addWidget(self.AutoUpdateBox)

        self.UpdateAndBoxs = QWidget()
        self.layoutUpAndBoxs = QHBoxLayout(self.UpdateAndBoxs)
        self.layoutUpAndBoxs.setContentsMargins(0, 0, 0, 0)
        self.layoutUpAndBoxs.setAlignment(Qt.AlignLeft)
        self.layoutUpAndBoxs.addWidget(self.FreqUpdate)
        self.layoutUpAndBoxs.addSpacing(100)
        self.layoutUpAndBoxs.addWidget(self.CheckBoxs)

        self.UpdateAndBoxsStackedWidget = QStackedWidget(self)
        self.UpdateAndBoxsStackedWidget.addWidget(self.UpdateAndBoxs)


        self.SaveButton = QPushButton(languageDict.LangDict['SaveBut'][gadjetLanguage])
        self.SaveButton.clicked.connect(self.saveEvent)
        self.SaveButton.setFixedSize(QSize(160, 25))
        self.SaveButton.setToolTip(languageDict.LangDict['SaveTip'][gadjetLanguage])


        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 10)
        self.layout.addWidget(self.WinLabel)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.PosLangStackedWidget)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.PathLabel)
        self.layout.addWidget(self.pathStackedWidget)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.UpdateAndBoxsStackedWidget)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SaveButton)
        self.setLayout(self.layout)

    def setRadioButtonLanguage(self):
        global gadjetLanguage

        if gadjetLanguage == 0:
            self.radioButtonEng.setChecked(True)
        elif gadjetLanguage == 1:
            self.radioButtonDeu.setChecked(True)
        else:
            self.radioButtonRus.setChecked(True)

    def setRadioButtonPosition(self):
        global gadjetPosition

        dictPos = {1:self.radioButtonP1, 2:self.radioButtonP2, 3:self.radioButtonP3, 4:self.radioButtonP4, 5:self.radioButtonP5,
                   6:self.radioButtonP6, 7:self.radioButtonP7, 8:self.radioButtonP8, 9:self.radioButtonP9}
        dictPos[gadjetPosition].setChecked(True)

    def checkRadioButtonLanguage(self):
        if self.radioButtonEng.isChecked():
            return 0
        elif self.radioButtonDeu.isChecked():
            return 1
        elif self.radioButtonRus.isChecked():
            return 2

    def closeEvent(self, event):
        self.destroy()

    def saveEvent(self):
        global gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate

        fileName = self.InputString.text()
        updateTime = self.dict_direct.get(self.UpdateTime.currentText())
        gadjetLanguage = self.checkRadioButtonLanguage()
        gadjetPosition = self.groupPos.checkedId()
        startUp = int(self.StartUpBox.isChecked())
        autoUpdate = int(self.AutoUpdateBox.isChecked())

        SaveSettings(gadjetPosition, gadjetLanguage, fileName, updateTime, startUp, autoUpdate)
        if self.FlagChangedStartUpBox:
            if startUp == 1:
                StartUpPy.TurnOnStartUp()
            else:
                StartUpPy.TurnOffStartUp()

        w.restart()
        self.destroy()

    def openFile(self):
        FilePath = QFileDialog.getOpenFileName(self, 'Open File', './', "CSV (*.csv)")[0]
        self.InputString.setText(FilePath)

    # def selectStartUpBox(self):
    #     self.FlagChangedStartUpBox = True

class AddWindow(QWidget):
    def __init__(self):
        super().__init__()

        global gadjetPosition, gadjetLanguage, fileName, updateTime, appName

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 300)

        self.text = languageDict.LangDict['AddLabel'][gadjetLanguage]
        self.path = languageDict.LangDict['AddLabel2'][gadjetLanguage] + '\n' + fileName
        self.firstPunkt = languageDict.LangDict['AddNameLabel'][gadjetLanguage]
        self.secondPunkt = languageDict.LangDict['AddDateLabel'][gadjetLanguage]

        self.WinLabel = QLabel(self)
        self.WinLabel.setText(self.text)
        self.WinLabel.setAlignment(Qt.AlignLeft)
        self.WinLabel.setStyleSheet("font: 24px")

        self.PathLabel = QLabel(self)
        self.PathLabel.setText(self.path)
        self.PathLabel.setAlignment(Qt.AlignLeft)
        self.PathLabel.setStyleSheet("font-size: 12px; font-weight: bold")

        self.FirstPunktLabel = QLabel(self)
        self.FirstPunktLabel.setText(self.firstPunkt)
        self.FirstPunktLabel.setAlignment(Qt.AlignLeft)
        self.FirstPunktLabel.setStyleSheet("font: 12px")

        self.SecondPunktLabel = QLabel(self)
        self.SecondPunktLabel.setText(self.secondPunkt)
        self.SecondPunktLabel.setAlignment(Qt.AlignLeft)
        self.SecondPunktLabel.setStyleSheet("font: 12px")

        self.SaveButton = QPushButton(languageDict.LangDict['SaveBut'][gadjetLanguage])
        self.SaveButton.clicked.connect(self.saveEvent)
        self.SaveButton.setFixedSize(QSize(160, 25))
        self.SaveButton.setToolTip(languageDict.LangDict['SaveTip'][gadjetLanguage])


        self.InputName = QLineEdit()
        self.InputName.setPlaceholderText(languageDict.LangDict['AddNameTip'][gadjetLanguage])
        self.InputName.setFixedSize(QSize(400, 25))


        self.InputDate = QLineEdit()
        self.InputDate.setMaxLength(10)
        self.regexp = QRegExp("^(?:(?:31(\.)(?:0[13578]|1[02]))\1|(?:(?:29|30)(\.)(?:0[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)\d{2})$|^(?:29(\.)(?:02)\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0[1-9]|1\d|2[0-8])(\.)(?:(?:0[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)\d{2})$")
        self.Validator = QRegExpValidator(self.regexp, self.InputDate)
        self.InputDate.setPlaceholderText(languageDict.LangDict['AddDateTip'][gadjetLanguage])
        self.InputDate.setValidator(self.Validator)
        self.InputDate.setFixedSize(QSize(375, 25))
        self.InputDate.textEdited[str].connect(self.format_text)
        self.InputDate.setContentsMargins(0,0,0,0)

        self.CalendarButton = QPushButton('\u02C5')
        self.CalendarButton.clicked.connect(self.openCalendar)
        self.CalendarButton.setFixedSize(QSize(25, 25))
        self.CalendarButton.setToolTip(languageDict.LangDict['CalendarTip'][gadjetLanguage])
        self.CalendarButton.setContentsMargins(0,0,0,0)

        self.dates = QWidget()
        self.layoutH = QHBoxLayout(self.dates)
        self.layoutH.setContentsMargins(0, 0, 0, 0)
        self.layoutH.setAlignment(Qt.AlignLeft)
        self.layoutH.addWidget(self.InputDate)
        self.layoutH.addWidget(self.CalendarButton)

        self.dateStackedWidget = QStackedWidget(self)
        self.dateStackedWidget.addWidget(self.dates)


        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 10)
        self.layout.addWidget(self.WinLabel)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.PathLabel)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.FirstPunktLabel)
        self.layout.addWidget(self.InputName)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SecondPunktLabel)
        self.layout.addWidget(self.dateStackedWidget)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SaveButton)
        self.setLayout(self.layout)

    @pyqtSlot(str)
    def format_text(self):
        text = self.InputDate.text()
        if re.fullmatch('\d\d', text) or re.fullmatch('\d\d\.\d\d', text):
            self.InputDate.setText(text+'.')

    def closeEvent(self, event):
        self.destroy()

    def saveEvent(self):
        global fileName, gadjetLanguage
        dateText = self.InputDate.text()
        nameText = self.InputName.text()
        if len(dateText) == 10 and nameText != "":
            adding.add_csv(fileName, nameText, dateText)
            w.data_input()
            self.destroy()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(languageDict.LangDict['WarningText'][gadjetLanguage])
            msg.setWindowTitle(languageDict.LangDict['WarningTitle'][gadjetLanguage])
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def openCalendar(self):
        self.calendar = CalendarWindow(self.InputDate)
        self.calendar.show()

class CalendarWindow(QWidget):
    def __init__(self, widget):

        global appName

        super().__init__()
        self.widget = widget
        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(350, 250)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate(1900, 1, 1))
        self.calendar.setMaximumDate(QDate(3000, 12, 31))
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.clicked.connect(self.getDateCalendar)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 10)
        self.layout.addWidget(self.calendar)
        self.setLayout(self.layout)

    def getDateCalendar(self, date):
        day = str(date.day())
        if len(day) == 1:
            day = '0' + day
        month = str(date.month())
        if len(month) == 1:
            month = "0" + month
        year = str(date.year())
        text = f'{day}.{month}.{year}'
        self.widget.setText(text)
        self.destroy()

class ButtonButton(PreviewWindow):
    BigButSize = QSize(160, 25)
    SmallButSize = QSize(30, 25)
    HorizontalSpacingBig = 58
    HorizontalSpacingSmall = 2

    def __init__(self, final_stretch=True):
        super(QWidget, self).__init__()

        global gadjetPosition, gadjetLanguage, fileName, updateTime

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        closeButton = QPushButton(languageDict.LangDict['HideBut'][gadjetLanguage])
        closeButton.clicked.connect(self.closeImTray)
        closeButton.setFixedSize(self.BigButSize)
        closeButton.setToolTip(languageDict.LangDict['HideTip'][gadjetLanguage])


        addButton = QPushButton()
        addButton.clicked.connect(self.addDay)
        addButton.setFixedSize(self.SmallButSize)
        addButton.setIcon(QIcon('.\Data\\add.png'))
        addButton.setToolTip(languageDict.LangDict['AddTip'][gadjetLanguage])

        updateButton = QPushButton()
        updateButton.clicked.connect(self.Update)
        updateButton.setFixedSize(self.SmallButSize)
        updateButton.setIcon(QIcon('.\Data\up.png'))
        updateButton.setToolTip(languageDict.LangDict['RefreschTip'][gadjetLanguage])

        settingsButton = QPushButton()
        settingsButton.clicked.connect(self.setting)
        settingsButton.setFixedSize(self.SmallButSize)
        settingsButton.setIcon(QIcon('.\Data\setting.png'))
        settingsButton.setToolTip(languageDict.LangDict['SetTip'][gadjetLanguage])

        infoButton = QPushButton()
        infoButton.clicked.connect(self.info)
        infoButton.setFixedSize(self.SmallButSize)
        infoButton.setIcon(QIcon('.\Data\info.png'))
        infoButton.setToolTip(languageDict.LangDict['InfoTip'][gadjetLanguage])

        layout.addWidget(closeButton)
        layout.addSpacing(self.HorizontalSpacingBig)
        layout.addWidget(addButton)
        layout.addSpacing(self.HorizontalSpacingSmall)
        layout.addWidget(updateButton)
        layout.addSpacing(self.HorizontalSpacingSmall)
        layout.addWidget(infoButton)
        layout.addSpacing(self.HorizontalSpacingSmall)
        layout.addWidget(settingsButton)

        if final_stretch:
            layout.addStretch()

    def closeImTray(self):
        w.hide()

    def Update(self):
        w.data_input()

    def info(self):
        self.infoW = InfoWindow()
        self.infoW.show()

    def addDay(self):
        self.addW = AddWindow()
        self.addW.show()

    def setting(self):
        self.setW = SettingWindow()
        self.setW.show()

class IconLabel(QWidget):
    IconSize = QSize(16, 16)
    HorizontalSpacing = 50

    def __init__(self, qta_id, text, final_stretch=True):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        icon = QLabel()
        icon.setPixmap(qta.icon(qta_id).pixmap(self.IconSize))

        label = QLabel(self)
        label.setText(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font: 18px; font-weight: bold")

        layout.addWidget(icon)
        layout.addSpacing(self.HorizontalSpacing)
        layout.addWidget(label)

        if final_stretch:
            layout.addStretch()


if __name__ == '__main__':
    myappid = 'mycompany.myproduct.subproduct.version'  # переопределение приложения как самомтоятельное
    #QtWin.setCurrentProcessExplicitAppUserModelID(myappid) # для смены значка в панели задач

    app = QApplication(sys.argv)

    screenWidth = app.desktop().screenGeometry().width()
    screenHeight = app.desktop().screenGeometry().height()

    w = PreviewWindow()
    w.show()

    app.exec_()