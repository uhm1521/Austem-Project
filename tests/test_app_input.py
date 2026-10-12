import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from streamlit.testing.v1 import AppTest

from workreq.storage import list_requests

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "requests.db"
        self.env = mock.patch.dict(os.environ, {"WORKREQ_DB_PATH": str(self.db)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def submit(self, content, name, dept):
        at = AppTest.from_file(APP_PATH).run()
        at.text_area(key="content").input(content)
        at.text_input(key="requester_name").input(name)
        at.text_input(key="requester_dept").input(dept)
        at.button[0].click().run()
        return at


class InputPageTest(AppTestCase):
    def test_shows_sensitive_info_notice(self):
        at = AppTest.from_file(APP_PATH).run()
        self.assertTrue(any("민감정보" in c.value for c in at.caption))

    def test_empty_submit_shows_three_errors(self):
        at = self.submit("", "", "")
        self.assertFalse(at.exception)
        self.assertEqual(len(at.error), 3)
        self.assertEqual(len(at.selectbox), 0)

    def test_missing_name_shows_one_error(self):
        at = self.submit("노트북이 켜지지 않습니다.", "", "영업팀")
        self.assertEqual([e.value for e in at.error], ["요청자 이름을(를) 입력해 주세요."])


class ReviewAndSaveTest(AppTestCase):
    def test_recommendation_prefilled_and_saved(self):
        at = self.submit("3층 화장실 세면대에서 물이 샙니다.", "박테스트", "생산팀")
        self.assertFalse(at.exception)
        self.assertEqual(at.selectbox(key="sel_work_type").value, "시설")
        self.assertEqual(at.selectbox(key="sel_urgency").value, "높음")
        self.assertEqual(at.selectbox(key="sel_department").value, "경영지원팀")
        self.assertTrue(any("추천 근거" in c.value for c in at.caption))

        next(b for b in at.button if b.label == "저장").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("저장했습니다" in s.value for s in at.success))
        rows = list_requests(self.db)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["work_type"], rows[0]["urgency"]), ("시설", "높음"))

    def test_user_can_change_recommendation(self):
        at = self.submit("3층 화장실 세면대에서 물이 샙니다.", "박테스트", "생산팀")
        at.selectbox(key="sel_urgency").select("보통").run()
        next(b for b in at.button if b.label == "저장").click().run()
        self.assertEqual(list_requests(self.db)[0]["urgency"], "보통")

    def test_no_match_requires_manual_selection(self):
        at = self.submit("안녕하세요", "김가상", "영업팀")
        self.assertIsNone(at.selectbox(key="sel_work_type").value)
        self.assertTrue(any("직접 선택" in w.value for w in at.warning))
        next(b for b in at.button if b.label == "저장").click().run()
        self.assertEqual(len(at.error), 3)
        self.assertEqual(list_requests(self.db), [])

        at.selectbox(key="sel_work_type").select("인사")
        at.selectbox(key="sel_urgency").select("낮음")
        at.selectbox(key="sel_department").select("인사팀").run()
        next(b for b in at.button if b.label == "저장").click().run()
        self.assertEqual(list_requests(self.db)[0]["work_type"], "인사")

    def test_recommender_error_falls_back_to_manual(self):
        with mock.patch("workreq.recommender.recommend", side_effect=RuntimeError("boom")):
            at = self.submit("노트북이 켜지지 않습니다.", "김가상", "영업팀")
        self.assertFalse(at.exception)
        self.assertTrue(any("추천 중 오류" in w.value for w in at.warning))
        self.assertIsNone(at.selectbox(key="sel_work_type").value)

    def test_save_failure_shows_message(self):
        at = self.submit("3층 화장실 세면대에서 물이 샙니다.", "박테스트", "생산팀")
        with mock.patch("workreq.storage.sqlite3.connect", side_effect=__import__("sqlite3").OperationalError("locked")):
            next(b for b in at.button if b.label == "저장").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("저장하지 못했습니다" in e.value for e in at.error))


if __name__ == "__main__":
    unittest.main()
