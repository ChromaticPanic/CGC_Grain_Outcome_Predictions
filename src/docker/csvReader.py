import csv

with open('provBoundaries.csv', newline='') as provBoundaries:
    reader = csv.DictReader(provBoundaries)

    for row in reader:
        print(row['provID'])