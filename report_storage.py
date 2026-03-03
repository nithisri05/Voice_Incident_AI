import os
from openpyxl import Workbook, load_workbook
from datetime import datetime
from zipfile import BadZipFile

FILE_NAME = "incident_reports.xlsx"


def create_new_workbook():
    wb = Workbook()
    ws = wb.active
    ws.title = "Incident Reports"

    headers = [
        "System Timestamp",
        "Incident Date",
        "Incident Time",
        "Reporter Name",
        "Department",
        "Location/Unit",
        "Equipment",
        "Incident Summary",
        "Measured Parameters",
        "Severity"
    ]

    ws.append(headers)
    wb.save(FILE_NAME)


def save_report_to_excel(report_data):

    if not os.path.exists(FILE_NAME):
        create_new_workbook()

    try:
        wb = load_workbook(FILE_NAME)
    except BadZipFile:
        os.remove(FILE_NAME)
        create_new_workbook()
        wb = load_workbook(FILE_NAME)

    ws = wb.active

    ws.append([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        report_data.get("incident_date", ""),
        report_data.get("incident_time", ""),
        report_data.get("reporter_name", ""),
        report_data.get("department", ""),
        report_data.get("location_or_unit", ""),
        report_data.get("equipment", ""),
        report_data.get("incident_summary", ""),
        str(report_data.get("measured_parameters", {})),
        report_data.get("severity", "")
    ])

    wb.save(FILE_NAME)