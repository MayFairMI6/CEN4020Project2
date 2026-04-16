import unittest

from app.schedule_routes import _detect_time_conflicts


class CrossListedConflictTests(unittest.TestCase):
    def _empty_grid(self):
        return {day: [] for day in ["M", "T", "W", "R", "F", "S"]}

    def test_cross_listed_overlap_is_ignored(self):
        grid = self._empty_grid()
        grid["M"] = [
            {
                "subj": "COP",
                "crse_numb": "4930",
                "crse_title": "Concepts of Computer Security",
                "time_display": "11:00 AM - 12:15 PM",
                "start_time": "11:00 AM",
                "end_time": "12:15 PM",
            },
            {
                "subj": "CIS",
                "crse_numb": "6930",
                "crse_title": "Concepts of Computer Security",
                "time_display": "11:00 AM - 12:15 PM",
                "start_time": "11:00 AM",
                "end_time": "12:15 PM",
            },
        ]

        conflicts = _detect_time_conflicts(grid)
        self.assertEqual(conflicts, [])

    def test_non_cross_listed_overlap_is_reported(self):
        grid = self._empty_grid()
        grid["M"] = [
            {
                "subj": "COP",
                "crse_numb": "4703",
                "crse_title": "Database Systems",
                "time_display": "11:00 AM - 12:15 PM",
                "start_time": "11:00 AM",
                "end_time": "12:15 PM",
            },
            {
                "subj": "CEN",
                "crse_numb": "4020",
                "crse_title": "Software Engineering",
                "time_display": "11:30 AM - 12:45 PM",
                "start_time": "11:30 AM",
                "end_time": "12:45 PM",
            },
        ]

        conflicts = _detect_time_conflicts(grid)
        self.assertEqual(len(conflicts), 1)

    def test_same_title_but_same_level_is_reported(self):
        grid = self._empty_grid()
        grid["M"] = [
            {
                "subj": "COP",
                "crse_numb": "3514",
                "crse_title": "Program Design",
                "time_display": "09:30 AM - 10:45 AM",
                "start_time": "09:30 AM",
                "end_time": "10:45 AM",
            },
            {
                "subj": "COP",
                "crse_numb": "2510",
                "crse_title": "Program Design",
                "time_display": "10:00 AM - 11:15 AM",
                "start_time": "10:00 AM",
                "end_time": "11:15 AM",
            },
        ]

        conflicts = _detect_time_conflicts(grid)
        self.assertEqual(len(conflicts), 1)

    def test_same_crn_duplicate_is_not_reported(self):
        grid = self._empty_grid()
        grid["M"] = [
            {
                "subj": "COP",
                "crse_numb": "3515",
                "crse_title": "Adv Program Design",
                "time_display": "12:30 PM - 01:45 PM",
                "start_time": "12:30 PM",
                "end_time": "01:45 PM",
                "crn": "15509.0",
            },
            {
                "subj": "COP",
                "crse_numb": "3515",
                "crse_title": "Adv Program Design",
                "time_display": "12:30 PM - 01:45 PM",
                "start_time": "12:30 PM",
                "end_time": "01:45 PM",
                "crn": "15509.0",
            },
        ]

        conflicts = _detect_time_conflicts(grid)
        self.assertEqual(conflicts, [])


if __name__ == "__main__":
    unittest.main()
