# 프로필 README에 들어가는 내용. 여기만 고치고 `python3 scripts/build.py`를 실행하면
# assets/의 SVG와 README.md가 다시 만들어진다.
# tech 항목: simple-icons 슬러그(scripts/icons.json에 있는 것), "슬러그:보일 이름", 아이콘 없이 글자만 쓰려면 "=이름".

NAME = "김진솔"
ROLE = "Backend Developer"
HOOK = ("다양한 현장을 거쳐,", "문제를 넓게 보는", " 개발자")  # 두 번째 조각이 강조색

# 표지 오른쪽 커밋 기록: (해시, 내용, 점 색: gray / orange / green)
LOG = [
    ("a1f3c2e", "init: 소프트웨어공학 전공", "gray"),
    ("7d2b9e1", "feat: 통역 · 영상 · 3D 실무", "gray"),
    ("c4e8a07", "feat: 업무 자동화 도구", "orange"),
    ("e91f5d3", "feat: 백엔드 · SSAFY 16기", "green"),
]

# 표지 오른쪽 그래프: main에서 갈라졌다 다시 합쳐지는 갈래
BRANCHES = ["소프트웨어공학", "통역 · 번역", "영상 편집", "3D 데이터"]

# 표지 아래 연락처: (이름, 보이는 글자, 주소)
LINKS = [
    ("Email", "soljinkim13@gmail.com", "mailto:soljinkim13@gmail.com"),
    ("Velog", "velog.io/@tongmill_g", "https://velog.io/@tongmill_g/posts"),
]

# 구역 제목: (이름표, 제목)
SECTIONS = {
    "projects": ("프로젝트", "대표 여섯 가지"),
    "more": ("그 밖의 프로젝트", "만들어 본 열 가지"),
    "stack": ("기술 스택", "프로젝트에서 직접 쓴 기술"),
    "activity": ("기록과 활동", "배운 것을 글과 발표로"),
    "grass": ("커밋 기록", "최근 1년"),
}

# 대표 프로젝트. result: (앞, 강조, 뒤)
FEATURED = [
    dict(name="KKIRI", desc="차량 여러 대를 하나로 묶는 실시간 소통 앱", period="2026.10 – 11",
         role="백엔드 전담", team="5인 팀 · 팀장",
         tech=["typescript", "nodedotjs:Node.js", "=WebSocket", "=REST API"],
         result=("세션 상태를 ", "4단계", "로 나눠 통신이 끊겨도 같은 무리로 복귀"),
         repo="https://github.com/OKKIKKI/KKIRI"),
    dict(name="헬스 루틴 편집실", desc="조건과 근거로 답하는 운동 RAG 서비스", period="2026.10",
         role="1인 개발", team="개인 프로젝트",
         tech=["python", "fastapi", "react", "langchain:LangGraph", "=ChromaDB"],
         result=("같은 질문의 응답 시간 ", "80% 단축", " · 17.6초 → 3.6초"),
         repo="https://github.com/soljinkim13/health-routine-studio"),
    dict(name="LocalHub", desc="로그인 없이 쓰는 광주·전라 여행 정보 서비스", period="2026.07",
         role="백엔드", team="3인 팀",
         tech=["python", "fastapi", "sqlite", "openai", "vuedotjs:Vue"],
         result=("장소 검색 · 리뷰 · 여행 챗봇 API를 ", "3일", " 만에 구현"),
         repo="https://github.com/soljinkim13/localhub", demo="https://gwangju-jeolla-nice.netlify.app/"),
    dict(name="빌려가요", desc="공공 대여 방문안을 짜 주는 에이전트", period="2026.11",
         role="1인 개발", team="개인 프로젝트",
         tech=["python", "fastapi", "langchain:LangGraph", "sqlite", "kakao"],
         result=("서초구 대여처 ", "18곳", "을 조건으로 탐색, 품절이면 다시 탐색"),
         repo="https://github.com/soljinkim13/borrow-planner"),
    dict(name="KIC AI Agent", desc="위기 다음 날의 투자 판단을 돕는 에이전트 기획", period="2026.10 – 11",
         role="조사와 기획", team="4인 팀",
         tech=["=사례 조사", "=위기 사건 선정", "=기획서"],
         result=("공식 문서로 시점을 확인한 위기 사건 ", "12건", " 선정")),
    dict(name="업무 자동화", desc="세미나 영상 더빙과 3D 데이터 가공 자동화", period="2024.11 – 2025.07",
         role="1인 개발", team="실무 · 연구소",
         tech=["python", "=Whisper", "elevenlabs", "ffmpeg", "rhinoceros:Rhino"],
         result=("약 일주일 걸리던 더빙을 ", "약 10분", "으로"), orange=True),
]

