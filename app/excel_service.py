import os
import io
import hashlib
import pandas as pd
from werkzeug.utils import secure_filename
from .data_service import DATA_FILE, normalize_dataframe


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")


def _sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def _file_hash(path):
    with open(path, "rb") as handle:
        return _sha256_bytes(handle.read())


def _unique_filename(folder, filename):
    name, ext = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(folder, candidate)):
        candidate = f"{name}_{counter}{ext}"
        counter += 1
    return candidate


def _normalize_key_columns(df):
    for col in ("TERM", "CRN"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
            df[col] = df[col].replace({"nan": None, "": None, "None": None})
    return df

def import_excel(file):
    filename = (file.filename or "").strip()
    if not filename:
        raise ValueError("No file selected.")

    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".xlsx", ".xls"}:
        raise ValueError("Invalid file type. Please upload an Excel file (.xlsx or .xls).")

    file_bytes = file.read()
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    incoming_hash = _sha256_bytes(file_bytes)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    original_name = secure_filename(filename or "uploaded.xlsx")
    if not original_name:
        original_name = "uploaded.xlsx"

    duplicate_of = None
    for existing_name in os.listdir(UPLOAD_FOLDER):
        existing_path = os.path.join(UPLOAD_FOLDER, existing_name)
        if not os.path.isfile(existing_path):
            continue
        if _file_hash(existing_path) == incoming_hash:
            duplicate_of = existing_name
            break

    saved_filename = duplicate_of
    if duplicate_of is None:
        saved_filename = _unique_filename(UPLOAD_FOLDER, original_name)
        with open(os.path.join(UPLOAD_FOLDER, saved_filename), "wb") as handle:
            handle.write(file_bytes)

    try:
        df = pd.read_excel(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError("Invalid Excel file content.") from exc

    if df.empty:
        raise ValueError("Uploaded Excel file has no rows.")

    df = normalize_dataframe(df)
    df = _normalize_key_columns(df)

    try:
        existing = pd.read_csv(DATA_FILE)
        existing = _normalize_key_columns(existing)
        df = pd.concat([existing, df], ignore_index=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        pass

    if "CRN" in df.columns and "TERM" in df.columns:
        df = df.drop_duplicates(subset=["CRN", "TERM"], keep="last")

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, index=False)

    if duplicate_of is not None:
        message = f"Data imported. Duplicate file detected and skipped: {duplicate_of}"
    else:
        message = f"Data imported. File saved: {saved_filename}"

    return {"message": message, "rows": len(df), "saved_file": saved_filename, "duplicate": duplicate_of is not None}


def rebuild_schedule_database_from_uploads():
    """Rebuild schedule database from all Excel files currently in uploads."""
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    excel_files = [
        os.path.join(UPLOAD_FOLDER, name)
        for name in os.listdir(UPLOAD_FOLDER)
        if name.lower().endswith((".xlsx", ".xls")) and os.path.isfile(os.path.join(UPLOAD_FOLDER, name))
    ]

    if not excel_files:
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        return 0

    dfs = []
    for file_path in excel_files:
        df = pd.read_excel(file_path)
        dfs.append(normalize_dataframe(df))

    combined = pd.concat(dfs, ignore_index=True)
    combined = _normalize_key_columns(combined)
    if "CRN" in combined.columns and "TERM" in combined.columns:
        combined = combined.drop_duplicates(subset=["CRN", "TERM"], keep="last")

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    combined.to_csv(DATA_FILE, index=False)
    return len(combined)
