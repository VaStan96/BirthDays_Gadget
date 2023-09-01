import csv


def add_csv(path, name, date):
    test_csv(path)
    with open(path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')#, lineterminator='')
        csv_writer.writerow([name, date])

def test_csv(path):
    with open(path, 'r') as file:
        lines = file.readlines()
        last_line = lines[-1]
        if last_line[-1] != '\n':
            add_empty_line_at_end(path)

def add_empty_line_at_end(path):
    with open(path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        csv_writer.writerow([])


# if __name__ == '__main__':
#      name = input()
#      date = input()
#      path = 'Dates.csv'
#      add_csv(path, name, date)
