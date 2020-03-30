#!/usr/bin/env python3

import sys
import os
import re
import math
from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

NETFLOW_FILE      = 'nfcapd.202002251200'
NETFLOW_DUMP_FILE = 'dump.txt' 

RE_DATA = re.compile(r'(\d+-\d+-\d+) (\d+:\d+:\d+\.\d+) (\w+)[ ]+(\w+ \w+)[ ]+((\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}):(\d+)|(.*?\.\d+))[ ]+->[ ]+((\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}):(\d+)|(.*?\.\d+))[ ]+((\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}):(\d+))[ ]+->[ ]+((\d{0,3}\.\d{0,3}\.\d{0,3}\.\d{0,3}):(\d+))[ ]+(\d+)[ ]+(\d+)')

def parse_dump(dump_file, is_graph=True, is_net=True):
    date_data_list = list()
    ip_data_list   = list()

    if (not is_graph) and (not is_net):
        print("[-] No reason to parse")
    else:
        with open(dump_file) as f:
            data = f.read()
        for match in re.findall(RE_DATA, data):
            # valid string matches as list of 20 elements
            if len(match) == 20:
                if is_graph:
                    date_data_list.append([match[0], match[1], match[-2]])
                if is_net:
                    ip_data_list.append([match[5], match[-2]])

    return date_data_list, ip_data_list

def graph(date_data_list):
    record_time   = list()
    traffic_count = list()

    min_date = None
    max_date = None
    max_traffic = 0
    for record in date_data_list:
        # datetime.strptime("11:21:06.190"[:-4], '%H:%M:%S')
        cur_datetime = datetime.strptime(record[0] + " " + record[1][:-4], '%Y-%m-%d %H:%M:%S')
        record_time.append(cur_datetime)

        if (min_date == None) or (min_date > cur_datetime):
            min_date = cur_datetime

        if (max_date == None) or (max_date < cur_datetime):
            max_date = cur_datetime
        
        cur_traffic = int(record[2]) / 1000000.0
        traffic_count.append(cur_traffic)

        if (max_traffic < cur_traffic):
            max_traffic = cur_traffic

    ax = plt.subplot()

    ax.set_ylabel('Traffic volume (Megabytes)')
    ax.set_xlabel('Time (hours and minutes)')

    ax.set_title('Graph of traffic volume per time')
    ax.set_xlim(min_date - timedelta(minutes=5), max_date + timedelta(minutes=5))
    ax.set_ylim(0, max_traffic + 0.05)

    formatter = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(formatter)

    ax.plot(record_time, traffic_count, "o")

    plt.gcf().set_size_inches(10, 7)
    plt.gcf().autofmt_xdate()
    plt.grid(True)
    plt.show()

def tariffing(ip_data_list, ip_addr, Mb_cost):
    traffic_volume = 0
    
    for record in ip_data_list:
        if record[0] == ip_addr:
            traffic_volume += int(record[1])

    # to Megabytes
    traffic_mb = math.ceil(traffic_volume / 1000000.0)

    traffic_cost = traffic_mb * Mb_cost

    return traffic_mb, traffic_volume, traffic_cost

# variant 18 mod 15 = 3
if __name__ == "__main__":
    print("== NetFlow Protocol ==")
    
    if len(sys.argv) >= 2:
        NETFLOW_FILE = sys.argv[1]

    if not os.path.exists(NETFLOW_DUMP_FILE):
        print("Creating dump of NetFlow file...")

        if not os.path.exists(NETFLOW_FILE):
            print("File {} doesn't exist".format(NETFLOW_FILE))
            sys.exit(-1)

        os.system("nfdump -r " + NETFLOW_FILE + " > " + NETFLOW_DUMP_FILE)
        if not os.path.exists(NETFLOW_DUMP_FILE):
            print("File {} doesn't exist".format(NETFLOW_DUMP_FILE))
            sys.exit(-1)

    ip_addr = "192.168.250.27"
    Mb_cost = 1
    
    print("------------------------------------------")
    print("IP address: " + ip_addr)
    print("Rate for 1 Mb : {} rub.".format(Mb_cost))
    print("------------------------------------------")
    
    print("Tariffing...")
    date_data_list, ip_data_list = parse_dump(NETFLOW_DUMP_FILE)

    traffic_mb, traffic_volume, net_cost = tariffing(ip_data_list, ip_addr, Mb_cost)
    print("Traffic {} bytes -> {} Mbytes ".format(traffic_volume, traffic_mb))
    print("Cost for {} Mb : {} rub.".format(traffic_mb, net_cost))
    print("")

    print("Drawing the graph...")
    graph(date_data_list)