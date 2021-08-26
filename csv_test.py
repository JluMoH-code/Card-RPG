import csv 

with open("table.csv", "r") as file:
	reader = csv.reader(file)

	table = {row[0]:int(row[1]) for row in reader}
	sorted_dict = {}
	sorted_keys = sorted(table, key=table.get)

	print(table)

	for key in sorted_keys:
		sorted_dict[key] = table[key]

with open("table_sorted.csv", "w", newline="") as file:
	writer = csv.writer(file)

	for line in sorted_dict:
		writer.writerow([line, sorted_dict[line]])

with open("table_sorted.csv", "r", newline="") as file:
	reader = csv.reader(file)

	table = {row[0]:int(row[1]) for row in reader}

	print(table)