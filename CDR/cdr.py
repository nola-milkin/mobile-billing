#!/usr/bin/env python3

import sys
import os
import csv
import math

CDR_FILE = 'data.csv'

def parse_cdr(cdr_file, tel_number):
    in_calls  = list()
    out_calls = list()
    sms_list  = list()

    with open(cdr_file) as f:
        data = csv.DictReader(f)
    
        for record in data:
            number_from   = record['msisdn_origin']
            number_to     = record['msisdn_dest']
            call_duration = record['call_duration']
            sms           = record['sms_number']

            if number_from == tel_number:
                out_calls.append([number_to, math.ceil(float(call_duration))])
                sms_list.append([number_to, int(sms)])
            
            if number_to == tel_number:
                in_calls.append([number_from, math.ceil(float(call_duration))])

    return in_calls, out_calls, sms_list
    

def tarif(tel_number, in_min_cost, in_min_free, out_min_cost, out_min_free, sms_cost, sms_free):

    cost_in  = 0
    cost_out = 0
    cost_sms = 0
    
    # returns lists of [target, count]
    in_calls, out_calls, sms_list = parse_cdr(CDR_FILE, tel_number)

    # iterate on list to sum all of count
    for in_record in in_calls:
        cost_in += in_record[1]
        
    # subtitute free ones and then power with cost
    cost_in  = 0 if ((cost_in - in_min_free) <= 0) else (cost_in - in_min_free) * in_min_cost 
    
    for out_record in out_calls:
        cost_out += out_record[1]
    cost_out = 0 if ((cost_out - out_min_free) <= 0) else (cost_out - out_min_free) * out_min_cost

    for sms_record in sms_list:
        cost_sms += sms_record[1]
    cost_sms = 0 if ((cost_sms - sms_free) <= 0) else (cost_sms - sms_free) * sms_cost

    return in_calls, out_calls, sms_list, \
           cost_in, cost_out, cost_sms


# variant 18 mod 15 = 3
if __name__ == "__main__":
    print("== Call Detail Record ==")
    
    if len(sys.argv) >= 2:
        CDR_FILE = sys.argv[1]

    if not os.path.exists(CDR_FILE):
        print("File {} doesn't exist".format(CDR_FILE))
        sys.exit(-1)

    tel_number = "915783624"
    in_min_cost  = 0
    in_min_free  = 0
    out_min_cost = 2
    out_min_free = 20
    sms_cost = 2
    sms_free = 0
    
    print("------------------------------------------")
    print("Abonent: " + tel_number)
    print("------------------------------------------")
    print("Cost per minute (incoming) : {} rub.".format(in_min_cost))
    print("Free minutes    (incoming) : {} minutes".format(in_min_free))
    print("")
    print("Cost per minute (outgoing) : {} rub.".format(out_min_cost))
    print("Free minutes    (outgoing) : {} minutes".format(out_min_free))
    print("")
    print("Cost per SMS               : {} rub.".format(sms_cost))
    print("Free SMS                   : {} sms".format(sms_free))
    print("------------------------------------------")
    
    print("Tariffing...")
    in_calls, out_calls, sms_list, \
        cost_in, cost_out, cost_sms \
            = tarif(tel_number, in_min_cost, in_min_free, out_min_cost, out_min_free, sms_cost, sms_free)
    
    cost_tel = cost_in + cost_out
    
    print("------------------------------------------")
    print("Incoming calls:")
    for in_record in in_calls:
        print("From {} ({} min)\t  : {} rub.".format(in_record[0], in_record[1], in_record[1] * in_min_cost))
    if in_min_free:
        print("Free minutes (incoming)   : {} rub.".format(in_min_free * in_min_cost * -1))
    print("Total incoming calls cost : {} rub.".format(cost_in))

    print("------------------------------------------")
    print("Outgoing calls:")
    for out_record in out_calls:
        print("To {} ({} min)\t  : {} rub.".format(out_record[0], out_record[1], out_record[1] * out_min_cost))
    if out_min_free:
        print("Free minutes (outgoing)   : {} rub.".format(out_min_free * out_min_cost * -1))
    print("Total outgoing calls cost : {} rub.".format(cost_out))

    print("------------------------------------------")
    print("SMS:")
    for sms_record in sms_list:
        print("To {} ({} SMS)\t  : {} rub.".format(sms_record[0], sms_record[1], sms_record[1] * sms_cost))
    if sms_free:
        print("Free SMS                  : {} rub.".format(sms_free * sms_cost * -1))
    print("Total SMS cost            : {} rub.".format(cost_sms))

    print("------------------------------------------")
    print("TOTAL COST : {} rub.".format(cost_tel + cost_sms))
    print("")
