#!/usr/bin/env python3

import sys
import os
from datetime import datetime

sys.path.insert(1, '../CDR')
import cdr

sys.path.insert(1, '../NetFlow')
import netflow

from fpdf import FPDF

CDR_FILE = '../CDR/data.csv'

NETFLOW_FILE      = '../NetFlow/nfcapd.202002251200'
NETFLOW_DUMP_FILE = '../NetFlow/dump.txt' 

PDF_FILE = 'payment.pdf'

def pdf_common_line(pdf, font_size, text):
    pdf.write(font_size / 2, text)
    pdf.ln(font_size / 2)

def create_pdf(bank_name, inn, kpp, bik, recipient, account_number1, account_number2, doc_number, date, provider, customer, reason):
    header = [['Банк получателя: ' + bank_name      , 'БИК: ' + bik],
            ["ИНН: " + inn + "   " + "КПП: " + kpp, 'Сч. №' + account_number1],
            ['Получатель: ' + recipient           , 'Сч. №' + account_number2]]
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', './fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', './fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
    
    pdf.set_font('DejaVu', '', 12)
    
    # header
    col_width = pdf.w / 2.2
    row_height = pdf.font_size
    spacing = 2
    for row in header:
        for item in row:
            pdf.cell(col_width, row_height * spacing,
                     txt=item, border=1)
        pdf.ln(row_height * spacing)

    font_size = 16
    pdf.set_font('DejaVu', 'B', font_size)
    pdf.ln(font_size / 2)
    pdf_common_line(pdf, font_size, "Счёт на оплату №{} от {}г.".format(doc_number, date))
    pdf_common_line(pdf, font_size, "_" * 74)

    font_size = 12
    pdf.ln(font_size)
    pdf.set_font('DejaVu', '', font_size)
    pdf_common_line(pdf, font_size, "Поставщик")
    pdf_common_line(pdf, font_size, "(Исполнитель): {}".format(provider))
    pdf_common_line(pdf, font_size, "")
    pdf_common_line(pdf, font_size, "Покупатель")
    pdf_common_line(pdf, font_size, "(Заказчик): {}".format(customer))
    pdf_common_line(pdf, font_size, "")
    pdf_common_line(pdf, font_size, "Основание: {}".format(reason))
    pdf_common_line(pdf, font_size, "")

    # table
    font_size = 10
    row_height = pdf.font_size
    pdf.set_font('DejaVu', '', font_size)

    table = [['№', "Товары (работы, услуги)", "Кол-во", "Ед.", "Сумма"]]
    counter = 1

    # in calls
    for in_record in in_calls:
        table.append([str(counter), "Входящий звонок от {}".format(in_record[0]), "{} мин.".format(in_record[1]), "{} руб.".format(in_min_cost), "{} руб.".format(in_record[1] * in_min_cost)])
        counter += 1

    if in_min_free:
        min_to_calc = min(in_min_free, res_count_in)
        table.append([str(counter), "Бесплатные минуты входящих звонков", "{} мин.".format(in_min_free), '', "{} руб.".format(min_to_calc * in_min_cost * -1)])
        counter += 1

    # out calls
    for out_record in out_calls:
        table.append([str(counter), "Исходящий звонок к {}".format(out_record[0]), "{} мин.".format(out_record[1]), "{} руб.".format(out_min_cost), "{} руб.".format(out_record[1] * out_min_cost)])
        counter += 1

    if out_min_free:
        min_to_calc = min(out_min_free, res_count_out)
        table.append([str(counter), "Бесплатные минуты исходящих звонков", "{} мин.".format(out_min_free), '', "{} руб.".format(min_to_calc * out_min_cost * -1)])
        counter += 1

    # sms
    for sms_record in sms_list:
        table.append([str(counter), "SMS для {}".format(sms_record[0]), "{} шт.".format(sms_record[1]), "{} руб.".format(sms_cost), "{} руб.".format(sms_record[1] * sms_cost)])
        counter += 1

    if sms_free:
        min_to_calc = min(sms_free, res_count_sms)
        table.append([str(counter), "Бесплатные SMS", "{} шт.".format(sms_free), '', "{} руб.".format(min_to_calc * sms_cost * -1)])
        counter += 1

    # internet
    table.append([str(counter), "Интернет трафик (за МБ)", "{} МБ".format(traffic_mb), "{} руб.".format(Mb_cost), "{} руб.".format(net_cost)])

    table.append(['', "ВСЕГО", '', '', "{} руб.".format(cost_tel + net_cost)])

    one_part = pdf.w / 18
    for row in table:
        pdf.cell(one_part * 1, row_height * spacing, txt=row[0], border=1) # number
        pdf.cell(one_part * 8, row_height * spacing, txt=row[1], border=1) # title
        pdf.cell(one_part * 2, row_height * spacing, txt=row[2], border=1) # count
        pdf.cell(one_part * 2, row_height * spacing, txt=row[3], border=1) # cost per one
        pdf.cell(one_part * 3, row_height * spacing, txt=row[4], border=1) # total cost
        pdf.ln(row_height * spacing)

    # footer
    font_size = 16
    pdf.set_font('DejaVu', 'B', font_size)
    pdf_common_line(pdf, font_size, "Всего к оплате: {} руб.".format(cost_tel + net_cost))
    pdf_common_line(pdf, font_size, "")

    font_size = 8
    pdf.set_font('DejaVu', '', font_size)
    pdf_common_line(pdf, font_size, "Внимание!")
    pdf_common_line(pdf, font_size, "Оплата данного счёта означает согласие с условиями поставки товара/предоставления услуг.")
    pdf_common_line(pdf, font_size, "")
    
    font_size = 16
    pdf.set_font('DejaVu', 'B', font_size)
    pdf.ln(font_size / 2)
    pdf_common_line(pdf, font_size, "_" * 74)
    font_size = 12
    pdf.set_font('DejaVu', '', font_size)
    pdf.ln(font_size / 2)
    pdf_common_line(pdf, font_size, "Руководитель " + "_" * 20 + " " * 25 + "Бухгалтер " + "_" * 20)
    
    pdf.output(name=PDF_FILE, dest='F').encode('utf-8')

