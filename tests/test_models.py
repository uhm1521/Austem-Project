import unittest

from workreq.models import (
    MAX_CONTENT_LENGTH,
    MAX_NAME_LENGTH,
    clean_input,
    validate_input,
)


class CleanInputTest(unittest.TestCase):
    def test_strips_whitespace(self):
        data = clean_input("  노트북 고장  ", " 김가상 ", " 영업팀\n")
        self.assertEqual(data.content, "노트북 고장")
        self.assertEqual(data.requester_name, "김가상")
        self.assertEqual(data.requester_dept, "영업팀")

    def test_none_becomes_empty(self):
        data = clean_input(None, None, None)
        self.assertEqual((data.content, data.requester_name, data.requester_dept), ("", "", ""))


class ValidateInputTest(unittest.TestCase):
    def test_valid_input_has_no_errors(self):
        data = clean_input("3층 화장실 세면대에서 물이 샙니다.", "박테스트", "생산팀")
        self.assertEqual(validate_input(data), [])

    def test_all_missing(self):
        errors = validate_input(clean_input("", "", ""))
        self.assertEqual(len(errors), 3)
        self.assertIn("요청 내용을(를) 입력해 주세요.", errors)
        self.assertIn("요청자 이름을(를) 입력해 주세요.", errors)
        self.assertIn("요청자 소속 부서을(를) 입력해 주세요.", errors)

    def test_whitespace_only_is_missing(self):
        errors = validate_input(clean_input("   ", "김가상", "영업팀"))
        self.assertEqual(errors, ["요청 내용을(를) 입력해 주세요."])

    def test_each_required_field(self):
        self.assertEqual(len(validate_input(clean_input("내용", "", "영업팀"))), 1)
        self.assertEqual(len(validate_input(clean_input("내용", "김가상", ""))), 1)

    def test_too_long_content(self):
        errors = validate_input(clean_input("가" * (MAX_CONTENT_LENGTH + 1), "김가상", "영업팀"))
        self.assertEqual(len(errors), 1)
        self.assertIn(f"{MAX_CONTENT_LENGTH}자 이하", errors[0])

    def test_max_length_is_allowed(self):
        data = clean_input("가" * MAX_CONTENT_LENGTH, "나" * MAX_NAME_LENGTH, "영업팀")
        self.assertEqual(validate_input(data), [])


if __name__ == "__main__":
    unittest.main()
