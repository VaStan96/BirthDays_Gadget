from datetime import datetime
import csv
import languageDict

def rewrite_csv(path, language, data):
    #dates = [str(data.item(x, 0).text()) + "\t" + str(data.item(x, 1).text()) for x in range(data.rowCount())]
    dates = []
    for x in range(data.rowCount()):
        IsDate = True
        try:
            dat = data.item(x, 1).text()
            datetime.strptime(data.item(x, 1).text(), '%Y-%m-%d')
        except ValueError:
            IsDate = False


        if data.item(x, 0).text() != "" and IsDate:
            dates.append(data.item(x, 0).text() + "\t" + change_date_format(data.item(x, 1).text()))
        else:
            #print('Error in str ' + str(x))
            return x+1

    try:
        csvfile = open(path, 'w', encoding='utf-8',)
        writer = csv.writer(csvfile, delimiter='\n')
        writer.writerow(dates)
        csvfile.close()
    except:
        return False
    return True

def change_date_format(date):
    yyyy = str(date[:4])
    MM = str(date[5:7])
    dd = str(date[8:])
    return dd+'.'+MM+'.'+yyyy

# if __name__ == '__main__':
#     print(sort_csv('Dates.csv'))