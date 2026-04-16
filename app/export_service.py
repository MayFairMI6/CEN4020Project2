import io
import pandas as pd
from flask import send_file, abort
from .data_service import DATA_FILE

def export_schedule(format):
    df = pd.read_csv(DATA_FILE)

    if format == "csv":
        output = io.BytesIO()
        output.write(df.to_csv(index=False).encode("utf-8"))
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name="schedule_export.csv",
            mimetype="text/csv",
        )

    if format == "excel":
        output = io.BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name="schedule_export.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    return abort(400, description="Unsupported export format")
