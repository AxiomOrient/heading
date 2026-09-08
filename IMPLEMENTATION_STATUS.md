# Heading 0.4.1 — 구현 상태와 인계

기준일: 2026-09-08. source 기준: 0.4.0 / `94c0920` → 0.4.1.

| 항목 | 상태 | 확인 위치 |
| --- | --- | --- |
| 5개 제품 스킬의 작업별 라우팅 | 구현됨 | 각 SKILL의 Roles and continuity |
| 공식 모델·effort 정책 | 구현됨 | model-policy.json |
| 순수 라우팅·고정 실패 상태 | 구현됨 | model_routing.py |
| role 우선순위 충돌 제거 | 구현됨 | runtime/heading/agents/*.toml |
| Lead 초기 Astra low 요청 | 구현됨 | heading.config.toml |
| native eval 후보 route·실패 로그 | 구현됨 | scripts/run-evals.py |
| 결정적 검증 결과 | 별도 기록 | VALIDATION.md |
| 사용자 설치·계정 모델 변경 | 수행하지 않음 | source ZIP만 변경 |
| native 모델·승급·writer 인계 실행 | NOT_PROVEN | Codex CLI 부재 |
| 비용·성능 최적성 | NOT_PROVEN | 인증된 동일 작업 평가 없음 |

이 소스는 모델 호출 서비스를 구현하지 않는다. 스킬은 Lead에게 선택·호스트 확인·관찰 프로토콜을 지시하고 helper는 요청 계산만 수행한다. 실제 모델 적용은 지원되는 호스트에서 확인해야 한다.

다음 담당자는 README의 비파괴 staging 절차로 기존 role model 키 유무부터 비교한다. 활성 작성자를 중지하지 않은 채 role 파일을 교체하지 않는다. 정책 ID, model/effort 요청과 관찰값, 도구 버전, task ID, candidate revision, 실패 로그를 함께 기록한다. PLAN의 native gate를 통과하기 전 실사용 경로가 검증 완료라고 표시하지 않는다.
