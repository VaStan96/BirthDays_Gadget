import sys

import qtawesome as qta

from PyQt5.QtGui import QIcon, QColor, QRegExpValidator, QStandardItemModel, QStandardItem, QFont, QPainter, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QSize, QTimer, QRegExp, pyqtSlot, QDate, QFile, QTextStream, QSortFilterProxyModel, QRect, QLocale, QRegExp, QModelIndex, QVariant
from PyQt5.QtWidgets import *

import parsing, adding, languageDict
import startUp as StartUpPy
import autoUpdate as AutoUpdatePy
import CSVrewrite as CSV_ReWritePy
import re

#import Breeze_Style.breeze_resources

def setStyle():
    if gadgetStyle == 0:
        style = QFile('./Data/DarkStyle.css')
    else:
        style = QFile('./Data/LightStyle.css')

    if style.open(QFile.ReadOnly | QFile.Text):
        style_sheet = style.readAll().data().decode("utf-8")
        app.setStyleSheet(style_sheet)

def ReadSettings():

    with open('.\Data\Settings.txt', mode='r') as save_file:
        reader = save_file.read()
        for line in reader.split('\n'):
            if line.split(' ')[0] == 'Position':
                gadgetPosition = int(line.split(' ')[1])
            if line.split(' ')[0] == 'Language':
                gadgetLanguage = int(line.split(' ')[1])
            if line.split(' ')[0] == 'Path':
                fileName = line.split(' ')[1]
            if line.split(' ')[0] == 'Freq':
                updateTime = int(line.split(' ')[1])
            if line.split(' ')[0] == 'StartUp':
                startUp = int(line.split(' ')[1])
            if line.split(' ')[0] == 'AutoUpdate':
                autoUpdate = int(line.split(' ')[1])
            if line.split(' ')[0] == 'Style':
                gadgetStyle = int(line.split(' ')[1])
            if line.split(' ')[0] == 'Color':
                color = int(line.split(' ')[1])

    return gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, gadgetStyle, color

def SaveSettings(gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, gadgetStyle, color):
    save_text = f"Position {gadgetPosition}\nLanguage {gadgetLanguage}\nPath {fileName}\nFreq {updateTime}\nStartUp {startUp}\nAutoUpdate {autoUpdate}\nStyle {gadgetStyle}\nColor {color}\n"
    with open('.\Data\Settings.txt', mode='w') as save_file:
        writer = save_file.write(save_text)

#GlobalVariable
with open('.\Data\Version.txt', mode='r') as file:
    lines = file.readlines()
    appName = lines[0].split(' ')[0]

gadgetPosition = None
gadgetLanguage = None
fileName = None
updateTime = None
startUp = None
autoUpdate = None
gadgetStyle = None
color = None

gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, gadgetStyle, color  = ReadSettings()
if gadgetPosition == None or gadgetLanguage == None or fileName == None or updateTime == None or startUp == None or autoUpdate == None or gadgetStyle == None or color == None:
    fileName = '.\Data\Dates.csv'
    updateTime = 7200000
    gadgetLanguage = 0
    gadgetPosition = 3
    startUp = 0
    autoUpdate = 0
    gadgetStyle = 1
    color = 1

class DateDelegate(QStyledItemDelegate):
    def displayText(self, value, locale):
        if value.isValid():
            return value.toString("dd.MM.yyyy")
        else:
            return super().displayText(value, locale)

