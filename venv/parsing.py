from datetime import datetime
import csv
from PyQt5.QtWidgets import QMessageBox
import languageDict
import calendar

def pars_csv(path, language):
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
                    alt = today.year - int(row[1].split('.')[2]) +1

                Birthdays.append([row[0], row[1], days, alt])
        csvfile.close()
    except:
        msgbox = QMessageBox()
        msgbox.setText(languageDict.LangDict['CSVErrorText'][language])
        msgbox.setStandardButtons(QMessageBox.Close)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setWindowTitle(languageDict.LangDict['CSVErrorTitle'][language])
        msgbox.exec()
        Birthdays = []

    return Birthdays

def sort_csv(path, language):
    Birthdays = pars_csv(path, language)
    sort_data = sorted(Birthdays, key=lambda x: x[2])

    updated = []
    for i in sort_data[-2:]:
        birthday_date = datetime(datetime.today().year, int(i[1].split('.')[1]), int(i[1].split('.')[0])).date()
        if birthday_date > datetime.date(datetime.today()):
            birthday_date = datetime(datetime.today().year - 1, int(i[1].split('.')[1]), int(i[1].split('.')[0])).date()

        days_since_birthday = (datetime.date(datetime.today()) - birthday_date).days
        updated.append([i[0], i[1], -days_since_birthday, i[3] - 1])

    data = list(reversed(updated + sort_data[:5]))
    data = [[i[0],i[1],i[3],i[2]] for i in data]
    return data

# if __name__ == '__main__':
#     print(sort_csv('.\\Data\\Dates.csv', 0))