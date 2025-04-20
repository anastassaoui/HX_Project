import fpdf
import datetime
import sys
import os
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    logging.debug("Starting report generation")

    data = [
        {"Parameter": "Shell Side Mass Flow Rate", "Value": 11023.1, "Unit": "lb/h"},
        {"Parameter": "Tube Side Mass Flow Rate", "Value": 26455.5, "Unit": "lb/h"},
        {"Parameter": "Shell Side Inlet Temperature", "Value": 206.33, "Unit": "°F"},
        {"Parameter": "Tube Side Inlet Temperature", "Value": -9.67, "Unit": "°F"},
        {"Parameter": "Shell Side Outlet Temperature", "Value": 117.04, "Unit": "°F"},
        {"Parameter": "Tube Side Outlet Temperature", "Value": 80.33, "Unit": "°F"},
    ]

    for item in data:
        if not all(key in item for key in ["Parameter", "Value", "Unit"]):
            logging.error("Invalid data dictionary")
            sys.exit(1)

    pdf = fpdf.FPDF(format='A4')
    pdf.add_page()
    pdf.set_margins(10, 10, 10)

    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 10, "Heat Exchanger Simulation Report", 0, 1, 'C')
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 10, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 1, 'C')
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(50, 50, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 8, "Parameter", 1, 0, 'L', fill=True)
    pdf.cell(50, 8, "Value", 1, 0, 'R', fill=True)
    pdf.cell(40, 8, "Unit", 1, 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)

    pdf.set_font("Arial", '', 8)
    for i, item in enumerate(data):
        pdf.set_fill_color(240 if i % 2 == 0 else 220)
        pdf.cell(100, 8, item["Parameter"], 1, 0, 'L', fill=i % 2 == 0)
        pdf.cell(50, 8, str(item["Value"]), 1, 0, 'R', fill=i % 2 == 0)
        pdf.cell(40, 8, item["Unit"], 1, 1, 'L', fill=i % 2 == 0)

    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    summary = f"The shell side mass flow rate ({data[0]['Value']} {data[0]['Unit']}) and tube side mass flow rate ({data[1]['Value']} {data[1]['Unit']}) produced inlet temperatures of{data[2]['Value']}{data[2]['Unit']} and {data[3]['Value'] if data[3]['Value'] >= 0 else '-' + str(abs(data[3]['Value']))}{data[3]['Unit']}, respectively, resulting in outlet temperatures of{data[4]['Value']}{data[4]['Unit']} and{data[5]['Value']}{data[5]['Unit']}. This indicates efficient heat transfer under design conditions."
    pdf.multi_cell(0, 5, summary)

    pdf.alias_nb_pages()
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Page {pdf.page_no()}/{{nb}}", 0, 0, 'C')

    pdf.output("report.pdf")
    logging.debug("PDF saved: report.pdf")

    if not os.path.exists("report.pdf") or os.path.getsize("report.pdf") == 0:
        logging.error("PDF file is empty or does not exist")
        sys.exit(2)

    if args.test:
        print(data)
        print(summary)

    logging.debug("Report generation completed")
    sys.exit(0)

if __name__ == "__main__":
    main()