import tempfile
import unittest
from pathlib import Path
from unittest import mock

from workreq.models import clean_input
from workreq.storage import StorageError, list_requests, save_request

SAMPLE = clean_input("3층 화장실 세면대에서 물이 샙니다.", "박테스트", "생산팀")


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "sub" / "requests.db"

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_db_returns_empty_list(self):
        self.assertEqual(list_requests(self.db), [])

    def test_save_then_reload(self):
        new_id = save_request(SAMPLE, "시설", "높음", "경영지원팀", path=self.db)
        rows = list_requests(self.db)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["id"], new_id)
        self.assertEqual(row["content"], SAMPLE.content)
        self.assertEqual((row["requester_name"], row["requester_dept"]), ("박테스트", "생산팀"))
        self.assertEqual((row["work_type"], row["urgency"], row["department"]), ("시설", "높음", "경영지원팀"))
        self.assertEqual(row["status"], "접수")

    def test_newest_first(self):
        save_request(SAMPLE, "시설", "높음", "경영지원팀", path=self.db)
        second = save_request(SAMPLE, "구매", "낮음", "경영지원팀", path=self.db)
        self.assertEqual(list_requests(self.db)[0]["id"], second)

    def test_invalid_classification_rejected(self):
        with self.assertRaises(ValueError):
            save_request(SAMPLE, "없는유형", "높음", "경영지원팀", path=self.db)
        with self.assertRaises(ValueError):
            save_request(SAMPLE, "시설", None, "경영지원팀", path=self.db)
        self.assertEqual(list_requests(self.db), [])

    def test_save_failure_raises_storage_error(self):
        with mock.patch("workreq.storage.sqlite3.connect", side_effect=__import__("sqlite3").OperationalError("locked")):
            with self.assertRaises(StorageError) as ctx:
                save_request(SAMPLE, "시설", "높음", "경영지원팀", path=self.db)
        self.assertIn("저장하지 못했습니다", str(ctx.exception))

    def test_load_failure_raises_storage_error(self):
        self.db.parent.mkdir(parents=True)
        self.db.write_text("not a database", encoding="utf-8")
        with self.assertRaises(StorageError):
            list_requests(self.db)


if __name__ == "__main__":
    unittest.main()