class MySwitch(QPushButton):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = '\u263C' if self.isChecked() else '\u263E' #26AA\263E\263D
        bg_color = Qt.white if self.isChecked() else Qt.black
        font_color = Qt.black if self.isChecked() else Qt.white
        bg_line_color = Qt.black if self.isChecked() else Qt.white

        radius = 10
        width = 30
        center = self.rect().center()

        bg = QPainter(self)
        bg.setRenderHint(QPainter.Antialiasing)
        bg.translate(center)
        bg.setBrush(bg_line_color)
        pen = QPen(bg_color)
        pen.setWidth(2)
        bg.setPen(pen)
        bg.drawRoundedRect(QRect(-width, -radius, 2 * width, 2 * radius), radius, radius)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(bg_color)
        pen = QPen(font_color)
        pen.setWidth(-2)
        painter.setPen(pen)
        sw_rect = QRect(-radius, -radius, width + radius, 2 * radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        self.activateWindowEvent = None

        global gadgetLanguage

        self.menu = QMenu(parent)
        self.showAction = QAction(languageDict.LangDict['TrayShow'][gadgetLanguage], parent, triggered=self._show)
        self.hideAction = QAction(languageDict.LangDict['TrayHide'][gadgetLanguage], parent, triggered=self._hide)
        self.exitAction = QAction(languageDict.LangDict['TrayClose'][gadgetLanguage], parent, triggered=self._exit)
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
    windowHeight = 324

    def __init__(self, parent=None):
        super(PreviewWindow, self).__init__(parent)

        global gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, appName, gadgetStyle, color

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


        self.tray_icon = SystemTrayIcon(QIcon('.\Data\icon.ico'), self)
        self.tray_icon.setToolTip(appName)
        self.tray_icon.activateWindowEvent = self.toggle_window
        self.tray_icon.show()


        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(7)

        self.table.setHorizontalHeaderLabels([languageDict.LangDict['NameCol'][gadgetLanguage], languageDict.LangDict['DateCol'][gadgetLanguage], languageDict.LangDict['AgeCol'][gadgetLanguage], languageDict.LangDict['DaysCol'][gadgetLanguage]])
        self.table.verticalHeader().hide()

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeaderItem(0).setSizeHint(QSize(146,23))
        self.table.horizontalHeaderItem(1).setSizeHint(QSize(80, 23))
        self.table.horizontalHeaderItem(2).setSizeHint(QSize(60, 23))
        self.table.horizontalHeaderItem(3).setSizeHint(QSize(70, 23))
        
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

        global gadgetPosition
        # X
        if gadgetPosition == 1 or gadgetPosition == 4 or gadgetPosition == 7:
            x = 10
        elif gadgetPosition == 2 or gadgetPosition == 5 or gadgetPosition == 8:
            x = int((screenWidth / 2) - (Width / 2))
        else:
            x = screenWidth - Width - 10

        # Y
        if gadgetPosition == 1 or gadgetPosition == 2 or gadgetPosition == 3:
            y = 10
        elif gadgetPosition == 4 or gadgetPosition == 5 or gadgetPosition == 6:
            y = int((screenHeight / 2) - (Height / 2))
        else:
            y = screenHeight - Height - 60

        return x, y

    def auto_update(self):
        global updateTime
        self.funktions_for_update()
        self.timer = QTimer()
        self.timer.timeout.connect(self.funktions_for_update)
        self.timer.start(updateTime)

    def funktions_for_update(self):
        self.check_update()
        self.data_input()

    def check_update(self):
        global autoUpdate, gadgetLanguage, gadgetStyle
        if autoUpdate == 1:
            updateBool = AutoUpdatePy.checkNewVer()
            if updateBool:
                with open('.\Data\Version.txt', mode='r') as file:
                    lines = file.readlines()
                    link = lines[2].split(' ')[1]

                #link = 'https://drive.google.com/drive/folders/1YX3FljwRpuXT2CxA9zknAVZIGS5lqigx?usp=sharing'
                if gadgetStyle == 0:
                    formattedText = f'<p>{languageDict.LangDict["NewVerText"][gadgetLanguage]} <a href="{link}" style="color:white">{languageDict.LangDict["Link"][gadgetLanguage]}</a></p>'
                else:
                    formattedText = f'<p>{languageDict.LangDict["NewVerText"][gadgetLanguage]} <a href="{link}" style="color:black">{languageDict.LangDict["Link"][gadgetLanguage]}</a></p>'

                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText(formattedText)
                msg.setWindowTitle(languageDict.LangDict['NewVerTitle'][gadgetLanguage])
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setFixedWidth(100)
                msg.setGeometry(int(screenWidth/2)-175, int(screenHeight/2)-75, 0, 0)
                msg.exec()

    def data_input(self):
        global fileName, gadgetLanguage, gadgetStyle, color
        items = parsing.sort_csv(fileName, gadgetLanguage)
        for x in range(len(items)):
            if items[x][3] < 0: #red
                for y in range(4):
                    item = QTableWidgetItem(str(items[x][y]))
                    item.setTextAlignment(Qt.AlignCenter)
                    if gadgetStyle == 1: #lightStyle
                        if color == 0:
                            item.setBackground(QColor('#FFD1D1'))
                        else:
                            item.setBackground(QColor('#D88686'))
                    else: #darkStyle
                        if color == 0:
                            item.setBackground(QColor('#31363b'))
                        else:
                            item.setBackground(QColor('#80404a'))
                    self.table.setItem(x, y, item)
            elif items[x][3] == 0: #green
                for y in range(4):
                    item = QTableWidgetItem(str(items[x][y]))
                    item.setTextAlignment(Qt.AlignCenter)
                    if gadgetStyle == 1: #lightStyle
                        if color == 0:
                            item.setBackground(QColor('#D1FFE7'))
                        else:
                            item.setBackground(QColor('#93E093'))
                    else: #darkStyle
                        if color == 0:
                            item.setBackground(QColor('#6F873B'))
                        else:
                            item.setBackground(QColor('#6F873b'))
                    self.table.setItem(x, y, item)
            else: #blue
                for y in range(4):
                    item = QTableWidgetItem(str(items[x][y]))
                    item.setTextAlignment(Qt.AlignCenter)
                    if gadgetStyle == 1: #lightStyle
                        if color == 0:
                            item.setBackground(QColor('#D1F0FF'))
                        else:
                            item.setBackground(QColor('#7ABDDD'))
                    else: #darkStyle
                        if color == 0:
                            item.setBackground(QColor('#626568'))
                        else:
                            item.setBackground(QColor('#406880'))
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

        global gadgetPosition, gadgetLanguage, fileName, updateTime, appName

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 300)

        infoFile = languageDict.LangDict['InfoPath'][gadgetLanguage]

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

