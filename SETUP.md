# 설치 및 실행 안내 (Windows 10 + VS Code)

## 처음 한 번만: 설치
1. VS Code에서 `파일 > 폴더 열기`로 이 프로젝트 폴더를 연다.
2. 위쪽 메뉴 `터미널 > 새 터미널`을 누른다. 아래쪽에 명령 입력창이 열린다.
3. 아래 명령을 한 줄씩 입력하고 Enter를 누른다.

```powershell
python --version
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

- `python --version`: Python 3.13 이상이 표시되어야 한다. 오류가 나면 python.org에서 Python을 설치하고 설치 화면의 "Add python.exe to PATH"를 체크한다.
- `python -m venv .venv`: 이 프로젝트 전용 라이브러리 보관 폴더(가상 환경)를 만든다.
- 세 번째 명령: 필요한 라이브러리를 인터넷(PyPI, 파이썬 공식 라이브러리 저장소)에서 내려받는다. 회사 데이터는 전송되지 않는다.

## 앱 실행
```powershell
.venv\Scripts\python -m streamlit run app.py
```
- 터미널에 `URL: http://localhost:8501`이 나오면 웹 브라우저 주소창에 `http://localhost:8501`을 입력한다. (첫 실행 시 이메일 입력으로 멈추는 문제를 막기 위해 브라우저 자동 열기는 꺼 두었다.)
- 이 PC에서만 접속할 수 있다. 다른 사람이 접속하는 방식은 아직 정하지 않았다(확인 필요).
- 종료하려면 터미널을 클릭하고 `Ctrl + C`를 누른다.

## 사용 방법
1. 왼쪽 메뉴 **요청 입력**: 요청 내용, 요청자 이름, 소속 부서를 쓰고 **추천 받기**를 누른다.
2. 추천된 업무유형·긴급도·담당부서와 근거를 확인한다. 틀리면 목록에서 바꾸고 **저장**을 누른다.
3. 왼쪽 메뉴 **대시보드**: 건수 요약과 최근 요청 10건을 본다.

## 데이터 위치와 백업
- 저장한 요청은 프로젝트 폴더 안 `data\requests.db` 파일에 있다. 첫 저장 때 자동으로 만들어진다.
- 백업: 앱을 끈 뒤 `data\requests.db` 파일을 다른 폴더(예: USB, 개인 백업 폴더)로 복사한다. 복원은 그 파일을 다시 `data` 폴더에 덮어쓴다.
- 이 파일을 지우면 저장한 요청이 모두 사라진다.

## 테스트 실행
```powershell
.venv\Scripts\python -m unittest discover -s tests -v
```
- 마지막 줄에 `OK`가 나오면 모든 테스트가 통과한 것이다.

## 사용 중인 라이브러리
| 이름 | 버전 | 용도 | 라이선스/비용 | 외부 연결 |
|---|---|---|---|---|
| streamlit | 1.65.0 | 웹 화면 | Apache-2.0, 무료 | 설치 시에만 인터넷 사용. 사용 통계 전송은 꺼 둠 |
