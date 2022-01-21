import datetime
from math import dist
import matplotlib.pyplot as plt

def read_latest_n_points(n):
    with open("data/data.csv", 'r') as f:
        file_content = f.read()

    lines = file_content.split('\n')
    relevant_lines = lines[-n::]

    # data is stored in the following format time,onshore,offshore,solar,conv,total,gpkwh
    data = {
        'time': [],
        'onshore': [],
        'offshore': [],
        'solar': [],
        'conv': [],
        'total': [],
        'gpkwh': []
    }

    for line in relevant_lines:
        if not line:
            break

        line_elements = line.split(',')

        data['time'].append(datetime.datetime.strptime(line_elements[0], "%Y-%m-%d %H:%M:%S.%f").timestamp())
        data['onshore'].append(float(line_elements[1]))
        data['offshore'].append(float(line_elements[2]))
        data['solar'].append(float(line_elements[3]))
        data['conv'].append(float(line_elements[4]))
        data['total'].append(float(line_elements[5]))
        data['gpkwh'].append(float(line_elements[6]))

    return data

def convert_to_plot_data(data):
    """use like this:
    time, distribution, total, gpkwh = convert_to_stackplot_data(data)
    ax.stackplot(time, distribution)
    ax.plot(time, total)
    ax.twinx().plot(time, gpkwh)"""
    return [data['time'], [data['offshore'], data['onshore'], data['solar'], data['conv']], data['total'], data['gpkwh']]


if __name__ == "__main__":
    fig, ax = plt.subplots()
    time, distribution, total, gpkwh = convert_to_plot_data(read_latest_n_points(10))
    ax.stackplot(time, distribution, labels=["onshore", "offshore", "solar", "conv"])
    ax.plot(time, total, label='total')
    ax.set_xlabel('time')
    ax.set_ylabel('power in GW')
    ax.xaxis.set_major_formatter(lambda x, pos: datetime.datetime.fromtimestamp(x).strftime("%H:%M"))

    ax2 = ax.twinx()
    ax2.set_ylim(200, 720)
    ax2.plot(time, gpkwh, 'black', label='emission')
    ax2.set_ylabel('g CO2 per kWh')

    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.show()
