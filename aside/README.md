# Aside JEV - 자동 스킬 선택기 (Aside 통합)

[To do - Jev](https://github.com/maker-KK/todo-jev) 엔진의 Aside(AI 브라우저 비서) 측 통합입니다.
매 요청을 유형 분류하고 스킬별 매칭률(%)을 계산해 최적의 스킬을 자동 적용하는 Jarvis 스타일 라우터 훅입니다.

## 구성

```
aside/jev/
  SKILL.md                    # 라우터 본체: 유형 분류 + 매칭률 계산 + 적용 규칙
  config.md                   # 설정: 보고 on/off, 임계값
  scripts/
    check-duplicates.mjs      # 설치 전 기존 스킬과의 유사도 검증
    refresh-table.mjs         # 새 스킬 설치 후 라우팅 테이블 자동 갱신
```

## 동작 방식

```
매 작업 시작 (AGENTS.md 훅)
  → 요청 유형 분류
  → 스킬별 매칭률(%) 계산
  → 임계값 이상인 스킬 자동 적용 (config.md 기준)
  → "JEV: 유형=... | <스킬> <n>% → 적용" 한 줄 보고 (report on일 때)
```

- 적용 임계값(기본): 최고 매칭률 70% 이상 적용, 2위가 1위와 20%p 이내면 함께 적용(최대 2개), 전부 40% 미만이면 적용 안 함.
- `config.md`에서 보고 on/off와 임계값을 조절할 수 있습니다.

## 설치

1. Aside 계정 루트의 `skills/user/jev/` 아래로 `aside/jev/` 내용을 복사합니다.
2. 계정 루트의 `AGENTS.md`에 훅 규칙을 추가합니다.

```markdown
## JEV 스킬 라우터 훅 (매 작업 자동 실행)

- 매 작업 시작 시 요청 유형을 분류하고, JEV 라우터(`skills/user/jev/SKILL.md`)로
  사용자 스킬별 매칭률을 계산해 임계값 이상인 스킬을 자동 적용한다.
- 세션 첫 작업에서 jev SKILL.md와 config.md를 한 번 읽어 로직을 기억하고,
  이후 작업은 기억으로 처리한다.
- 새 사용자 스킬 설치 시:
  ① `node skills/user/jev/scripts/check-duplicates.mjs <후보 디렉터리>`로 유사도 검증
  ② 유사도 50% 이상이면 양쪽 본문을 읽어 중복 여부 판단 후 보고
  ③ 설치 후 `node skills/user/jev/scripts/refresh-table.mjs`로 테이블 갱신
```
