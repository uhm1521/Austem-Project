import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from streamlit.testing.v1 import AppTest

from workreq.dashboard import RECENT_LIMIT, summarize
from workreq.models import clean_input
from workreq.storage import list_requests, save_request

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
SAMPLE = clean_input("가상 요청", "김가상", "영업팀")


class SummarizeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "requests.db"

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty(self):
        s = summarize([])
        self.assertEqual(s["total"], 0)
        self.assertEqual(sum(s["work_type"].values()), 0)
        self.assertEqual(s["recent"], [])

    def test_counts_match_saved_data(self):
        save_request(SAMPLE, "IT 지원", "높음", "전산팀", path=self.db)
        save_request(SAMPLE, "IT 지원", "보통", "전산팀", path=self.db)
        save_request(SAMPLE, "구매", "낮음", "경영지원팀", path=self.db)
        s = summarize(list_requests(self.db))
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["work_type"]["IT 지원"], 2)
        self.assertEqual(s["work_type"]["구매"], 1)
        self.assertEqual(s["work_type"]["인사"], 0)
        self.assertEqual(s["urgency"], {"높음": 1, "보통": 1, "낮음": 1})
        self.assertEqual(s["department"]["전산팀"], 2)
        self.assertEqual(s["department"]["경영지원팀"], 1)
        for key in ["work_type", "urgency", "department"]:
            self.assertEqual(sum(s[key].values()), s["total"])

    def test_recent_is_limited_and_newest_first(self):
        for _ in range(RECENT_LIMIT + 2):
            last = save_request(SAMPLE, "인사", "낮음", "인사팀", path=self.db)
        s = summarize(list_requests(self.db))
        self.assertEqual(len(s["recent"]), RECENT_LIMIT)
        self.assertEqual(s["recent"][0]["id"], last)


class DashboardPageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "requests.db"
        self.env = mock.patch.dict(os.environ, {"WORKREQ_DB_PATH": str(self.db)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def open_dashboard(self):
        at = AppTest.from_file(APP_PATH).run()
        at.sidebar.radio(key="page").set_value("대시보드").run()
        return at

    def test_empty_dashboard(self):
        at = self.open_dashboard()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, "0건")
        self.assertTrue(any("저장된 요청이 없습니다" in i.value for i in at.info))

    def test_dashboard_matches_saved_data(self):
        save_request(SAMPLE, "시설", "높음", "경영지원팀", path=self.db)
        save_request(SAMPLE, "인사", "낮음", "인사팀", path=self.db)
        at = self.open_dashboard()
        self.assertFalse(at.exception)
        self.assertEqual(at.metric[0].value, "2건")
        work_type_table = at.dataframe[0].value
        self.assertEqual(int(work_type_table.loc[work_type_table["업무유형"] == "시설", "건수"].iloc[0]), 1)
        self.assertEqual(len(at.dataframe[3].value), 2)

    def test_load_failure_shows_message(self):
        self.db.write_text("not a database", encoding="utf-8")
        at = self.open_dashboard()
        self.assertFalse(at.exception)
        self.assertTrue(any("불러오지 못했습니다" in e.value for e in at.error))


if __name__ == "__main__":
    unittest.main()