class ListWindow(QWidget):
    def __init__(self):
        super().__init__()

        global gadgetPosition, gadgetLanguage, fileName, updateTime, appName

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 310)

        self.NoOrder = 0
        self.Ascending = 1
        self.Descending = 2

        items = parsing.pars_csv(fileName, gadgetLanguage)
        items = [[i[0], self.str_to_Qdate(i[1]), i[3], i[2]] for i in items]

        font = QFont('OpenSans', 9)

        # line edit for filtering
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText(languageDict.LangDict['ListSearchTip'][gadgetLanguage])
        self.lineEdit.textChanged.connect(self.filter_changed)

        #datamodel
        self.model = QStandardItemModel(len(items), 4)

        self.model.setHeaderData(0, Qt.Horizontal, languageDict.LangDict['NameCol'][gadgetLanguage])
        self.model.setHeaderData(0, Qt.Horizontal, font, Qt.FontRole)
        self.model.setHeaderData(1, Qt.Horizontal, languageDict.LangDict['DateCol'][gadgetLanguage])
        self.model.setHeaderData(1, Qt.Horizontal, font, Qt.FontRole)
        self.model.setHeaderData(2, Qt.Horizontal, languageDict.LangDict['AgeCol'][gadgetLanguage])
        self.model.setHeaderData(2, Qt.Horizontal, font, Qt.FontRole)
        self.model.setHeaderData(3, Qt.Horizontal, languageDict.LangDict['DaysCol'][gadgetLanguage])
        self.model.setHeaderData(3, Qt.Horizontal, font, Qt.FontRole)

        for row_index, row_data in enumerate(items):
            for col_index, col_data in enumerate(row_data):
                item = QStandardItem()
                if col_index == 0:  # если столбец содержит текст
                    item.setData(col_data, Qt.DisplayRole)  # устанавливаем данные текста
                elif col_index == 1:  # если столбец содержит дату
                    item.setData(col_data, Qt.DisplayRole)  # устанавливаем данные даты
                else:  # для остальных столбцов
                    item.setData(col_data, Qt.DisplayRole)
                self.model.setItem(row_index, col_index, item)

        # table view
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setSectionsClickable(True)
        self.table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.table.setToolTip(languageDict.LangDict['TableViewTip'][gadgetLanguage])

        # filter proxy model
        self.filterProxyModel = QSortFilterProxyModel()
        self.filterProxyModel.setSourceModel(self.model)
        self.filterProxyModel.setFilterKeyColumn(0)  # 1 column
        self.table.setModel(self.filterProxyModel)

        # save button
        self.saveButton = QPushButton(languageDict.LangDict['SaveBut'][gadgetLanguage])
        self.saveButton.clicked.connect(self.saveEvent)
        self.saveButton.setFixedSize(QSize(160, 25))
        self.saveButton.setToolTip(languageDict.LangDict['SaveTip'][gadgetLanguage])

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.saveButton)
        self.setLayout(self.layout)

        self.table.setColumnWidth(0, 170)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 77)
        self.table.setColumnWidth(3, 80)

    def str_to_Qdate(self, date):
        dd = int(date[:2])
        MM = int(date[3:5])
        yyyy = int(date[6:])
        return QDate(yyyy, MM, dd)

    def filter_changed(self, text):
        reg_exp = QRegExp(text, Qt.CaseInsensitive, QRegExp.RegExp)  # регулярное выражение для фильтрации
        self.filterProxyModel.setFilterRegExp(reg_exp)

    def sort_table(self, logical_index):
        current_order = self.table.horizontalHeader().sortIndicatorOrder()
        if current_order == self.Ascending:
            new_order = self.Descending
        else:
            new_order = self.Ascending
        self.filterProxyModel.sort(logical_index, new_order-1)

    def saveEvent(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(languageDict.LangDict['ListSaveText'][gadgetLanguage])
        msg.setWindowTitle(languageDict.LangDict['ListSaveTitle'][gadgetLanguage])
        msg.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Cancel)
        res = msg.exec_()

        if res == 1024:
            rewrite = CSV_ReWritePy.rewrite_csv(fileName, gadgetLanguage, self.model)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            if isinstance(rewrite, bool) and rewrite == True:
                msg.setText(languageDict.LangDict['RewriteTrue'][gadgetLanguage])
            elif isinstance(rewrite, bool) and rewrite == False:
                msg.setText(languageDict.LangDict['RewriteFalse'][gadgetLanguage])
            else:
                msg.setText(languageDict.LangDict['RewriteFalseInRow'][gadgetLanguage]+str(rewrite))
            msg.setWindowTitle(languageDict.LangDict['ListSaveTitle'][gadgetLanguage])
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            w.data_input()

    def closeEvent(self, event):
        self.destroy()

