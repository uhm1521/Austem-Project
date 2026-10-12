"""요청 입력값의 정리와 검증."""

from dataclasses import dataclass

MAX_CONTENT_LENGTH = 2000
MAX_NAME_LENGTH = 50
MAX_DEPT_LENGTH = 50


@dataclass(frozen=True)
class RequestInput:
    content: str
    requester_name: str
    requester_dept: str


def clean_input(content, requester_name, requester_dept):
    """앞뒤 공백을 지운 입력값을 만든다. 값이 없으면 빈 문자열로 본다."""
    return RequestInput(
        content=(content or "").strip(),
        requester_name=(requester_name or "").strip(),
        requester_dept=(requester_dept or "").strip(),
    )


def validate_input(data):
    """입력값 오류 메시지 목록을 돌려준다. 빈 목록이면 정상이다."""
    errors = []
    fields = [
        (data.content, "요청 내용", MAX_CONTENT_LENGTH),
        (data.requester_name, "요청자 이름", MAX_NAME_LENGTH),
        (data.requester_dept, "요청자 소속 부서", MAX_DEPT_LENGTH),
    ]
    for value, label, max_length in fields:
        if not value:
            errors.append(f"{label}을(를) 입력해 주세요.")
        elif len(value) > max_length:
            errors.append(
                f"{label}은(는) {max_length}자 이하로 줄여 주세요. (현재 {len(value)}자)"
            )
    return errors
