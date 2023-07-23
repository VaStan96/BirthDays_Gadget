import sys

import qtawesome as qta

from PyQt5.QtWinExtras import QtWin  # !!!
from PyQt5.QtGui import QIcon, QPixmap, QColor, QCloseEvent
from PyQt5.QtCore import Qt, QSize, QThread, QMetaObject, QTimer
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QSystemTrayIcon, QMainWindow,
        QHBoxLayout, QPushButton, QTextEdit, QHeaderView, QVBoxLayout, QAction, QMenu,
        QWidget, QLabel, QTableWidget, QTableWidgetItem, QStyle, QStyleFactory, qApp)

import parsing

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
        self.timer.start(7200000)

    def data_input(self):
        items = parsing.sort_csv('Dates.csv')
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

class ButtonButton(PreviewWindow):
    BigButSize = QSize(160, 25)
    SmallButSize = QSize(30, 25)
    HorizontalSpacingBig = 90
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

        if final_stretch:
            layout.addStretch()

    def closeImTray(self):
        w.hide()

    def Update(self):
        w.data_input()

    def info(self):
        pass

    def addDay(self):
        pass

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