class SettingWindow(QWidget):
    def __init__(self):
        super().__init__()

        global gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, appName, gadgetStyle, color

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(550, 440)

        self.dict_reverse = dict(zip(languageDict.LangDict['UpdateTimeNum'][0], languageDict.LangDict['UpdateTimeWord'][gadgetLanguage]))
        self.dict_direct = dict(zip(languageDict.LangDict['UpdateTimeWord'][gadgetLanguage], languageDict.LangDict['UpdateTimeNum'][0]))

        self.FlagChangedStartUpBox = False

        self.text = languageDict.LangDict['SetLabel'][gadgetLanguage]
        self.firstPunkt = languageDict.LangDict['PathLabel'][gadgetLanguage]
        self.secondPunkt = languageDict.LangDict['TimeLabel'][gadgetLanguage]

        self.WinLabel = QLabel(self)
        self.WinLabel.setText(self.text)
        self.WinLabel.setAlignment(Qt.AlignLeft)
        self.WinLabel.setStyleSheet("font: 24px")

        self.position = QWidget()
        self.layoutP = QGridLayout(self.position)
        self.layoutP.setContentsMargins(0, 0, 0, 0)
        self.layoutP.setVerticalSpacing(5)

        self.PosLabel = QLabel(self)
        self.PosLabel.setText(languageDict.LangDict['PosLabel'][gadgetLanguage])
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
        self.LanLabel.setText(languageDict.LangDict['LangLabel'][gadgetLanguage])
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
        self.newFileButton.setToolTip(languageDict.LangDict['SelectButTip'][gadgetLanguage])

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
        self.UpdateTime.addItems(languageDict.LangDict['UpdateTimeWord'][gadgetLanguage])
        temp = self.dict_reverse.get(updateTime)
        self.UpdateTime.setCurrentText(temp)

        self.FreqUpdate = QWidget()
        self.layoutFreq = QVBoxLayout(self.FreqUpdate)
        self.layoutFreq.setContentsMargins(0,0,0,0)
        self.layoutFreq.setAlignment(Qt.AlignLeft)
        self.layoutFreq.addSpacing(10)
        self.layoutFreq.addWidget(self.UpdateTimeLabel)
        self.layoutFreq.addWidget(self.UpdateTime)
        self.layoutFreq.addStretch()


        self.SwitchLabel = QLabel(self)
        self.SwitchLabel.setText(languageDict.LangDict['SwitchTitle'][gadgetLanguage])
        self.SwitchLabel.setAlignment(Qt.AlignCenter)
        self.SwitchLabel.setStyleSheet("font: 14px")

        self.Switch = MySwitch()
        self.Switch.clicked.connect(self.switchStyle)
        self.Switch.setContentsMargins(0,0,0,0)
        self.Switch.setToolTip(languageDict.LangDict['Switch1Tip'][gadgetLanguage])

        self.LabelStyle1 = QLabel('Dark')
        self.LabelStyle1.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.LabelStyle1.setMargin(0)
        self.LabelStyle2 = QLabel('Light')
        self.LabelStyle2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.LabelStyle2.setMargin(0)

        self.StyleSwitch = QWidget()
        self.layoutSwitch = QHBoxLayout(self.StyleSwitch)
        self.layoutSwitch.addStretch()
        self.layoutSwitch.addWidget(self.LabelStyle1)
        self.layoutSwitch.addSpacing(0)
        self.layoutSwitch.addWidget(self.Switch)
        self.layoutSwitch.addSpacing(0)
        self.layoutSwitch.addWidget(self.LabelStyle2)
        self.layoutSwitch.addStretch()

        self.Switch2 = MySwitch()
        self.Switch2.clicked.connect(self.switchMono)
        self.Switch2.setContentsMargins(0, 0, 0, 0)
        self.Switch2.setToolTip(languageDict.LangDict['Switch2Tip'][gadgetLanguage])

        self.LabelStyle3 = QLabel('Mono')
        self.LabelStyle3.setAlignment(Qt.AlignBottom)
        self.LabelStyle3.setMargin(0)
        self.LabelStyle4 = QLabel('Color')
        self.LabelStyle4.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.LabelStyle4.setMargin(0)

        self.StyleSwitch2 = QWidget()
        self.layoutSwitch2 = QHBoxLayout(self.StyleSwitch2)
        self.layoutSwitch2.addStretch()
        self.layoutSwitch2.addWidget(self.LabelStyle3)
        self.layoutSwitch2.addSpacing(0)
        self.layoutSwitch2.addWidget(self.Switch2)
        self.layoutSwitch2.addSpacing(0)
        self.layoutSwitch2.addWidget(self.LabelStyle4)
        self.layoutSwitch2.addStretch()

        self.setSwitches()

        self.StyleSwitchBox = QWidget()
        self.layoutSwitchBox = QVBoxLayout(self.StyleSwitchBox)
        self.layoutSwitchBox.addWidget(self.SwitchLabel)
        self.layoutSwitchBox.addSpacing(0)
        self.layoutSwitchBox.addWidget(self.StyleSwitch)
        self.layoutSwitchBox.addSpacing(0)
        self.layoutSwitchBox.addWidget(self.StyleSwitch2)
        self.layoutSwitchBox.addStretch()

        self.UpdateAndStyle = QWidget()
        self.layoutUpdateAndStyle = QHBoxLayout(self.UpdateAndStyle)
        self.layoutUpdateAndStyle.setContentsMargins(0, 0, 0, 0)
        self.layoutUpdateAndStyle.setAlignment(Qt.AlignLeft)
        self.layoutUpdateAndStyle.addWidget(self.FreqUpdate)
        self.layoutUpdateAndStyle.addSpacing(100)
        self.layoutUpdateAndStyle.addWidget(self.StyleSwitchBox)

        self.UpdateAndStyleStackedWidget = QStackedWidget(self)
        self.UpdateAndStyleStackedWidget.addWidget(self.UpdateAndStyle)

        self.FlagChangedStartUpBox = False
        self.StartUpBox = QCheckBox(languageDict.LangDict['StartUpLabel'][gadgetLanguage])
        self.StartUpBox.setStyleSheet("font: 14px")
        if startUp == 0:
            self.StartUpBox.setChecked(False)
        else:
            self.StartUpBox.setChecked(True)
        self.StartUpBox.stateChanged.connect(lambda: setattr(self, 'FlagChangedStartUpBox', True))

        self.AutoUpdateBox = QCheckBox(languageDict.LangDict['AutoUpdateLabel'][gadgetLanguage])
        self.AutoUpdateBox.setStyleSheet("font: 14px")
        if autoUpdate == 0:
            self.AutoUpdateBox.setChecked(False)
        else:
            self.AutoUpdateBox.setChecked(True)

        self.CheckBoxs = QWidget()
        self.layoutBoxs = QHBoxLayout(self.CheckBoxs)
        #self.layoutBoxs.addStretch()
        self.layoutBoxs.addWidget(self.StartUpBox)
        self.layoutBoxs.addSpacing(50)
        self.layoutBoxs.addWidget(self.AutoUpdateBox)

        self.CheckBoxsStackedWidget = QStackedWidget(self)
        self.CheckBoxsStackedWidget.addWidget(self.CheckBoxs)


        self.SaveButton = QPushButton(languageDict.LangDict['SaveBut'][gadgetLanguage])
        self.SaveButton.clicked.connect(self.saveEvent)
        self.SaveButton.setFixedSize(QSize(160, 25))
        self.SaveButton.setToolTip(languageDict.LangDict['SaveTip'][gadgetLanguage])


        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 10)
        self.layout.addWidget(self.WinLabel)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.PosLangStackedWidget)
        self.layout.addSpacing(30)
        self.layout.addWidget(self.PathLabel)
        self.layout.addWidget(self.pathStackedWidget)
        self.layout.addSpacing(0)
        self.layout.addWidget(self.UpdateAndStyleStackedWidget)
        self.layout.addSpacing(0)
        self.layout.addWidget(self.CheckBoxsStackedWidget)
        self.layout.addSpacing(0)
        self.layout.addWidget(self.SaveButton)
        self.setLayout(self.layout)

    def setRadioButtonLanguage(self):
        global gadgetLanguage

        if gadgetLanguage == 0:
            self.radioButtonEng.setChecked(True)
        elif gadgetLanguage == 1:
            self.radioButtonDeu.setChecked(True)
        else:
            self.radioButtonRus.setChecked(True)

    def setRadioButtonPosition(self):
        global gadgetPosition

        dictPos = {1:self.radioButtonP1, 2:self.radioButtonP2, 3:self.radioButtonP3, 4:self.radioButtonP4, 5:self.radioButtonP5,
                   6:self.radioButtonP6, 7:self.radioButtonP7, 8:self.radioButtonP8, 9:self.radioButtonP9}
        dictPos[gadgetPosition].setChecked(True)

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
        global gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, gadgetStyle, color

        self.saving()
        self.restart()

    def openFile(self):
        FilePath = QFileDialog.getOpenFileName(self, 'Open File', './', "CSV (*.csv)")[0]
        self.InputString.setText(FilePath)

    def saving(self):
        global gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, gadgetStyle, color

        fileName = self.InputString.text()
        updateTime = self.dict_direct.get(self.UpdateTime.currentText())
        gadgetLanguage = self.checkRadioButtonLanguage()
        gadgetPosition = self.groupPos.checkedId()
        startUp = int(self.StartUpBox.isChecked())
        autoUpdate = int(self.AutoUpdateBox.isChecked())
        gadgetStyle = int(self.Switch.isChecked())
        color = int(self.Switch2.isChecked())

        SaveSettings(gadgetPosition, gadgetLanguage, fileName, updateTime, startUp, autoUpdate, gadgetStyle, color)
        if self.FlagChangedStartUpBox:
            if startUp == 1:
                StartUpPy.TurnOnStartUp()
            else:
                StartUpPy.TurnOffStartUp()

    def restart(self):
        setStyle()
        w.restart()
        self.destroy()

    def switchStyle(self):
        self.saving()
        self.restart()
        setW = SettingWindow()
        setW.show()

    def switchMono(self):
        self.saving()
        self.restart()
        setW = SettingWindow()
        setW.show()

    def setSwitches(self):
        global gadgetStyle, color

        if gadgetStyle == 0:
            self.Switch.setChecked(False)
        else:
            self.Switch.setChecked(True)

        if color == 0:
            self.Switch2.setChecked(False)
        else:
            self.Switch2.setChecked(True)

