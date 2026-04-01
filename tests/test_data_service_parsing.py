import unittest

import pandas as pd

from app.data_service import build_weekly_grid, parse_meeting_days, parse_meeting_time


class DataServiceParsingTests(unittest.TestCase):
    def test_parse_meeting_days_handles_nan_float(self):
        self.assertEqual(parse_meeting_days(float("nan")), [])

    def test_parse_meeting_time_handles_nan_float(self):
        self.assertEqual(parse_meeting_time(float("nan")), (None, None))

    def test_build_weekly_grid_skips_invalid_day_time_rows(self):
        classes_df = pd.DataFrame(
            [
                {
                    "SUBJ": "CIS",
                    "CRSE_NUMB": "4930",
                    "CRSE_TITLE": "Valid Course",
                    "CRSE_SECTION": "1",
                    "INSTRUCTOR": "Test Instructor",
                    "MEETING_ROOM": "SOC 150",
                    "MEETING_DAYS": "F",
                    "MEETING_TIMES": "08:00 AM - 10:45 AM",
                    "CRN": "12345",
                },
                {
                    "SUBJ": "CIS",
                    "CRSE_NUMB": "6930",
                    "CRSE_TITLE": "Invalid Row",
                    "CRSE_SECTION": "2",
                    "INSTRUCTOR": "Test Instructor",
                    "MEETING_ROOM": "SOC 150",
                    "MEETING_DAYS": float("nan"),
                    "MEETING_TIMES": float("nan"),
                    "CRN": "67890",
                },
            ]
        )

        grid = build_weekly_grid(classes_df)

        self.assertEqual(len(grid["F"]), 1)
        self.assertEqual(grid["F"][0]["crn"], "12345")


if __name__ == "__main__":
    unittest.main()