# 그 밖의 프로젝트 (한 줄 목록)
MORE = [
    dict(name="폰스토리 메이커", desc="폰 스토리 편집기", team="개인", tech=["javascript", "html5", "=IndexedDB", "vercel"], repo="https://github.com/soljinkim13/phone-maker"),
    dict(name="틈 TEUM", desc="여행 일정 추천", team="SSAFY 관통", tech=["openjdk:Java", "spring", "=MyBatis", "mysql"], repo="https://github.com/soljinkim13/teum-enjoytrip"),
    dict(name="맛집기행", desc="맛집 정렬 추천", team="2인 팀 · 화면", tech=["javascript", "nodedotjs:Node.js", "openjdk:Java", "supabase"], repo="https://github.com/soljinkim13/matzip-trip"),
    dict(name="전기충전행", desc="충전소 안내", team="2인 팀 · 충전소", tech=["openjdk:Java", "=Swing", "=OpenAPI"], repo="https://github.com/soljinkim13/ev-charge-trip"),
    dict(name="SSAFY AI Challenge 2", desc="VQA 오답 분석", team="4인 팀 · 분석", tech=["python", "=VLM"]),
    dict(name="Pleos Flow", desc="차량 자동화 앱", team="개인", tech=["kotlin", "jetpackcompose:Compose"], repo="https://github.com/soljinkim13/pleos-flow"),
    dict(name="TripParty", desc="차량용 파티게임", team="개인", tech=["kotlin", "jetpackcompose:Compose"], repo="https://github.com/soljinkim13/trip-party"),
    dict(name="방 지킴이", desc="움직임 감지 알림", team="개인", tech=["=C#", "cplusplus", "mattermost"], repo="https://github.com/soljinkim13/what-you-doin"),
    dict(name="우리집 식재료", desc="식재료 관리 PWA", team="개인", tech=["vuedotjs:Vue", "typescript", "supabase"], repo="https://github.com/soljinkim13/food_manager_plus"),
    dict(name="Pelican", desc="영상 제작 자동화", team="개인", tech=["python", "ffmpeg", "=Remotion"], repo="https://github.com/soljinkim13/auto-pelican"),
]

STACK = [
    ("언어", ["openjdk:Java", "python", "typescript", "javascript", "kotlin"]),
    ("서버", ["spring", "fastapi", "nodedotjs:Node.js", "=WebSocket", "=MyBatis"]),
    ("데이터", ["mysql", "sqlite", "supabase", "=ChromaDB"]),
    ("AI", ["langchain:LangGraph", "openai", "claude", "elevenlabs"]),
    ("화면", ["react", "vuedotjs:Vue", "jetpackcompose:Compose"]),
    ("도구", ["git", "github", "ffmpeg", "vercel"]),
]

# (Feather 아이콘, 앞, 강조)
ACTIVITY = [
    ("pen-tool", "Velog 기술 글 ", "23편"),
    ("code", "알고리즘 풀이 ", "167커밋"),
    ("message-square", "스터디 발표 ", "3회"),
    ("users", "JavaScript 스터디 ", "리더"),
]
CERTS = ["정보처리기사 필기", "ADsP", "OPIc IH", "HSK 6급", "SSAFY 역량테스트 A형"]