class AddWindow(QWidget):
    def __init__(self):
        super().__init__()

        global gadgetPosition, gadgetLanguage, fileName, updateTime, appName

        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 300)

        self.text = languageDict.LangDict['AddLabel'][gadgetLanguage]
        self.path = languageDict.LangDict['AddLabel2'][gadgetLanguage] + '\n' + fileName
        self.firstPunkt = languageDict.LangDict['AddNameLabel'][gadgetLanguage]
        self.secondPunkt = languageDict.LangDict['AddDateLabel'][gadgetLanguage]

        self.WinLabel = QLabel(self)
        self.WinLabel.setText(self.text)
        self.WinLabel.setAlignment(Qt.AlignLeft)
        self.WinLabel.setStyleSheet("font: 24px")

        self.PathLabel = QLabel(self)
        self.PathLabel.setText(self.path)
        self.PathLabel.setAlignment(Qt.AlignLeft)
        self.PathLabel.setStyleSheet("font-size: 12px; font-weight: bold")
        self.PathLabel.setFixedSize(QSize(450, 50))
        self.PathLabel.setWordWrap(True)


        self.FirstPunktLabel = QLabel(self)
        self.FirstPunktLabel.setText(self.firstPunkt)
        self.FirstPunktLabel.setAlignment(Qt.AlignLeft)
        self.FirstPunktLabel.setStyleSheet("font: 12px")

        self.SecondPunktLabel = QLabel(self)
        self.SecondPunktLabel.setText(self.secondPunkt)
        self.SecondPunktLabel.setAlignment(Qt.AlignLeft)
        self.SecondPunktLabel.setStyleSheet("font: 12px")

        self.SaveButton = QPushButton(languageDict.LangDict['SaveBut'][gadgetLanguage])
        self.SaveButton.clicked.connect(self.saveEvent)
        self.SaveButton.setFixedSize(QSize(160, 25))
        self.SaveButton.setToolTip(languageDict.LangDict['SaveTip'][gadgetLanguage])


        self.InputName = QLineEdit()
        self.InputName.setPlaceholderText(languageDict.LangDict['AddNameTip'][gadgetLanguage])
        self.InputName.setFixedSize(QSize(450, 25))


        self.InputDate = QLineEdit()
        self.InputDate.setMaxLength(10)
        self.regexp = QRegExp("^(?:(?:31(\.)(?:0[13578]|1[02]))\1|(?:(?:29|30)(\.)(?:0[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)\d{2})$|^(?:29(\.)(?:02)\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0[1-9]|1\d|2[0-8])(\.)(?:(?:0[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)\d{2})$")
        self.Validator = QRegExpValidator(self.regexp, self.InputDate)
        self.InputDate.setPlaceholderText(languageDict.LangDict['AddDateTip'][gadgetLanguage])
        self.InputDate.setValidator(self.Validator)
        self.InputDate.setFixedSize(QSize(425, 25))
        self.InputDate.textEdited[str].connect(self.format_text)
        self.InputDate.setContentsMargins(0,0,0,0)

        self.CalendarButton = QPushButton('\u02C5')
        self.CalendarButton.clicked.connect(self.openCalendar)
        self.CalendarButton.setFixedSize(QSize(25, 25))
        self.CalendarButton.setToolTip(languageDict.LangDict['CalendarTip'][gadgetLanguage])
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
        self.layout.addSpacing(5)
        self.layout.addWidget(self.PathLabel)
        self.layout.addSpacing(30)
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
        global fileName, gadgetLanguage
        dateText = self.InputDate.text()
        nameText = self.InputName.text()
        if len(dateText) == 10 and nameText != "":
            adding.add_csv(fileName, nameText, dateText)
            w.data_input()
            self.destroy()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(languageDict.LangDict['WarningText'][gadgetLanguage])
            msg.setWindowTitle(languageDict.LangDict['WarningTitle'][gadgetLanguage])
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def openCalendar(self):
        self.calendar = CalendarWindow(self.InputDate)
        self.calendar.show()

