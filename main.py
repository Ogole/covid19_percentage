import matplotlib.pyplot as plt
import csv
import glob

VERBOSE = False
PERCENTAGE_CASES = True
COUNTRIES = {"China"}
EXPORT = False


def add_country_synonym(country1, country2):
    if country1 in COUNTRIES:
        COUNTRIES.add(country2)
    elif country2 in COUNTRIES:
        COUNTRIES.add(country1)


if __name__ == "__main__":
    add_country_synonym("China", "Mainland China")
    add_country_synonym("Russia", "Russian Federation")

    population = dict()
    with open("population.csv", newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            population[row[0]] = int(row[1])

    dict_country_cases_time = dict()
    for file in glob.glob("COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/*.csv"):
        with open(file, newline='\n') as csvfile:
            dict_country_cases = dict()
            dict_country_cases["World"] = (0, 0, 0)

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
                dict_country_cases["World"] = (dict_country_cases["World"][0] + int(row[3] if row[3] else 0),
                                               dict_country_cases["World"][1] + int(row[4] if row[4] else 0),
                                               dict_country_cases["World"][2] + int(row[5] if row[5] else 0))

        date = file[-14:-4]
        dict_country_cases_time[date[6:] + "-" + date[:2] + "-" + date[3:5]] = dict_country_cases

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

    xaxis = list(dict_country_cases_time.keys())
    xaxis.sort()

    fig, ax = plt.subplots()
    ax.plot(xaxis, confirmed, label='confirmed')
    ax.plot(xaxis, deaths, label='deaths')
    ax.plot(xaxis, recovered, label='recovered')
    ax.legend()
    plt.title(" + ".join(COUNTRIES))
    plt.ylabel('percentage cases' if PERCENTAGE_CASES else 'total cases')
    plt.xticks(rotation=90)
    for label in ax.xaxis.get_ticklabels()[::2]:
        label.set_visible(False)
    if EXPORT:
        plt.savefig('{}.pdf'.format("_".join(COUNTRIES)), bbox_inches='tight')
    plt.show()
