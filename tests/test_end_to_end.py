import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from streamlit.testing.v1 import AppTest

from test_recommender import EXAMPLES

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


class EndToEndTest(unittest.TestCase):
    """대표 예시 7개를 입력 → 추천 → 저장하고, 앱을 새로 열어 대시보드 값을 확인한다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"WORKREQ_DB_PATH": str(Path(self.tmp.name) / "requests.db")})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_input_recommend_save_dashboard(self):
        at = AppTest.from_file(APP_PATH).run()
        for content, *_ in EXAMPLES:
            at.text_area(key="content").input(content)
            at.text_input(key="requester_name").input("김가상")
            at.text_input(key="requester_dept").input("영업팀")
            next(b for b in at.button if b.label == "추천 받기").click().run()
            next(b for b in at.button if b.label == "저장").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(any("저장했습니다" in s.value for s in at.success))
            self.assertEqual(at.text_area(key="content").value, "")

        fresh = AppTest.from_file(APP_PATH).run()
        fresh.sidebar.radio(key="page").set_value("대시보드").run()
        self.assertEqual(fresh.metric[0].value, f"{len(EXAMPLES)}건")
        work_types = dict(zip(fresh.dataframe[0].value["업무유형"], fresh.dataframe[0].value["건수"]))
        self.assertEqual(work_types["IT 지원"], 2)
        self.assertEqual(work_types["시설"], 1)
        departments = dict(zip(fresh.dataframe[2].value["담당부서"], fresh.dataframe[2].value["건수"]))
        self.assertEqual(departments["경영지원팀"], 2)
        self.assertEqual(len(fresh.dataframe[3].value), len(EXAMPLES))


if __name__ == "__main__":
    unittest.main()
