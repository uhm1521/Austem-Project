import unittest

from workreq.criteria import DEPARTMENTS, URGENCIES, WORK_TYPES
from workreq.recommender import recommend

# PRD.md `대표 요청 예시` (가상 데이터)
EXAMPLES = [
    ("회의실 노트북이 인터넷에 연결되지 않습니다. 오후 회의 전에 봐주세요.", "IT 지원", "높음", "전산팀"),
    ("다음 주 월요일 신규 입사자가 옵니다. 사내 계정과 PC를 준비해 주세요.", "IT 지원", "보통", "전산팀"),
    ("3층 화장실 세면대에서 물이 샙니다.", "시설", "높음", "경영지원팀"),
    ("복합기 토너가 거의 떨어졌습니다. 여분 구매 부탁드립니다.", "구매", "낮음", "경영지원팀"),
    ("지난달 법인카드 사용분 정산 마감일이 언제인가요?", "회계·경비", "보통", "재경팀"),
    ("제 남은 연차 일수를 확인하고 싶습니다.", "인사", "낮음", "인사팀"),
    ("거래처 계약서를 내일 서명해야 하는데, 오늘 중 검토 부탁드립니다.", "계약·법무", "높음", "영업팀"),
]


class RecommendTest(unittest.TestCase):
    def test_representative_examples(self):
        for content, work_type, urgency, department in EXAMPLES:
            with self.subTest(content=content):
                r = recommend(content)
                self.assertEqual((r.work_type, r.urgency, r.department), (work_type, urgency, department))

    def test_values_are_in_criteria(self):
        for content, *_ in EXAMPLES:
            r = recommend(content)
            self.assertIn(r.work_type, WORK_TYPES)
            self.assertIn(r.urgency, URGENCIES)
            self.assertIn(r.department, DEPARTMENTS)

    def test_reasons_show_matched_word(self):
        r = recommend("노트북이 켜지지 않아요")
        self.assertIn("'노트북' → 업무유형 IT 지원", r.reasons)

    def test_no_match_returns_none(self):
        r = recommend("안녕하세요")
        self.assertIsNone(r.work_type)
        self.assertIsNone(r.department)
        self.assertIsNone(r.urgency)
        self.assertEqual(r.reasons, [])

    def test_empty_and_none_input(self):
        self.assertIsNone(recommend("").work_type)
        self.assertIsNone(recommend(None).work_type)

    def test_not_urgent_phrase_is_low(self):
        self.assertEqual(recommend("급하지 않으니 모니터 교체 부탁드립니다").urgency, "낮음")


if __name__ == "__main__":
    unittest.main()
