import sys

import qtawesome as qta

from PyQt5.QtWinExtras import QtWin  # !!!
from PyQt5.QtGui import QIcon, QPixmap, QColor, QCloseEvent, QRegExpValidator
from PyQt5.QtCore import Qt, QSize, QThread, QMetaObject, QTimer, QRegExp
from PyQt5.QtWidgets import *

import parsing, adding

import time


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super(SystemTrayIcon, self).__init__(icon, parent)
        self.activateWindowEvent = None

        self.menu = QMenu(parent)
        self.showAction = QAction("Show", parent, triggered=self._show)
        self.hideAction = QAction("Hide", parent, triggered=self._hide)
        self.exitAction = QAction("Close", parent, triggered=self._exit)
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
    fileName = 'Dates.csv'
    updateTime = 7200000

    def __init__(self, parent=None):
        super(PreviewWindow, self).__init__(parent)

        self.setWindowFlags(
            Qt.Window
            | Qt.WindowStaysOnBottomHint     # <<<=====<
            #| Qt.CustomizeWindowHint         # Отключает подсказки заголовка окна по умолчанию.
            #| Qt.WindowTitleHint             # Придает окну строку заголовка.
            #| Qt.MSWindowsFixedSizeDialogHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )

        self.setWindowTitle("BirthDays_Gadget_v1")
        self.setGeometry(1530, 10, 350, 200)
        self.setFixedSize(380, 320)

        self.tray_icon = SystemTrayIcon(QIcon('icon.png'), self)
        self.tray_icon.activateWindowEvent = self.toggle_window
        self.tray_icon.show()


        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(7)

        self.table.setHorizontalHeaderLabels(["Name", "Date", "Age", "Days left"])
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
        layout.addWidget(IconLabel("fa.birthday-cake", "BirthDays_Gadget_v1.1"))
        layout.addWidget(self.table)
        layout.addWidget(ButtonButton())
        self.setLayout(layout)

        self.auto_update()

    def auto_update(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.data_input)
        self.timer.start(self.updateTime)

    def data_input(self):
        items = parsing.sort_csv(self.fileName)
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

class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BirthDays_Gadget_v1")
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 200)


        self.text = "-\-\- Ivan Stanchenko-/-/- (07.2023)\n\n" \
               "A desktop widget for Windows to display the birthdays of your relatives,\nfriends and colleagues.\n\n" \
               "- Information is collected from a CSV file, which makes it possible to import names \nand dates as a list at once.\n" \
               "- To add names and dates one by one, use the ""+"" button.\n" \
               "- Updating is carried out automatically every 2 hours or by clicking on \nthe ""Update"" button.\n" \
               "- You can close the widget using the context menu in the tray.\n"

        self.label = QLabel(self)
        self.label.setText(self.text)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("font: 12px")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.destroy()

class SettingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BirthDays_Gadget_v1")
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 300) #500x200

        self.dict_direct = {'1 Hour': 3600000, '2 Hour': 7200000, '6 Hour': 21600000, '12 Hour': 43200000, '1 Day': 86400000}
        self.dict_reverse = {3600000: '1 Hour', 7200000: '2 Hour', 21600000: '6 Hour', 43200000: '12 Hour', 86400000: '1 Day'}

        self.text = "Settings"
        self.firstPunkt = "Path to source file (.csv):"
        self.secondPunkt = "Update frequency:"

        self.WinLabel = QLabel(self)
        self.WinLabel.setText(self.text)
        self.WinLabel.setAlignment(Qt.AlignLeft)
        self.WinLabel.setStyleSheet("font: 24px")

        self.FirstPunktLabel = QLabel(self)
        self.FirstPunktLabel.setText(self.firstPunkt)
        self.FirstPunktLabel.setAlignment(Qt.AlignLeft)
        self.FirstPunktLabel.setStyleSheet("font: 12px")

        self.SecondPunktLabel = QLabel(self)
        self.SecondPunktLabel.setText(self.secondPunkt)
        self.SecondPunktLabel.setAlignment(Qt.AlignLeft)
        self.SecondPunktLabel.setStyleSheet("font: 12px")


        self.SaveButton = QPushButton("Save")
        self.SaveButton.clicked.connect(self.saveEvent)
        self.SaveButton.setFixedSize(QSize(160, 25))

        self.newFileButton = QPushButton('...')
        self.newFileButton.clicked.connect(self.openFile)
        self.newFileButton.setFixedSize(QSize(30, 25))

        self.InputString = QLineEdit()
        self.InputString.setText(w.fileName)
        self.InputString.setFixedSize(QSize(400,25))
        self.InputString.deselect()

        self.UpdateTime = QComboBox()
        self.UpdateTime.setFixedSize(QSize(110, 25))
        self.UpdateTime.addItems(['1 Hour', '2 Hour', '6 Hour', '12 Hour', '1 Day'])
        temp = self.dict_reverse.get(w.updateTime)
        self.UpdateTime.setCurrentText(temp)


        self.input = QWidget()
        self.layoutH = QHBoxLayout(self.input)
        self.layoutH.setContentsMargins(0, 0, 0, 0)
        self.layoutH.addWidget(self.InputString)
        self.layoutH.addWidget(self.newFileButton)

        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.addWidget(self.input)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 40, 20, 10)
        self.layout.addWidget(self.WinLabel)
        self.layout.addSpacing(60)
        self.layout.addWidget(self.FirstPunktLabel)
        self.layout.addWidget(self.stackedWidget)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SecondPunktLabel)
        self.layout.addWidget(self.UpdateTime)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SaveButton)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.destroy()

    def saveEvent(self):
        w.fileName = self.InputString.text()
        w.updateTime = self.dict_direct.get(self.UpdateTime.currentText())
        w.data_input()
        self.destroy()

    def openFile(self):
        FilePath = QFileDialog.getOpenFileName(self, 'Open File', './', "CSV (*.csv)")[0]
        self.InputString.setText(FilePath)

class AddWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BirthDays_Gadget_v1")
        self.setGeometry(1300, 100, 500, 500)
        self.setFixedSize(500, 300)

        self.text = "Add"
        self.path = "Adding in file: " + w.fileName
        self.firstPunkt = "Added Name:"
        self.secondPunkt = "Added Date:"

        self.WinLabel = QLabel(self)
        self.WinLabel.setText(self.text)
        self.WinLabel.setAlignment(Qt.AlignLeft)
        self.WinLabel.setStyleSheet("font: 24px")

        self.PathLabel = QLabel(self)
        self.PathLabel.setText(self.path)
        self.PathLabel.setAlignment(Qt.AlignLeft)
        self.PathLabel.setStyleSheet("font-size: 14px; font-weight: bold")

        self.FirstPunktLabel = QLabel(self)
        self.FirstPunktLabel.setText(self.firstPunkt)
        self.FirstPunktLabel.setAlignment(Qt.AlignLeft)
        self.FirstPunktLabel.setStyleSheet("font: 12px")

        self.SecondPunktLabel = QLabel(self)
        self.SecondPunktLabel.setText(self.secondPunkt)
        self.SecondPunktLabel.setAlignment(Qt.AlignLeft)
        self.SecondPunktLabel.setStyleSheet("font: 12px")

        self.SaveButton = QPushButton("Save")
        self.SaveButton.clicked.connect(self.saveEvent)
        self.SaveButton.setFixedSize(QSize(160, 25))



        self.InputName = QLineEdit()
        self.InputName.setPlaceholderText('Event|Name|Surname|Family')
        self.InputName.setFixedSize(QSize(400, 25))

        self.InputDate = QLineEdit()
        self.regexp = QRegExp("(((0[1-9])|([12][0-9])|(3[01]))\.((0[0-9])|(1[012]))\.((20[012]\d|19\d\d)|(1\d|2[0123])))")
        self.Validator = QRegExpValidator(self.regexp, self.InputDate)
        self.InputDate.setPlaceholderText('Date in the form "dd.mm.yyyy"')
        self.InputDate.setValidator(self.Validator)
        self.InputDate.setFixedSize(QSize(400, 25))

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 40, 20, 10)
        self.layout.addWidget(self.WinLabel)
        self.layout.addSpacing(60)
        self.layout.addWidget(self.PathLabel)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.FirstPunktLabel)
        self.layout.addWidget(self.InputName)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SecondPunktLabel)
        self.layout.addWidget(self.InputDate)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.SaveButton)
        self.setLayout(self.layout)

    def closeEvent(self, event):
        self.destroy()

    def saveEvent(self):
        adding.add_csv(w.fileName, self.InputName.text(), self.InputDate.text())
        w.data_input()
        self.destroy()


class ButtonButton(PreviewWindow):
    BigButSize = QSize(160, 25)
    SmallButSize = QSize(30, 25)
    HorizontalSpacingBig = 58
    HorizontalSpacingSmall = 2

    def __init__(self, final_stretch=True):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        closeButton = QPushButton("Hide")
        closeButton.clicked.connect(self.closeImTray)
        closeButton.setFixedSize(self.BigButSize)

        addButton = QPushButton()
        addButton.clicked.connect(self.addDay)
        addButton.setFixedSize(self.SmallButSize)
        addButton.setIcon(QIcon('add.png'))

        updateButton = QPushButton()
        updateButton.clicked.connect(self.Update)
        updateButton.setFixedSize(self.SmallButSize)
        updateButton.setIcon(QIcon('up.png'))

        settingsButton = QPushButton()
        settingsButton.clicked.connect(self.setting)
        settingsButton.setFixedSize(self.SmallButSize)
        settingsButton.setIcon(QIcon('setting.png'))

        infoButton = QPushButton()
        infoButton.clicked.connect(self.info)
        infoButton.setFixedSize(self.SmallButSize)
        infoButton.setIcon(QIcon('info.png'))

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


    #myappid = 'mycompany.myproduct.subproduct.version'  # переопределение приложения как самомтоятельное
    #QtWin.setCurrentProcessExplicitAppUserModelID(myappid) # для смены значка в панели задач

    app = QApplication(sys.argv)
    #app.setStyleSheet(QSS)

    w = PreviewWindow()
    w.show()


    sys.exit(app.exec_())