"""Benchmark dataset of 80 Korean prompts for Jev routing evaluation.
Strictly separated into Dev Set (20 cases) and Final Eval Set (60 cases).
"""
import json
from pathlib import Path

BENCHMARK_PROMPTS = [
    # ==========================================
    # DEV SET (20 Prompts) - For development & calibration
    # ==========================================
    {"id": "dev-01", "split": "dev", "prompt": "신규 결제 시스템 구현 전 EARS 기획서 작성 및 태스크 분할", "expected_skill": "tlc-spec-driven", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-02", "split": "dev", "prompt": "모놀리스 결합도 분석 및 Bounded Context 도메인 분리", "expected_skill": "tactical-ddd", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-03", "split": "dev", "prompt": "로그인 페이지 자동 입력 및 화면 캡처 E2E 테스트 작성", "expected_skill": "playwright-skill", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-04", "split": "dev", "prompt": "소스 코드 OWASP Top 10 취약점 및 하드코딩 시크릿 점검", "expected_skill": "security-best-practices", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-05", "split": "dev", "prompt": "피그마 디자인 파일 URL에서 React Tailwind 컴포넌트 변환", "expected_skill": "figma-implement-design", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-06", "split": "dev", "prompt": "작성자!=검증자 원칙으로 PR diff에 대한 독립 교차 코드 리뷰", "expected_skill": "the-judge", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-07", "split": "dev", "prompt": "GitHub Actions CI 빌드 실패 로그 파싱 및 로컬 재현 패치", "expected_skill": "gh-fix-ci", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-08", "split": "dev", "prompt": "웹사이트 LCP와 CLS 지표 분석 및 렌더링 블로킹 리소스 제거", "expected_skill": "core-web-vitals", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-09", "split": "dev", "prompt": "DB를 PostgreSQL에서 DynamoDB로 변경하는 아키텍처 결정(ADR) 문서화", "expected_skill": "create-adr", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-10", "split": "dev", "prompt": "크로스 팀 공통 인증 토큰 도입을 위한 RFC 제안서 작성", "expected_skill": "create-rfc", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-11", "split": "dev", "prompt": "패키지 간 구심/원심 결합도 및 순환 참조(Circular) 의존성 분석", "expected_skill": "coupling-analysis", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-12", "split": "dev", "prompt": "신규 결제 게이트웨이의 STRIDE 위협 모델링 및 데이터 흐름도 분석", "expected_skill": "security-threat-model", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-13", "split": "dev", "prompt": "NestJS 기반 주문/배송 모듈 경계 설정 및 모듈형 모놀리스 설계", "expected_skill": "nestjs-modular-monolith", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-14", "split": "dev", "prompt": "React 컴포넌트의 불필요한 리렌더링 제거 및 useEffect 훅 최적화", "expected_skill": "react-best-practices", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-15", "split": "dev", "prompt": "React Native Expo 앱의 안드로이드 및 iOS 네이티브 권한 분기 처리", "expected_skill": "react-native-expert", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-16", "split": "dev", "prompt": "Lighthouse CLI로 프로덕션 웹사이트 접근성 및 SEO 성능 감사", "expected_skill": "perf-lighthouse", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-17", "split": "dev", "prompt": "Sentry SDK 연동하여 프로덕션 서버 런타임 예외 스택 트레이스 수집", "expected_skill": "sentry", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-18", "split": "dev", "prompt": "Cloudflare Workers와 D1 데이터베이스 엣지 배포 wrangler 설정", "expected_skill": "cloudflare-deploy", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-19", "split": "dev", "prompt": "명세 기반 평가 하네스 구축 및 회귀 테스트 벤치마크 자동 채점", "expected_skill": "spec-driven-eval", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "dev-20", "split": "dev", "prompt": "10년 된 레거시 ERP 시스템의 스트랭글러 피그 현대화 마이그레이션 로드맵", "expected_skill": "legacy-migration-planner", "expected_tier": "Tier 2", "is_negative": False},

    # ==========================================
    # FINAL EVAL SET (60 Prompts) - Unseen Evaluation
    # ==========================================
    # Group A: 20 Positive Target Tasks for Canonical Skills
    {"id": "eval-pos-01", "split": "eval", "prompt": "구독 관리 기능 명세를 EARS 표기법으로 작성하고 체크포인트 분할해줘", "expected_skill": "tlc-spec-driven", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-02", "split": "eval", "prompt": "주문 도메인과 재고 도메인의 강한 결합도를 분석하고 바운디드 컨텍스트 분리해줘", "expected_skill": "tactical-ddd", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-03", "split": "eval", "prompt": "장바구니 담기 후 결제완료까지 브라우저 동작 E2E 시나리오 Playwright로 검증해줘", "expected_skill": "playwright-skill", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-04", "split": "eval", "prompt": "백엔드 API 서버의 SQL Injection 취약점 점검 및 보안 SAST 분석 리포트 생성해줘", "expected_skill": "security-best-practices", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-05", "split": "eval", "prompt": "피그마 디자인 시안의 컬러 팔레트와 버튼 컴포넌트 React 코드로 추출해줘", "expected_skill": "figma-implement-design", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-06", "split": "eval", "prompt": "이번 PR 변경사항에 대해 테스트 통과 여부와 엣지 케이스를 독립 검증자로 채점해줘", "expected_skill": "the-judge", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-07", "split": "eval", "prompt": "GitHub Actions 파이프라인에서 npm test 단계가 깨진 원인을 분석하고 고쳐줘", "expected_skill": "gh-fix-ci", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-08", "split": "eval", "prompt": "모바일 웹 첫 로딩 시 LCP가 4초 이상 걸리는데 렌더링 병목 진단해줘", "expected_skill": "core-web-vitals", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-09", "split": "eval", "prompt": "메시지 큐로 RabbitMQ 대신 Kafka를 도입하기로 한 아키텍처 결정 기록(ADR) 작성해줘", "expected_skill": "create-adr", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-10", "split": "eval", "prompt": "전사 마이크로서비스 간 공통 gRPC 프로토콜 전환을 위한 기술 RFC 문서 작성해줘", "expected_skill": "create-rfc", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-11", "split": "eval", "prompt": "src/services 내부 모듈 간의 원심 결합도(Ce)와 순환 의존성 관계 도출해줘", "expected_skill": "coupling-analysis", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-12", "split": "eval", "prompt": "사용자 개인정보 처리 흐름에서 스푸핑과 정보유출에 대한 STRIDE 위협 모델링해줘", "expected_skill": "security-threat-model", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-13", "split": "eval", "prompt": "NestJS 앱에서 UserModule과 AuthModule 의존성을 분리하고 모듈러 모놀리스로 재구성해줘", "expected_skill": "nestjs-modular-monolith", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-14", "split": "eval", "prompt": "React 컴포넌트에서 useMemo와 useCallback 오용으로 인한 성능 저하 개선해줘", "expected_skill": "react-best-practices", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-15", "split": "eval", "prompt": "Expo Router 기반 React Native 모바일 화면 전환 내비게이션 구현해줘", "expected_skill": "react-native-expert", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-16", "split": "eval", "prompt": "신규 배포된 메인 페이지의 Lighthouse 성능, 웹 접근성, SEO 점수 리포트 뽑아줘", "expected_skill": "perf-lighthouse", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-17", "split": "eval", "prompt": "Next.js 애플리케이션에 Sentry 캡처 연동하고 처리되지 않은 500 에러 추적해줘", "expected_skill": "sentry", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-18", "split": "eval", "prompt": "Cloudflare Pages에 프론트엔드 정적 웹앱 배포하고 커스텀 도메인 바인딩해줘", "expected_skill": "cloudflare-deploy", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-19", "split": "eval", "prompt": "LLM 프롬프트 변경 후 기존 응답 품질이 깨지지 않는지 벤치마크 하네스로 자동 평가해줘", "expected_skill": "spec-driven-eval", "expected_tier": "Tier 2", "is_negative": False},
    {"id": "eval-pos-20", "split": "eval", "prompt": "레거시 자바 스프링 3.0 모놀리스를 단계별로 분해하는 전환 로드맵과 롤백 방안 설계해줘", "expected_skill": "legacy-migration-planner", "expected_tier": "Tier 2", "is_negative": False},

    # Group B: 15 Hard Negative / Veto Cases (Skills must NOT match due to exclusion rules)
    {"id": "eval-neg-01", "split": "eval", "prompt": "README 파일의 오탈자 1글자만 수정하고 커밋해줘 (기획서나 태스크 분할 절대 하지마)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-02", "split": "eval", "prompt": "버튼 배경색 패딩 CSS 2px 늘려줘 (도메인 분리나 DDD 아키텍처 분석 금지)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-03", "split": "eval", "prompt": "백엔드에서 피보나치 수열 구하는 순수 파이썬 알고리즘 함수 작성해줘 (브라우저나 Playwright 쓰지마)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-04", "split": "eval", "prompt": "메인 페이지 폰트 패밀리를 나눔고딕으로 변경해줘 (보안 점검이나 취약점 감사 아님)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-05", "split": "eval", "prompt": "데이터베이스 테이블에 새 컬럼 id bigint 추가하는 마이그레이션 SQL 작성해줘 (피그마 디자인 구현 아님)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-06", "split": "eval", "prompt": "이번 신규 사업 아이디어에 대해 자유롭게 상상하고 브레인스토밍해줘 (코드 리뷰나 채점 루브릭 아님)", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": True},
    {"id": "eval-neg-07", "split": "eval", "prompt": "고객 홍보용 뉴스레터 이메일 마케팅 카피 3가지 버전 작성해줘 (CI 빌드 고치는 작업 아님)", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": True},
    {"id": "eval-neg-08", "split": "eval", "prompt": "PostgreSQL 데이터베이스 슬로우 쿼리 인덱스 튜닝 방안 설명해줘 (프론트엔드 LCP 웹 바이탈 아님)", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": True},
    {"id": "eval-neg-09", "split": "eval", "prompt": "깃 저장소 커밋 메시지 컨벤션 단 1줄 추가해줘 (거창한 아키텍처 결정 ADR 작성 아님)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-10", "split": "eval", "prompt": "프로덕션 긴급 장애 발생으로 방화벽 포트 443 임시 개방 핫픽스 적용 (RFC 제안서 논의할 시간 없음)", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": True},
    {"id": "eval-neg-11", "split": "eval", "prompt": "단순 유틸리티 함수 math.sqrt() 단일 단위 테스트 작성해줘 (전체 결합도 분석 작업 아님)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-12", "split": "eval", "prompt": "파이썬 코드에 black 포매터 돌려서 린트 에러만 정리해줘 (위협 모델링 아님)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},
    {"id": "eval-neg-13", "split": "eval", "prompt": "FastAPI 파이썬 비동기 엔드포인트 1개 만들어줘 (NestJS 프레임워크 아님)", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": True},
    {"id": "eval-neg-14", "split": "eval", "prompt": "Vue 3 Composition API로 ToDo 리스트 컴포넌트 하나 짜줘 (React 패턴 아님)", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": True},
    {"id": "eval-neg-15", "split": "eval", "prompt": "단순 크롬 데스크톱 웹페이지에서 텍스트 복사 버튼 구현해줘 (모바일 React Native 앱 아님)", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": True},

    # Group C: 10 Deterministic Tier 1 Tasks (Math, Regex, Format)
    {"id": "eval-det-01", "split": "eval", "prompt": "1024 * 768 수식 계산해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-02", "split": "eval", "prompt": "이메일 주소 형식 유효성 검사하는 정규표현식(Regex) 작성해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-03", "split": "eval", "prompt": "75 인치를 센티미터(cm)로 단위 변환해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-04", "split": "eval", "prompt": "JSON 문자열 파싱해서 들여쓰기 2칸으로 포맷팅해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-05", "split": "eval", "prompt": "다음 쉼표로 구분된 CSV 문자열을 파이썬 리스트로 변환해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-06", "split": "eval", "prompt": "섭씨 36.5도를 화씨 온도로 변환해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-07", "split": "eval", "prompt": "주어진 문자열에서 모든 특수문자를 제거하는 정규식 작성해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-08", "split": "eval", "prompt": "3의 10제곱을 계산해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-09", "split": "eval", "prompt": "yyyy-mm-dd 날짜 포맷을 Unix Timestamp 초 단위 정수로 변환해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},
    {"id": "eval-det-10", "split": "eval", "prompt": "Base64 인코딩된 문자열 'SGVsbG8=' 디코딩해줘", "expected_skill": None, "expected_tier": "Tier 1", "is_negative": False},

    # Group D: 10 Complex Reasoning / Creative Tasks (Tier 3 Foundation LLM)
    {"id": "eval-reason-01", "split": "eval", "prompt": "인공지능과 자유의지에 관한 철학적 에세이를 3000자로 창작해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-02", "split": "eval", "prompt": "스타트업 B2B SaaS 비즈니스를 위한 글로벌 시장 진출 전략 보고서 작성해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-03", "split": "eval", "prompt": "SF 소설의 주인공 캐릭터 설정과 배경 세계관을 독창적으로 기획해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-04", "split": "eval", "prompt": "투자 유치를 위한 엔젤 투자자 대상 5분 피칭 스피치 원고 작성해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-05", "split": "eval", "prompt": "팀 내 갈등 해결을 위한 비폭력 대화법(NVC) 코칭 시나리오를 작성해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-06", "split": "eval", "prompt": "양자역학의 다세계 해석과 코펜하겐 해석의 본질적 차이를 쉽게 설명해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-07", "split": "eval", "prompt": "고객 불만 대응을 위한 정중하고 공감대 높은 고객지원 답변 서한 작성해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-08", "split": "eval", "prompt": "글로벌 거시경제 인플레이션과 환율 변동이 테크 기업에 미치는 영향 분석해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-09", "split": "eval", "prompt": "신규 모바일 게임의 몰입형 퀘스트 스토리라인과 NPC 대사집 창작해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-reason-10", "split": "eval", "prompt": "직장인을 위한 번아웃 예방 및 주간 회복 루틴 플랜을 설계해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},

    # Group E: 5 Vision / Multimodal OCR Tasks (Tier 3 Vision LLM)
    {"id": "eval-vis-01", "split": "eval", "prompt": "첨부된 기하학 도형 그림에서 삼각형 각도 A의 크기를 판독해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-vis-02", "split": "eval", "prompt": "손글씨로 구겨진 영수증 사진에서 결제 총액과 품목명 OCR 인식해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-vis-03", "split": "eval", "prompt": "전기 전자 회로도 다이어그램 이미지에서 저항 R1과 커패시터 C2 연결 관계 판독해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-vis-04", "split": "eval", "prompt": "흐릿하게 스캔된 고문서 한자 이미지에서 본문 문장 추출해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False},
    {"id": "eval-vis-05", "split": "eval", "prompt": "스마트폰으로 촬영한 수기 설문지 체크박스 표시 결과 판독해줘", "expected_skill": None, "expected_tier": "Tier 3", "is_negative": False}
]

if __name__ == "__main__":
    out_path = Path(__file__).parent / "benchmark_80.json"
    out_path.write_text(json.dumps(BENCHMARK_PROMPTS, ensure_ascii=False, indent=2), encoding="utf-8")
    dev_cnt = sum(1 for p in BENCHMARK_PROMPTS if p["split"] == "dev")
    eval_cnt = sum(1 for p in BENCHMARK_PROMPTS if p["split"] == "eval")
    print(f"Total benchmark prompts: {len(BENCHMARK_PROMPTS)} (Dev: {dev_cnt}, Eval: {eval_cnt})")
    print(f"Saved to: {out_path}")
