import csv


def add_csv(path, name, date):
    test_csv(path)
    with open(path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')#, lineterminator='')
        csv_writer.writerow([name, date])

def test_csv(path):
    # with open(path, mode='r', encoding='utf-8') as csv_file:
    #     csv_reader = csv.reader(csv_file, delimiter='\t')
    #     lines = [row for row in csv_reader]
    #     last_line = lines[-1]
    #     if last_line[-1] != '\n':
    #         add_empty_line_at_end(path)

    with open(path, mode='r', encoding='utf-8') as csv_file:
        lines = csv_file.readlines()
        last_line = lines[-1]
        if last_line[-1] != '\n':
            add_empty_line_at_end(path)

def add_empty_line_at_end(path):
    with open(path, mode='a', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t')
        csv_writer.writerow([])

# if __name__ == '__main__':
#      name = 'test2'
#      date = '10.09.2020'
#      path = 'Dates.csv'
#      add_csv(path, name, date)
