from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import csv
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSize

def pars_csv(path):
    Birthdays = []
    today = datetime.date(datetime.today())

    try:
        csvfile = open(path, encoding='utf-8')
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            if row != []:
                delta1 = datetime(today.year, int(row[1].split('.')[1]), int(row[1].split('.')[0])).date()
                delta2 = datetime(today.year + 1, int(row[1].split('.')[1]), int(row[1].split('.')[0])).date()

                if delta1 >= today:
                    days = (delta1-today).days
                    alt = today.year - int(row[1].split('.')[2])
                else:
                    days = (delta2 - today).days
                    alt = today.year - int(row[1].split('.')[2]) + 1

                Birthdays.append([row[0], row[1], days, alt])
        csvfile.close()
    except:
        msgbox = QMessageBox()
        msgbox.setText('Check your .CSV-file!')
        msgbox.setStandardButtons(QMessageBox.Close)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setWindowTitle('ERROR')
        msgbox.exec()
        Birthdays = []

    return Birthdays

def sort_csv(path):
    Birthdays = pars_csv(path)
    sort_data = sorted(Birthdays, key=lambda x: x[2])
    minus = [[i[0], i[1], i[2] - 366, i[3]-1] for i in sort_data[-2:]]
    data = list(reversed(minus + sort_data[:5]))
    data = [[i[0],i[1],i[3],i[2]] for i in data]
    return data

# if __name__ == '__main__':
#     print(sort_csv('new.csv'))