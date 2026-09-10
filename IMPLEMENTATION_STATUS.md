# Heading 0.5.0 — 구현 상태와 인계

기준일: 2026-09-10. source 기준: `d7561c5` 이후 0.5.0 clean-break 변경.

| 항목 | 상태 | 확인 위치 |
| --- | --- | --- |
| work-shape 필수 라우팅 | 구현됨 | `model_routing.py`, 고정 routing 사례 |
| Luna/Terra/Astra 후보 route | 구현됨 | `model-policy.json` |
| bounded evidence capsule | 구현됨 | `evidence_capsule.py`, `EVIDENCE-CAPSULE.md` |
| 독립 scout 상한 | 구현됨 | 기본 1개, 독립 질문 2개 상한; fork none |
| Luna high/xhigh/max, Terra medium/high 및 Astra 예외 | 구현됨 | 작업 근거, 위험 하한, 예외 예산, host gate |
| global skill 복사 제거 | 구현됨 | profile installer와 native eval runner |
| role 우선순위 충돌 제거 | 구현됨 | runtime role TOML에 model/effort 없음 |
| 결정적 source 검증 | PASS: 63 tests, 17 vectors | `verify-source-package.sh` |
| native 모델 route·host 지원 | `NOT_PROVEN` | 실제 Codex host metadata 필요 |
| 비용·품질 최적성 | `NOT_PROVEN` | 동일 조건 benchmark 미실행 |

이 소스는 모델 호출 서비스를 구현하지 않는다. 스킬은 Lead에게 packet, host 확인, 관찰 프로토콜을 지시하고 helper는 요청만 계산한다. 실제 model/effort 적용은 지원되는 host에서 별도로 증명해야 한다.

다음 담당자는 candidate revision, policy version, requested/effective model·effort, task ID, role, sandbox, host version, acceptance oracle, 실패 로그를 함께 기록한다. `route-benchmark-plan.json`의 사전 약속을 만족하기 전 실사용 경로를 검증 완료라고 표시하지 않는다.
