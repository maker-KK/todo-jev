# JEV 설정

주인님 지시가 있을 때만 수정. jev 훅 실행 시 세션 첫 작업에서 한 번 읽는다.

- report: on   # on = "JEV: ..." 한 줄 보고 / off = 조용히 적용
- applyThreshold: 70   # 최고 매칭률이 이 이상이면 적용 (%)
- skipThreshold: 40    # 전부 이 미만이면 적용 안 함 (%)
- comboGap: 20         # 2위가 1위와 이 %p 이내로 근접하면 함께 적용
- maxSkills: 2         # 동시 적용 최대 개수
