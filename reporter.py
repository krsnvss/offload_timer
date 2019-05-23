import xlsxwriter
from datetime import datetime
from sql import *
from misc import *
from subprocess import Popen


def create_report():
        
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('Отчет за смену.xlsx')

    worksheet_name = datetime.now().strftime('%d.%m.%Y')

    worksheet = workbook.add_worksheet(worksheet_name)
    bold = workbook.add_format({'bold': True,
                                'font_size':14,
                                'font_name':'Arial'})
    semibold = workbook.add_format({'bold': True,
                                    'font_size':10,
                                    'font_name':'Arial'})
    table_header = workbook.add_format({'bold': True,
                                    'font_size':10,
                                    'border':1,
                                    'bg_color':'#000000',
                                    'font_color':'#FFFFFF',
                                    'font_name':'Arial',
                                    'align':'center'})
    date_fmt = workbook.add_format({'font_size':10,
                                    'font_name':'Arial',
                                    'border':1,
                                    'num_format': 'dd.mm.yyyy hh:mm:ss'})
    int_fmt = workbook.add_format({'font_size':10,
                                'font_name':'Arial',
                                'border':1,
                                'num_format':1})
    date_fmt_odd = workbook.add_format({'font_size':10,
                                    'font_name':'Arial',
                                    'border':1,
                                    'bg_color':'#DFDFDF',
                                    'num_format': 'dd.mm.yyyy hh:mm:ss'})
    int_fmt_odd = workbook.add_format({'font_size':10,
                                'font_name':'Arial',
                                'border':1,
                                'bg_color':'#DFDFDF',
                                'num_format':1})
    time_fmt = workbook.add_format({'font_size':10,
                                    'font_name':'Arial',
                                    'border':1, 
                                    'num_format':21,
                                    'bg_color':'#AAFF7F'})
    late_fmt = workbook.add_format({'font_size':10,
                                    'font_name':'Arial',
                                    'border':1,
                                    'num_format':21,
                                    'bg_color':'#BE6666'})

    rows = shift_data()

    worksheet.write(0, 0, 'Отчет за смену', bold)
    report_date = shift_time(datetime.now())
    worksheet.write(1, 0, '{} - {}'.format(report_date[0].strftime("%d.%m.%Y %H:%M:%S"),
                                        report_date[1].strftime("%d.%m.%Y %H:%M:%S")), semibold)

    # Start from the first cell. Rows and columns are zero indexed.
    row = 4
    col = 0

    # table headers
    worksheet.write(3, 0, "Время выгрузки", table_header)
    worksheet.write(3, 1, "Смена", table_header)
    worksheet.write(3, 2, "Интервал", table_header)

    # first date value in rows list
    first_date = datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S")

    # Iterate over the data and write it out row by row.
    for _item in rows:
        new_date = datetime.strptime(_item[0], "%Y-%m-%d %H:%M:%S")
        delta = new_date - first_date
        if row % 2 != 0:
            worksheet.write(row, col, new_date, date_fmt_odd)
            worksheet.write(row, col + 1, _item[1], int_fmt_odd)
        else:
            worksheet.write(row, col, new_date, date_fmt)
            worksheet.write(row, col + 1, _item[1], int_fmt)
        if delta.seconds > 180:
            worksheet.write(row, col + 2, delta, late_fmt)
        else:
            worksheet.write(row, col + 2, delta, time_fmt)
        row += 1
        first_date = new_date

    # Write a total using a formula.
    worksheet.write(row, 0, 'Всего:', semibold)
    worksheet.write(row, 1, '=COUNT(B4:B{})'.format(row), table_header)

    # Set column width
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:C', 10)
    # make a chart
    # collect chart data
    hours_total = []
    _hour = shift_time(datetime.now())[0]
    while _hour <= shift_time(datetime.now())[1]:
        hours_total.append([_hour.hour, hour_total_report(_hour)])
        _hour += timedelta(seconds=3600)

    print(hours_total)
    # write totals to table
    worksheet.write(3, 4, "Час", table_header)
    worksheet.write(3, 5, "Выгрузки", table_header)
    totals_row = 4
    totals_col = 4

    for _item in hours_total:
        if totals_row % 2 != 0:
            worksheet.write(totals_row, totals_col, _item[0], int_fmt_odd)
            worksheet.write(totals_row, totals_col + 1, _item[1], int_fmt_odd)
        else:
            worksheet.write(totals_row, totals_col, _item[0], int_fmt)
            worksheet.write(totals_row, totals_col + 1, _item[1], int_fmt)
        totals_row += 1

    # Create a new chart object.
    chart = workbook.add_chart({'type': 'column'})

    # Add a series to the chart.
    chart.add_series({'values': '={}!$F$4:$F${}'
                    .format(worksheet_name, totals_row)})
    chart.set_x_axis({'name': 'Часы смены'})
    chart.set_y_axis({'name': 'Количество выгрузок'})

    # Insert the chart into the worksheet.
    worksheet.insert_chart('E18', chart)

    workbook.close()
    # Uncomment to launch libreoffice calc automatically
    # Popen(["libreoffice", "--calc", "Отчет за смену.xlsx"])

