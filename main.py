import matplotlib.pyplot as plt
import csv
import glob
import fire

VERBOSE = True
PERCENTAGE_CASES = True
COUNTRIES = set()
EXPORT = True
EXPORT_FORMAT = "png"
SHOW = False

country_synonyms = dict()


def add_country_synonym(country_a, country_b):
    if country_a in country_synonyms.keys():
        country_synonyms[country_a].append(country_b)
    else:
        country_synonyms[country_a] = [country_b]


def get_data():
    population = dict()
    with open("population.csv", newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            population[row[0]] = int(row[1])

    dict_country_cases_time = dict()
    files = list(glob.glob("COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv"))
    files.sort()
    for file in files:
        file_date = file.split("/")[-1].split(".")[0]
        file_date = file_date.split("-")[2] + "-" + file_date.split("-")[0] + "-" + file_date.split("-")[1]

        idx_country_region = 1
        idx_confirmed = 3
        idx_deaths = 4
        idx_recovered = 5

        if file_date >= "2020-03-22":
            idx_country_region = 3
            idx_confirmed = 7
            idx_deaths = 8
            idx_recovered = 9

        with open(file, newline='\n') as csvfile:
            dict_country_cases = dict()
            dict_country_cases["World"] = (0, 0, 0)

            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(reader)
            for row in reader:
                country_ = row[idx_country_region]

                for country in country_synonyms.keys():
                    if country_ in country_synonyms[country]:
                        country_ = country
                        break

                if country_ in dict_country_cases.keys():
                    dict_country_cases[country_] = (dict_country_cases[country_][0] +
                                                    int(float(row[idx_confirmed]) if row[idx_confirmed] else 0),
                                                    dict_country_cases[country_][1] +
                                                    int(float(row[idx_deaths]) if row[idx_deaths] else 0),
                                                    dict_country_cases[country_][2] +
                                                    int(float(row[idx_recovered]) if row[idx_recovered] else 0))
                else:
                    dict_country_cases[country_] = (int(float(row[idx_confirmed]) if row[idx_confirmed] else 0),
                                                    int(float(row[idx_deaths]) if row[idx_deaths] else 0),
                                                    int(float(row[idx_recovered]) if row[idx_recovered] else 0))
                dict_country_cases["World"] = (
                                                dict_country_cases["World"][0] + int(float(row[idx_confirmed])
                                                                                     if row[idx_confirmed] else 0),
                                                dict_country_cases["World"][1] + int(float(row[idx_deaths])
                                                                                     if row[idx_deaths] else 0),
                                                dict_country_cases["World"][2] + int(float(row[idx_recovered])
                                                                                     if row[idx_recovered] else 0))

        date = file[-14:-4]
        dict_country_cases_time[date[6:] + "-" + date[:2] + "-" + date[3:5]] = dict_country_cases

    return dict_country_cases_time, population


def filter_data(dict_country_cases_time, population):
    if VERBOSE:
        print("{:15s} - {:15s}: {:7s} {:7s} {:7s}\n".format("country", "time", "confirmed", "deaths", "recovered"))

    time_list = list(dict_country_cases_time.keys())
    time_list.sort()

    confirmed = []
    deaths = []
    recovered = []

    for time in time_list:
        confirmed_ = 0
        deaths_ = 0
        recovered_ = 0
        for country in COUNTRIES:
            country_ = country
            for c in country_synonyms.keys():
                if country_ in country_synonyms[c]:
                    country_ = c
                    break

            if country_ in dict_country_cases_time[time]:
                if VERBOSE:
                    print("{:15s} - {:15s}: {:7d} {:7d} {:7d}".format(country_, time,
                                                                      dict_country_cases_time[time][country_][0],
                                                                      dict_country_cases_time[time][country_][1],
                                                                      dict_country_cases_time[time][country_][2]))
                confirmed_ += dict_country_cases_time[time][country_][0]
                deaths_ += dict_country_cases_time[time][country_][1]
                recovered_ += dict_country_cases_time[time][country_][2]

        confirmed_ -= (deaths_ + recovered_)

        if PERCENTAGE_CASES:
            population_ = 0
            for country in COUNTRIES:
                found = False
                for c in country_synonyms.keys():
                    if country in country_synonyms[c]:
                        country_ = c
                        found = True
                        break
                if not found:
                    country_ = country

                population_ += population[country_]
            confirmed_ = confirmed_ / population_ * 100
            deaths_ = deaths_ / population_ * 100
            recovered_ = recovered_ / population_ * 100

        confirmed.append(confirmed_)
        deaths.append(deaths_)
        recovered.append(recovered_)

    return confirmed, deaths, recovered


def draw_graph(dict_country_cases_time, confirmed, deaths, recovered):
    xaxis = list(dict_country_cases_time.keys())
    xaxis.sort()

    fig, ax = plt.subplots()
    ax.plot(xaxis, confirmed, label='currently infected', color='orangered')
    ax.plot(xaxis, deaths, label='deaths', color='gold')
    ax.plot(xaxis, recovered, label='recovered', color='cornflowerblue')
    ax.legend()
    plt.title(" + ".join(COUNTRIES))
    plt.ylabel('percentage cases' if PERCENTAGE_CASES else 'total cases')
    plt.xticks(rotation=45)
    plt.grid(color='lightgray', linestyle='-', axis='x')
    plt.grid(color='lightgray', linestyle='-', axis='y')
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=min(xaxis), xmax=max(xaxis))
    for idx in range(len(ax.xaxis.get_ticklabels()))[::-1]:
        if idx % 15:
            ax.xaxis.get_ticklabels()[idx].set_visible(False)
    if EXPORT:
        name = list(COUNTRIES)
        name.sort()
        for i in range(len(name)):
            name[i] = name[i].replace(" ", "-")
        plt.savefig('{}.{}'.format("_".join(name), EXPORT_FORMAT), bbox_inches='tight')
    if SHOW:
        plt.show()


def main():
    add_country_synonym("DR Congo", "Congo (Kinshasa)")
    add_country_synonym("United States", "US")
    add_country_synonym("Congo", "Congo (Brazzaville)")
    add_country_synonym("Côte d'Ivoire", "Cote d'Ivoire")
    add_country_synonym("Czech Republic (Czechia)", "Czechia")
    add_country_synonym("Other", "Diamond Princess")
    add_country_synonym("South Korea", "Korea, South")
    add_country_synonym("Other", "MS Zaandam")
    add_country_synonym("Saint Kitts & Nevis", "Saint Kitts and Nevis")
    add_country_synonym("St. Vincent & Grenadines", "Saint Vincent and the Grenadines")
    add_country_synonym("Taiwan", "Taiwan*")
    add_country_synonym("Palestinian territories", "West Bank and Gaza")
    add_country_synonym("China", "Mainland China")
    add_country_synonym("United States", "US")
    add_country_synonym("South Korea", "Republic of Korea")

    dict_country_cases_time, population = get_data()
    confirmed, deaths, recovered = filter_data(dict_country_cases_time, population)
    draw_graph(dict_country_cases_time, confirmed, deaths, recovered)


def parse_args(country='World', verbose=True, percentage_cases=True, export=True, export_format='png', show=False):
    global VERBOSE
    global PERCENTAGE_CASES
    global COUNTRIES
    global EXPORT
    global EXPORT_FORMAT
    global SHOW

    VERBOSE = verbose
    PERCENTAGE_CASES = percentage_cases
    COUNTRIES.add(country)
    EXPORT = export
    EXPORT_FORMAT = export_format
    SHOW = show


if __name__ == "__main__":
    fire.Fire(parse_args)
    main()
