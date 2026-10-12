"""키워드 규칙 추천. PC 안에서만 동작하며 외부로 아무것도 보내지 않는다.

나중에 다른 추천 방식(PC 설치형 AI 등)으로 바꿀 때는 같은 형태의
Recommendation을 돌려주는 함수를 만들어 recommend 대신 쓰면 된다.
"""

from dataclasses import dataclass, field

from workreq.criteria import DEPARTMENT_BY_WORK_TYPE, WORK_TYPES

WORK_TYPE_KEYWORDS = {
    "IT 지원": ["노트북", "컴퓨터", "pc", "모니터", "인터넷", "네트워크", "와이파이", "계정",
              "비밀번호", "이메일", "프로그램", "소프트웨어", "프린터", "전산", "로그인",
              "키보드", "마우스"],
    "시설": ["화장실", "세면대", "누수", "샙니다", "물이새", "에어컨", "난방", "냉방", "조명",
           "전등", "형광등", "엘리베이터", "주차", "청소"],
    "구매": ["구매", "구입", "주문", "토너", "비품", "소모품", "사무용품", "견적", "발주", "여분"],
    "회계·경비": ["법인카드", "정산", "경비", "영수증", "비용처리", "세금계산서", "출장비", "지출",
              "예산"],
    "인사": ["연차", "휴가", "급여", "월급", "입사", "퇴사", "채용", "재직증명서", "근태", "휴직"],
    "계약·법무": ["계약", "법무", "서명", "날인", "약관", "소송", "법률", "비밀유지"],
}

# 위에서부터 차례로 확인한다. 낮음의 부정 표현("급하지 않")을 먼저 본다.
URGENCY_KEYWORDS = [
    ("낮음", ["급하지않", "천천히", "여유", "시간될때", "여분", "확인하고싶"]),
    ("높음", ["긴급", "급히", "급합니다", "급해", "당장", "오늘", "내일", "오후", "되지않",
            "안됩니다", "안돼", "고장", "샙니다", "누수", "멈췄"]),
    ("보통", ["이번주", "다음주", "마감", "주중"]),
]


@dataclass
class Recommendation:
    work_type: str | None = None
    urgency: str | None = None
    department: str | None = None
    reasons: list[str] = field(default_factory=list)


def _normalize(text):
    return "".join((text or "").split()).lower()


def recommend(content):
    """요청 내용으로 업무유형·긴급도·담당부서를 추천한다. 못 찾은 항목은 None이다."""
    text = _normalize(content)
    result = Recommendation()

    best_score = 0
    for work_type in WORK_TYPES:
        matched = [k for k in WORK_TYPE_KEYWORDS[work_type] if k in text]
        if len(matched) > best_score:
            best_score = len(matched)
            result.work_type = work_type
            best_matched = matched
    if result.work_type:
        words = ", ".join(f"'{k}'" for k in best_matched)
        result.reasons.append(f"{words} → 업무유형 {result.work_type}")
        result.department = DEPARTMENT_BY_WORK_TYPE[result.work_type]
        result.reasons.append(f"업무유형 {result.work_type} → 담당부서 {result.department}")

    for urgency, keywords in URGENCY_KEYWORDS:
        matched = next((k for k in keywords if k in text), None)
        if matched:
            result.urgency = urgency
            result.reasons.append(f"'{matched}' → 긴급도 {urgency}")
            break

    return result
