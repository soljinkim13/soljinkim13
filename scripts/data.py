# 프로필 README 그림에 들어가는 내용. 여기만 고치고 `python3 scripts/build.py`를 실행하면 assets/의 SVG가 다시 만들어진다.
# tech 항목: simple-icons 슬러그(scripts/icons.json에 있는 것) 또는 아이콘 없는 글자만 쓰려면 "=이름".

NAME = "김진솔"
NAME_EN = "Jinsol Kim"
ROLE = "Backend Developer"
HOOK = ("다양한 현장을 거쳐,", "문제를 넓게 보는", " 개발자")

# 표지 아래 연락처 배지: (설명, shields 배지 글자, 로고, 주소)
LINKS = [
    ("Email", "Email-soljinkim13@gmail.com-2F8050", "gmail", "mailto:soljinkim13@gmail.com"),
    ("Velog", "Velog-tongmill__g-2F8050", "velog", "https://velog.io/@tongmill_g/posts"),
]

# 표지 오른쪽 그래프: 서로 다른 현장이 하나로 합쳐지는 모양
BRANCHES = ["소프트웨어공학", "통역 · 번역", "영상 편집", "3D 데이터"]

JOURNEY = [
    ("2018.09", "Beihang University", "소프트웨어공학 · 베이징"),
    ("2023.06", "졸업 논문", "LLM 주제 · 중국어로 작성"),
    ("2024.11", "한국치과임플란트연구소", "통역 · 영상 · 3D 자동화"),
    ("2026.07", "삼성청년SW·AI아카데미", "16기 · Java 백엔드"),
]

# 대표 프로젝트 (큰 카드)
FEATURED = [
    dict(name="KKIRI", tag="SERVER", period="2026.10 – 11",
         desc="여러 차와 동승자를 한 무리로 잇는 차량 앱",
         role="팀장 · 백엔드 전담", team="5인 팀",
         metric=("4단계", "끊겨도 이어지는 세션 상태"),
         tech=["typescript", "nodedotjs", "=WebSocket", "=REST API"],
         link="https://github.com/OKKIKKI/KKIRI"),
    dict(name="헬스 루틴 편집실", tag="AI · RAG", period="2026.10",
         desc="조건은 코드로, 설명은 문서 검색으로 답하는 운동 RAG",
         role="1인 개발", team="개인",
         metric=("−80%", "응답 17.6초 → 3.6초"),
         tech=["python", "fastapi", "react", "langchain:LangGraph", "=ChromaDB"]),
    dict(name="LocalHub", tag="WEB API", period="2026.07",
         desc="로그인 없이 쓰는 광주·전라 여행 정보 서비스",
         role="백엔드", team="3인 팀",
         metric=("3일", "검색 · 리뷰 · 챗봇 API 완성"),
         tech=["python", "fastapi", "sqlite", "openai", "vuedotjs:Vue"],
         link="https://gwangju-jeolla-nice.netlify.app/"),
    dict(name="빌려가요", tag="AI AGENT", period="2026.11",
         desc="휠체어·공구 공공 대여 방문안을 짜 주는 에이전트",
         role="1인 개발", team="개인",
         metric=("18곳", "서초구 대여처를 조건으로 탐색"),
         tech=["python", "fastapi", "langchain:LangGraph", "sqlite", "kakao"]),
    dict(name="KIC AI Agent", tag="PLANNING", period="2026.10 – 11",
         desc="위기 다음 날의 자산 배분 판단을 돕는 에이전트 기획",
         role="조사 · 공동 기획", team="4인 팀",
         metric=("12건", "공식 문서로 검증한 위기 사건"),
         tech=["=사례 조사", "=위기 사건 선정", "=기획서"]),
    dict(name="업무 자동화", tag="AUTOMATION", period="2024.11 – 2025.07",
         desc="세미나 영상 더빙과 3D 데이터 가공을 한 번에",
         role="실무 · 1인 개발", team="연구소",
         metric=("1주 → 10분", "2시간 세미나 중국어 더빙"),
         tech=["python", "=Whisper", "elevenlabs", "ffmpeg", "rhinoceros:Rhino"],
         orange=True),
]

