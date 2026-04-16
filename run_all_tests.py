#!/usr/bin/env python3
"""Run deterministic unit tests and route smoke tests in one command."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path

import pandas as pd

from app import create_app


def run_unit_tests() -> bool:
    suite = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()


def run_route_smoke_tests() -> bool:
    app = create_app()
    client = app.test_client()

    results = []

    def check(path: str, expected=(200,)) -> None:
        response = client.get(path, follow_redirects=False)
        ok = response.status_code in expected
        results.append((path, response.status_code, ok))

    csv_path = Path("data/schedule_database.csv")
    if not csv_path.exists():
        print("FAIL missing data/schedule_database.csv")
        return False

    df = pd.read_csv(csv_path)
    df["TERM"] = df["TERM"].astype(str).str.replace(r"\\.0$", "", regex=True)
    terms = sorted(df["TERM"].dropna().unique())
    if not terms:
        print("FAIL no terms found in schedule data")
        return False

    semester = terms[0]

    room_series = df["MEETING_ROOM"].dropna().astype(str).str.strip().replace("nan", "")
    room_series = room_series[room_series != ""]
    if room_series.empty:
        print("FAIL no room found in schedule data")
        return False
    room = room_series.iloc[0]

    instr_series = df["INSTRUCTOR"].dropna().astype(str).str.strip().replace("nan", "")
    instr_series = instr_series[instr_series != ""]
    if instr_series.empty:
        print("FAIL no instructor found in schedule data")
        return False
    instructor = instr_series.iloc[0]

    course = f"{df['SUBJ'].iloc[0]}{df['CRSE_NUMB'].iloc[0]}"

    backup = csv_path.read_bytes()
    try:
        check("/", (200,))
        check("/files", (200,))

        upload_dir = Path("uploads")
        sample_files = sorted(list(upload_dir.glob("*.xlsx")) + list(upload_dir.glob("*.xls")))
        sample_file = sample_files[0] if sample_files else None

        if sample_file is not None:
            check(f"/view/{sample_file.name}", (200,))
            check(f"/download/{sample_file.name}", (200,))
            check(f"/export/{sample_file.name}", (200,))
        else:
            print("INFO no sample Excel file in uploads; skipping view/download/export file checks")

        check("/export/schedule/csv", (200,))
        check("/export/schedule/excel", (200,))
        check("/export/schedule/pdf", (400,))

        check("/schedule/room", (200,))
        check(f"/schedule/room/{room}?semester={semester}", (200,))
        check(f"/schedule/room/{room}", (302,))

        check("/schedule/vacancy", (200,))
        check(f"/schedule/vacancy/results?semester={semester}&duration=75", (200,))
        check("/schedule/vacancy/results?semester=&duration=75", (302,))

        check("/schedule/instructor", (200,))
        check(f"/schedule/instructor/{instructor}?semester={semester}", (200,))
        check(f"/schedule/instructor/{instructor}", (302,))

        check("/schedule/search", (200,))
        check(f"/schedule/search?department=COP&semester={semester}", (200,))

        check("/schedule/comparison", (200,))
        if len(terms) >= 2:
            check(f"/schedule/comparison/{terms[0]}/{terms[1]}", (200, 302))
            check(f"/schedule/comparison/details/{terms[0]}/{terms[1]}/{course}", (200,))

        check("/view/DOES_NOT_EXIST.xlsx", (404,))

        if sample_file is not None:
            with sample_file.open("rb") as handle:
                data = {"file": (io.BytesIO(handle.read()), sample_file.name)}
                response = client.post(
                    "/upload",
                    data=data,
                    content_type="multipart/form-data",
                    follow_redirects=False,
                )
                results.append(("/upload", response.status_code, response.status_code == 200))
        else:
            print("INFO no sample Excel file in uploads; skipping upload check")
    finally:
        csv_path.write_bytes(backup)

    all_ok = all(ok for _, _, ok in results)
    print(f"ROUTE_ALL_OK {all_ok}")
    print(f"ROUTE_TOTAL {len(results)}")
    for path, status, ok in results:
        prefix = "PASS" if ok else "FAIL"
        print(prefix, status, path)

    return all_ok


def main() -> int:
    print("=== Running unit tests ===")
    unit_ok = run_unit_tests()

    print("\n=== Running route smoke tests ===")
    smoke_ok = run_route_smoke_tests()

    all_ok = unit_ok and smoke_ok
    print("\n=== Summary ===")
    print(f"UNIT_TESTS_OK {unit_ok}")
    print(f"ROUTE_TESTS_OK {smoke_ok}")
    print(f"ALL_OK {all_ok}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