class CalendarWindow(QWidget):
    def __init__(self, widget):

        global appName, gadgetLanguage

        super().__init__()
        self.widget = widget
        self.setWindowTitle(appName)
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(360, 250)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate(1900, 1, 1))
        self.calendar.setMaximumDate(QDate(3000, 12, 31))
        self.calendar.setSelectedDate(QDate.currentDate())
        # вставить условие по теме
        self.cal_fmt = self.calendar.headerTextFormat()
        self.cal_fmt.setFont(QFont('OpenSans', 9, QFont.Bold))

        self.cal_fmt.setBackground(QColor('#76797c'))
        for d in (Qt.Saturday, Qt.Sunday,):
            fmt = self.calendar.weekdayTextFormat(d)
            fmt.setForeground(QColor('#fff'))
            self.calendar.setWeekdayTextFormat(d, fmt)

        if gadgetLanguage == 0:
            locale = QLocale(QLocale.English, QLocale.UnitedStates)  # Устанавливаем английскую локаль
        elif gadgetLanguage == 1:
            locale = QLocale(QLocale.German, QLocale.Germany)  # Устанавливаем немецкую локаль
        else:
            locale = QLocale(QLocale.Russian, QLocale.Russia)  # Устанавливаем русскую локаль
        self.calendar.setLocale(locale)

        self.calendar.setHeaderTextFormat(self.cal_fmt)
        self.calendar.clicked.connect(self.getDateCalendar)

        self.layout = QVBoxLayout()
        #self.layout.setContentsMargins(20, 20, 20, 10)
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
    BigButSize = QSize(140, 25)
    SmallButSize = QSize(30, 25)
    HorizontalSpacingBig = 46
    HorizontalSpacingSmall = 2

    def __init__(self, final_stretch=True):
        super(QWidget, self).__init__()

        global gadgetPosition, gadgetLanguage, fileName, updateTime

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        closeButton = QPushButton(languageDict.LangDict['HideBut'][gadgetLanguage])
        closeButton.clicked.connect(self.closeImTray)
        closeButton.setFixedSize(self.BigButSize)
        closeButton.setToolTip(languageDict.LangDict['HideTip'][gadgetLanguage])

        addButton = QPushButton()
        addButton.setObjectName("addButton")
        addButton.clicked.connect(self.addDay)
        addButton.setFixedSize(self.SmallButSize)
        addButton.setToolTip(languageDict.LangDict['AddTip'][gadgetLanguage])

        updateButton = QPushButton()
        updateButton.setObjectName("updateButton")
        updateButton.clicked.connect(self.Update)
        updateButton.setFixedSize(self.SmallButSize)
        updateButton.setToolTip(languageDict.LangDict['RefreschTip'][gadgetLanguage])

        settingsButton = QPushButton()
        settingsButton.setObjectName("settingsButton")
        settingsButton.clicked.connect(self.setting)
        settingsButton.setFixedSize(self.SmallButSize)
        settingsButton.setToolTip(languageDict.LangDict['SetTip'][gadgetLanguage])

        infoButton = QPushButton()
        infoButton.setObjectName("infoButton")
        infoButton.clicked.connect(self.info)
        infoButton.setFixedSize(self.SmallButSize)
        infoButton.setToolTip(languageDict.LangDict['InfoTip'][gadgetLanguage])

        listButton = QPushButton()
        listButton.setObjectName("listButton")
        listButton.clicked.connect(self.showList)
        listButton.setFixedSize(self.SmallButSize)
        listButton.setToolTip(languageDict.LangDict['ListTip'][gadgetLanguage])

        layout.addWidget(closeButton)
        layout.addSpacing(self.HorizontalSpacingBig)
        layout.addWidget(listButton)
        layout.addSpacing(self.HorizontalSpacingSmall)
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

    def showList(self):
        self.listW = ListWindow()
        self.listW.show()

class IconLabel(QWidget):
    HorizontalSpacing = 40

    def __init__(self, qta_id, text, final_stretch=True):

        global gadgetStyle

        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        if gadgetStyle == 0:
            icon = QPixmap('./Data/icon_dark.png')
        else:
            icon = QPixmap('./Data/icon_light.png')
        icon = icon.scaled(30, 30)
        iconWidget = QLabel(self)
        iconWidget.setPixmap(icon)

        label = QLabel(self)
        label.setText(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font: 18px; font-weight: bold")

        layout.addSpacing(10)
        layout.addWidget(iconWidget)
        layout.addSpacing(self.HorizontalSpacing)
        layout.addWidget(label)

        if final_stretch:
            layout.addStretch()


if __name__ == '__main__':
    myappid = 'mycompany.myproduct.subproduct.version'  # переопределение приложения как самостоятельное
    #QtWin.setCurrentProcessExplicitAppUserModelID(myappid) # для смены значка в панели задач

    app = QApplication(sys.argv)

    setStyle()

    screenWidth = app.desktop().screenGeometry().width()
    screenHeight = app.desktop().screenGeometry().height()

    w = PreviewWindow()
    w.show()

    app.exec_()