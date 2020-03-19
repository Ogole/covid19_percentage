import matplotlib.pyplot as plt
import csv
import glob

PERCENTAGE_CASES = False

country_synonyms = []


def add_country_synonym(country_a, country_b):
    found = False

    idx = 0
    for l in country_synonyms:
        if country_a in l:
            country_synonyms[idx].append(country_b)
            found = True
        elif country_b in l:
            country_synonyms[idx].append(country_a)
            found = True
        idx = idx + 1

    if not found:
        country_synonyms.append([country_a, country_b])


def get_data():
    population = dict()
    with open("population.csv", newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            population[row[0]] = int(row[1])

    for l in country_synonyms:
        max_population = 0
        for country in l:
            if (country in population) and (max_population < population[country]):
                max_population = population[country]
        for country in l:
            population[country] = max_population

    files = list(glob.glob("COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv"))
    files.sort()
    file = files[-1]

    with open(file, newline='\n') as csvfile:
        dict_country_cases = dict()

        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(reader)
        for row in reader:
            if row[1] in dict_country_cases.keys():
                dict_country_cases[row[1]] = (dict_country_cases[row[1]][0] + int(row[3] if row[3] else 0),
                                              dict_country_cases[row[1]][1] + int(row[4] if row[4] else 0),
                                              dict_country_cases[row[1]][2] + int(row[5] if row[5] else 0))
            else:
                dict_country_cases[row[1]] = (int(row[3] if row[3] else 0),
                                              int(row[4] if row[4] else 0),
                                              int(row[5] if row[5] else 0))

    return dict_country_cases, population


def filter_data(dict_country_cases, population):
    print("{:35s}: {:10s} {:10s} {:10s} {:10s}\n".format("country", "infected", "infected per", "deaths", "recovered"))

    max_country = ""
    max_infected = 0

    dcc_sorted = dict()

    for country in dict_country_cases.keys():
        dcc_sorted[country] = [dict_country_cases[country][0],
                                 dict_country_cases[country][0] / population[country] * 100 if population[country] > 0 else 0,
                                 dict_country_cases[country][1],
                                 dict_country_cases[country][2]]

    if PERCENTAGE_CASES:
        dcc_sorted = {k: v for k, v in sorted(dcc_sorted.items(), key=lambda item: item[1][1], reverse=True)}
    else:
        dcc_sorted = {k: v for k, v in sorted(dcc_sorted.items(), key=lambda item: item[1][0], reverse=True)}

    for country in dcc_sorted.keys():
        print("{:35s}: {:10d} {:10f} {:10d} {:10d}".format(country,
                                                       dcc_sorted[country][0],
                                                       dcc_sorted[country][1],
                                                       dcc_sorted[country][2],
                                                       dcc_sorted[country][3]))

        if PERCENTAGE_CASES:
            if (dcc_sorted[country][1]) > max_infected:
                max_infected = dcc_sorted[country][1]
                max_country = country
        else:
            if (dcc_sorted[country][0]) > max_infected:
                max_infected = dcc_sorted[country][0]
                max_country = country

    print("The country {} has the highest infection rate ({} {}).".format(max_country, max_infected, "per" if PERCENTAGE_CASES else ""))


def main():
    add_country_synonym("China", "Mainland China")
    add_country_synonym("Russia", "Russian Federation")
    add_country_synonym("Taiwan", "Taiwan*")
    add_country_synonym("Taiwan", "Taipei and environs")
    add_country_synonym("Iran", "Iran (Islamic Republic of)")
    add_country_synonym("South Korea", "Republic of Korea")
    add_country_synonym("South Korea", "Korea, South")
    add_country_synonym("China", "Hong Kong SAR")
    add_country_synonym("China", "Hong Kong")
    add_country_synonym("China", "Macau")
    add_country_synonym("United Kingdom", "UK")
    add_country_synonym("Congo(Kinshasa)", "Congo (Brazzaville)")
    add_country_synonym("Gambia, The", "The Gambia")

    dict_country_cases_time, population = get_data()

    filter_data(dict_country_cases_time, population)


if __name__ == "__main__":
    main()