# 그 밖의 프로젝트 (작은 카드)
MORE = [
    dict(name="폰스토리 메이커", tag="WEB", period="2026.11",
         desc="메시지·단서·엔딩을 잇는 휴대폰 스토리 편집기",
         role="기획 · 개발", team="개인",
         tech=["javascript", "html5", "=IndexedDB", "vercel"],
         link="https://phone-maker.vercel.app/editor/"),
    dict(name="틈 TEUM", tag="WEB", period="2026.11",
         desc="취향과 귀가 시간으로 짜는 여행 일정 추천",
         role="풀스택", team="SSAFY 관통",
         tech=["openjdk:Java", "spring", "=MyBatis", "mysql"]),
    dict(name="맛집기행", tag="WEB", period="2026.10",
         desc="음식점을 모아 한 번에 정렬해 추천하는 서비스",
         role="화면 전반", team="2인 팀",
         tech=["javascript", "nodedotjs", "openjdk:Java", "supabase"]),
    dict(name="전기충전행", tag="DESKTOP", period="2026.07",
         desc="관광지 주변 충전소를 거리순으로 보여 주는 앱",
         role="충전소 · 화면", team="2인 팀",
         tech=["openjdk:Java", "=Swing", "=OpenAPI"]),
    dict(name="SSAFY AI Challenge 2", tag="AI", period="2026.09",
         desc="이미지 질의응답 모델의 오답 229건 분석",
         role="오답 분석", team="4인 팀",
         tech=["python", "=VLM", "=프롬프트"]),
    dict(name="Pleos Flow", tag="ANDROID", period="2026.11",
         desc="트리거 → 조건 → 동작으로 만드는 차량 자동화",
         role="1인 개발", team="개인",
         tech=["kotlin", "jetpackcompose:Compose", "android"]),
    dict(name="TripParty", tag="ANDROID", period="2026.11",
         desc="정차 중에 일행과 즐기는 차량용 파티게임",
         role="1인 개발", team="개인",
         tech=["kotlin", "jetpackcompose:Compose", "android"]),
    dict(name="방 지킴이", tag="DESKTOP", period="2026.11",
         desc="움직임과 소리를 감지해 Mattermost로 알림",
         role="1인 개발", team="개인",
         tech=["=C#", "cplusplus", "dotnet", "mattermost"]),
    dict(name="우리집 식재료", tag="PWA", period="2026.08",
         desc="오프라인에서도 쓰는 가족 식재료 관리 앱",
         role="1인 개발", team="개인",
         tech=["vuedotjs:Vue", "typescript", "supabase", "pwa"]),
    dict(name="Pelican", tag="AUTOMATION", period="2026.11",
         desc="유튜브 롱폼 영상 제작을 돕는 자동화 도구",
         role="1인 개발", team="개인",
         tech=["python", "ffmpeg", "=Remotion", "nodedotjs"]),
]

STACK = [
    ("LANGUAGE", "언어", ["openjdk:Java", "python", "typescript", "javascript", "kotlin"]),
    ("BACKEND", "서버", ["spring", "fastapi", "nodedotjs:Node.js", "=WebSocket", "=MyBatis"]),
    ("DATA", "데이터", ["mysql", "sqlite", "supabase", "=ChromaDB"]),
    ("AI", "AI", ["langchain:LangGraph", "openai", "claude", "elevenlabs"]),
    ("FRONT · APP", "화면", ["react", "vuedotjs:Vue", "vite", "jetpackcompose:Compose"]),
    ("TOOLS", "도구", ["git", "github", "ffmpeg", "vercel"]),
]

STATS = [
    ("23편", "Velog 기술 글"),
    ("167", "알고리즘 풀이 커밋"),
    ("3회", "스터디 발표"),
    (f"{len(FEATURED) + len(MORE)}개", "만든 프로젝트"),
]
CERTS = ["정보처리기사 필기", "ADsP", "OPIc IH", "HSK 6급", "SSAFY 역량테스트 A형"]

SECTIONS = {
    "journey": ("걸어온 길", "git log --graph"),
    "projects": ("대표 프로젝트", "git branch --list featured/*"),
    "more": ("그 밖의 프로젝트", "git branch --all"),
    "stack": ("기술 스택", "cat stack.json"),
    "activity": ("기록과 활동", "git shortlog -sn"),
    "grass": ("커밋 기록", "git log --since=1.year"),
}
