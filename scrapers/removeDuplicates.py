import csv


def remove_duplicates(input_file, output_file):
    seen = set()
    exclude_keywords = {
        'refill', 'set', 'travel spray', 'candle', 'rollerball', 'mist', 'deodorant', 'oil', 'lotion'
    }

    with open(input_file, mode='r', newline='', encoding='utf-8') as infile, \
            open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        writer.writerow(header)

        for row in reader:
            brand, name = row[0], row[1]
            lower_name = name.lower()

            if (brand, name) not in seen and not any(keyword in lower_name for keyword in exclude_keywords):
                writer.writerow(row)
                seen.add((brand, name))
            else:
                print(f'Skipping duplicate or excluded item - Brand: {brand}, Name: {name}')

# Treba samo rucno podesiti ulazni i izlazni fajl
if __name__ == "__main__":
    input_csv = 'togetherTemp.csv'
    output_csv = 'togetherUnique.csv'

    remove_duplicates(input_csv, output_csv)
    print('Duplicate rows removed and saved to', output_csv)
