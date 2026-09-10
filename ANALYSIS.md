# Heading — 0.5.0 근거 기반 변경 분석

## 결론

고정 계층형 위임 대신, 작업 형태와 증거 경계를 먼저 고정하는 closed work-shape router가 적합하다. Terra의 읽기 중심 탐색과 Luna의 좁고 반복 가능한 작업, Terra의 명확한 구현, Astra의 경계 판단을 분리하되 실제 성능 우열은 주장하지 않는다.

## 관찰된 문제

- 이전 분류는 작업 형태보다 단순 난이도 라벨에 의존해 route 근거와 재현성을 약화시켰다.
- 읽기 중심 병렬 탐색은 원시 context를 확장하거나 write ownership을 혼합할 위험이 있었다.
- profile installer와 native evaluation의 별도 global-skill 복사는 plugin distribution boundary를 흐렸다.
- Ultra 예외의 예산 승인이 문서적 설명에 머물고 request schema에서 확인되지 않았다.

## 변경

- 모든 packet에 `shape`와 닫힌 fact schema를 요구한다.
- route는 deterministic/direct, fixed-extraction/Luna high, bounded-read/Luna high, broad-read/Terra medium, implementation/Terra medium, decision/Astra low, critical/Astra high으로 분리한다.
- read-heavy scout는 승인된 한 개를 기본으로 하며 독립 질문일 때만 최대 두 개이고 bounded evidence capsule만 반환한다.
- Ultra는 `allowUltra`, task-specific reason, `ultraBudgetAuthorized`, native host support를 모두 요구한다.
- optional profile installer와 native evaluation 모두 plugin package를 distribution source로 사용하고 global skill copy를 하지 않는다.

## 남은 불확실성

[UNVERIFIED] 현재 계정과 host가 후보 model/effort request를 실제로 적용하는지. [UNVERIFIED] 이 route가 accepted outcome당 비용·지연·품질에서 최선인지. 결정적 validation과 공식 문서 조회는 이 둘을 증명하지 않는다.
