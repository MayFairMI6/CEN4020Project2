import pandas as pd
from flask import send_file

DAFA_FILE = "data/schedule_database.csv"

def export_schedule(format):
    df = pd.read_csv(DAFA_FILE)
    
    if format == "csv":
        file = "schedule_export.cvs"
        df.to_csv(file, index = False)
        return send_file(file, as_attachment = True)
    
    if format == "excel":
        file = "schedule_export.xlsx"
        df.to_excel(file, index = False)
        return send_file(file, as_attachment = True)
    