"""요청 저장소. 이 PC의 SQLite 파일(data\\requests.db)에 저장한다."""

import os
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from workreq.criteria import DEPARTMENTS, URGENCIES, WORK_TYPES

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "requests.db"

SAVE_FAILED_MESSAGE = (
    "요청을 저장하지 못했습니다. 잠시 후 다시 저장해 보고, 계속 실패하면 "
    "프로젝트의 data 폴더가 있는지, 다른 프로그램이 requests.db 파일을 열고 있지 않은지 확인해 주세요."
)
LOAD_FAILED_MESSAGE = (
    "저장된 요청을 불러오지 못했습니다. 앱을 다시 실행해 보고, 계속 실패하면 "
    "data\\requests.db 파일이 손상되지 않았는지 확인해 주세요."
)

COLUMNS = ["id", "created_at", "content", "requester_name", "requester_dept",
           "work_type", "urgency", "department", "status"]


class StorageError(Exception):
    pass


def get_db_path():
    return Path(os.environ.get("WORKREQ_DB_PATH", DEFAULT_DB_PATH))


def _connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        _create_table(conn)
    except sqlite3.Error:
        conn.close()
        raise
    return conn


def _create_table(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            content TEXT NOT NULL,
            requester_name TEXT NOT NULL,
            requester_dept TEXT NOT NULL,
            work_type TEXT NOT NULL,
            urgency TEXT NOT NULL,
            department TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT '접수'
        )"""
    )


def validate_classification(work_type, urgency, department):
    """분류값 오류 메시지 목록을 돌려준다."""
    errors = []
    for value, label, allowed in [
        (work_type, "업무유형", WORK_TYPES),
        (urgency, "긴급도", URGENCIES),
        (department, "담당부서", DEPARTMENTS),
    ]:
        if value not in allowed:
            errors.append(f"{label}을(를) 목록에서 선택해 주세요.")
    return errors


def save_request(data, work_type, urgency, department, path=None):
    """검증된 입력과 분류를 저장하고 새 요청 번호를 돌려준다."""
    errors = validate_classification(work_type, urgency, department)
    if errors:
        raise ValueError(" ".join(errors))
    try:
        with closing(_connect(path or get_db_path())) as conn, conn:
            cursor = conn.execute(
                "INSERT INTO requests (created_at, content, requester_name, requester_dept,"
                " work_type, urgency, department) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M"), data.content, data.requester_name,
                 data.requester_dept, work_type, urgency, department),
            )
            return cursor.lastrowid
    except (sqlite3.Error, OSError) as e:
        raise StorageError(SAVE_FAILED_MESSAGE) from e


def list_requests(path=None):
    """저장된 요청을 최신순으로 돌려준다."""
    try:
        with closing(_connect(path or get_db_path())) as conn:
            rows = conn.execute(f"SELECT {', '.join(COLUMNS)} FROM requests ORDER BY id DESC").fetchall()
    except (sqlite3.Error, OSError) as e:
        raise StorageError(LOAD_FAILED_MESSAGE) from e
    return [dict(row) for row in rows]
