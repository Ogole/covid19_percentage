import matplotlib.pyplot as plt
import csv
import glob

VERBOSE = True
PERCENTAGE_CASES = True
COUNTRIES = {"World"}
EXPORT = False
EXPORT_FORMAT = "png"
SHOW = True


def add_country_synonym(country1, country2):
    if country1 in COUNTRIES:
        COUNTRIES.add(country2)
    if country2 in COUNTRIES:
        COUNTRIES.add(country1)


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

        print("{}: {}".format(file_date, file_date >= "2020-03-22"))
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
                if row[idx_country_region] in dict_country_cases.keys():
                    dict_country_cases[row[idx_country_region]] = (dict_country_cases[row[idx_country_region]][0] +
                                                                   int(row[idx_confirmed] if row[idx_confirmed] else 0),
                                                                   dict_country_cases[row[idx_country_region]][1] +
                                                                   int(row[idx_deaths] if row[idx_deaths] else 0),
                                                                   dict_country_cases[row[idx_country_region]][2] +
                                                                   int(row[idx_recovered] if row[idx_recovered] else 0))
                else:
                    dict_country_cases[row[idx_country_region]] = (int(row[idx_confirmed] if row[idx_confirmed] else 0),
                                                                   int(row[idx_deaths] if row[idx_deaths] else 0),
                                                                   int(row[idx_recovered] if row[idx_recovered] else 0))
                dict_country_cases["World"] = (
                dict_country_cases["World"][0] + int(row[idx_confirmed] if row[idx_confirmed] else 0),
                dict_country_cases["World"][1] + int(row[idx_deaths] if row[idx_deaths] else 0),
                dict_country_cases["World"][2] + int(row[idx_recovered] if row[idx_recovered] else 0))

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
            if country in dict_country_cases_time[time]:
                if VERBOSE:
                    print("{:15s} - {:15s}: {:7d} {:7d} {:7d}".format(country, time,
                                                                      dict_country_cases_time[time][country][0],
                                                                      dict_country_cases_time[time][country][1],
                                                                      dict_country_cases_time[time][country][2]))
                confirmed_ += dict_country_cases_time[time][country][0]
                deaths_ += dict_country_cases_time[time][country][1]
                recovered_ += dict_country_cases_time[time][country][2]

        confirmed_ -= (deaths_ + recovered_)

        if PERCENTAGE_CASES:
            population_ = 0
            for country in COUNTRIES:
                population_ += population[country]
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
        if idx % 7:
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
    add_country_synonym("US", "Puerto Rico")
    add_country_synonym("Bahamas, The", "The Bahamas")
    add_country_synonym("Bahamas, The", "Bahamas")
    add_country_synonym("Gambia, The", "Gambia")
    add_country_synonym("Others", "Diamond Princess")

    dict_country_cases_time, population = get_data()

    confirmed, deaths, recovered = filter_data(dict_country_cases_time, population)

    draw_graph(dict_country_cases_time, confirmed, deaths, recovered)


if __name__ == "__main__":
    main()