# variant 18 mod 15 = 3
if __name__ == "__main__":
    print("== Payment document ==")
    
    if not os.path.exists(CDR_FILE):
        print("File {} doesn't exist".format(CDR_FILE))
        sys.exit(-1)

    if not os.path.exists(NETFLOW_DUMP_FILE):
        print("Creating dump of NetFlow file...")

        if not os.path.exists(NETFLOW_FILE):
            print("File {} doesn't exist".format(NETFLOW_FILE))
            sys.exit(-1)

        os.system("nfdump -r " + NETFLOW_FILE + " > " + NETFLOW_DUMP_FILE)
        if not os.path.exists(NETFLOW_DUMP_FILE):
            print("File {} doesn't exist".format(NETFLOW_DUMP_FILE))
            sys.exit(-1)

    # 1 lab
    tel_number = "915783624"
    in_min_cost  = 0
    in_min_free  = 0
    out_min_cost = 2
    out_min_free = 20
    sms_cost = 2
    sms_free = 0
    
    print("Tariffing calls and SMS...")
    in_calls, out_calls, sms_list, \
        res_count_in, res_count_out, res_count_sms, \
            cost_in, cost_out, cost_sms \
                = cdr.tariffing(CDR_FILE,
                                tel_number,
                                in_min_cost, in_min_free,
                                out_min_cost, out_min_free,
                                sms_cost, sms_free)
    
    cost_tel = cost_in + cost_out + cost_sms

    # 2 lab
    ip_addr = "192.168.250.27"
    Mb_cost = 1

    print("Tariffing the Internet...")
    date_data_list, ip_data_list = netflow.parse_dump(NETFLOW_DUMP_FILE)
    traffic_mb, traffic_volume, net_cost = netflow.tariffing(ip_data_list, ip_addr, Mb_cost)

    # pdf
    print("Creating PDF file...")
    create_pdf(bank_name="Лучший Банк", inn='11122233', kpp='0000001', bik='31337', \
               recipient="Иванов Иван", account_number1="111111", account_number2="222222", \
               doc_number="1", date=datetime.now().strftime("%d.%m.%Y"), \
               provider="Провайдер", customer="Иван ({}, {})".format(ip_addr, tel_number), reason="День оплаты")

