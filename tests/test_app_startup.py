import tomllib
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


class AppStartupTest(unittest.TestCase):
    def test_app_runs_and_shows_title(self):
        at = AppTest.from_file(str(ROOT / "app.py")).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.title[0].value, "업무 요청 분류 관리")


class ConfigTest(unittest.TestCase):
    def setUp(self):
        with open(ROOT / ".streamlit" / "config.toml", "rb") as f:
            self.config = tomllib.load(f)

    def test_usage_stats_disabled(self):
        self.assertIs(self.config["browser"]["gatherUsageStats"], False)

    def test_local_only_access(self):
        self.assertEqual(self.config["server"]["address"], "localhost")

    def test_headless_to_skip_email_prompt(self):
        self.assertIs(self.config["server"]["headless"], True)


class RequirementsTest(unittest.TestCase):
    def test_streamlit_version_pinned(self):
        lines = (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        self.assertIn("streamlit==1.65.0", [line.strip() for line in lines])


if __name__ == "__main__":
    unittest.main()
