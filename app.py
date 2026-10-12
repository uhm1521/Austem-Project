import streamlit as st

from workreq.criteria import DEPARTMENTS, URGENCIES, URGENCY_DESCRIPTIONS, WORK_TYPES
from workreq.dashboard import summarize
from workreq.models import (
    MAX_CONTENT_LENGTH,
    MAX_DEPT_LENGTH,
    MAX_NAME_LENGTH,
    clean_input,
    validate_input,
)
from workreq.recommender import Recommendation, recommend
from workreq.storage import StorageError, list_requests, save_request, validate_classification

APP_TITLE = "업무 요청 분류 관리"
PAGES = ["요청 입력", "대시보드"]
SENSITIVE_INFO_NOTICE = "주민등록번호, 연락처, 계좌번호 등 민감정보는 입력하지 마세요."
INPUT_KEYS = ["content", "requester_name", "requester_dept"]
SELECT_FIELDS = [
    ("sel_work_type", "업무유형", WORK_TYPES),
    ("sel_urgency", "긴급도", URGENCIES),
    ("sel_department", "담당부서", DEPARTMENTS),
]


def start_review(data):
    """입력값으로 추천을 받아 검토 단계로 넘어간다."""
    try:
        rec = recommend(data.content)
        failed = False
    except Exception:
        rec = Recommendation()
        failed = True
    st.session_state["draft"] = {"input": data, "reasons": rec.reasons, "failed": failed}
    st.session_state["sel_work_type"] = rec.work_type
    st.session_state["sel_urgency"] = rec.urgency
    st.session_state["sel_department"] = rec.department


def show_review(draft):
    data = draft["input"]
    st.subheader("추천 확인")
    st.write(f"**요청 내용:** {data.content}")
    st.write(f"**요청자:** {data.requester_name} / {data.requester_dept}")

    if draft["failed"]:
        st.warning("추천 중 오류가 발생했습니다. 아래 목록에서 직접 선택해 주세요.")
    elif draft["reasons"]:
        st.caption("추천 근거: " + " · ".join(draft["reasons"]))
    missing = [label for key, label, _ in SELECT_FIELDS if st.session_state.get(key) is None]
    if missing and not draft["failed"]:
        st.warning(f"{', '.join(missing)}은(는) 추천하지 못했습니다. 목록에서 직접 선택해 주세요.")

    for key, label, options in SELECT_FIELDS:
        st.selectbox(
            label, options, key=key, index=None, placeholder="선택하세요",
            format_func=(lambda u: f"{u} ({URGENCY_DESCRIPTIONS[u]})") if key == "sel_urgency" else str,
        )

    col_save, col_cancel = st.columns(2)
    if col_save.button("저장", type="primary"):
        values = [st.session_state[key] for key, _, _ in SELECT_FIELDS]
        errors = validate_classification(*values)
        if errors:
            for message in errors:
                st.error(message)
            return
        try:
            request_id = save_request(data, *values)
        except StorageError as e:
            st.error(str(e))
            return
        finish(f"요청 #{request_id}을(를) 저장했습니다.")
    if col_cancel.button("다시 입력"):
        finish(None)


def finish(message):
    """검토 단계를 끝내고 입력 화면을 비운다."""
    for key in ["draft"] + INPUT_KEYS:
        st.session_state.pop(key, None)
    st.session_state["flash"] = message
    st.rerun()


def show_input_page():
    st.header("요청 입력")
    if st.session_state.get("flash"):
        st.success(st.session_state.pop("flash"))
    st.caption(SENSITIVE_INFO_NOTICE)
    with st.form("request_form"):
        content = st.text_area("요청 내용", max_chars=MAX_CONTENT_LENGTH, key="content")
        requester_name = st.text_input("요청자 이름", max_chars=MAX_NAME_LENGTH, key="requester_name")
        requester_dept = st.text_input("요청자 소속 부서", max_chars=MAX_DEPT_LENGTH, key="requester_dept")
        submitted = st.form_submit_button("추천 받기")

    if submitted:
        data = clean_input(content, requester_name, requester_dept)
        errors = validate_input(data)
        if errors:
            st.session_state.pop("draft", None)
            for message in errors:
                st.error(message)
        else:
            start_review(data)

    if "draft" in st.session_state:
        show_review(st.session_state["draft"])


def show_dashboard_page():
    st.header("대시보드")
    try:
        rows = list_requests()
    except StorageError as e:
        st.error(str(e))
        return
    summary = summarize(rows)
    st.metric("전체 요청", f"{summary['total']}건")
    if not rows:
        st.info("저장된 요청이 없습니다. '요청 입력' 메뉴에서 요청을 저장해 주세요.")
        return

    for col, (key, label) in zip(st.columns(3), [("work_type", "업무유형"), ("urgency", "긴급도"), ("department", "담당부서")]):
        col.subheader(f"{label}별")
        col.dataframe(
            [{label: name, "건수": count} for name, count in summary[key].items()],
            hide_index=True, width="stretch",
        )

    st.subheader("최근 요청")
    st.dataframe(
        [{"번호": r["id"], "등록일시": r["created_at"], "요청 내용": r["content"],
          "요청자": f"{r['requester_name']} / {r['requester_dept']}", "업무유형": r["work_type"],
          "긴급도": r["urgency"], "담당부서": r["department"]} for r in summary["recent"]],
        hide_index=True, width="stretch",
    )


st.set_page_config(page_title=APP_TITLE)
st.title(APP_TITLE)
page = st.sidebar.radio("메뉴", PAGES, key="page")

if page == "요청 입력":
    show_input_page()
else:
    show_dashboard_page()
