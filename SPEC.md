# Heading 0.5.0 — 규격

## 유지 계약

5개 implicit 제품 스킬, 1개 explicit-only orchestration 스킬, 4개 native child 역할을 유지한다. 기존 27개 mode, METHOD·결과 schema, 182개 mode/intake/dialogue 사례는 변경하지 않았다. intake는 `PROCEED / ASK / REFUSE`이며 `NOT_PROVEN`은 증거 상태다. 선택적 profile 설치는 5 files이고 기본적으로 전역 skill을 복사하지 않는다.

## 모델 요청 계약

정본은 `plugins/heading/skills/heading-orchestrate/references/model-policy.json`이다. 입력 fact는 clarity, scope, reversible, oracle, risk, shape이며 모두 필수다. shape는 deterministic, fixed-extraction, read-heavy-exploration, implementation, cross-boundary-decision, unknown 중 하나다. deterministic은 모델 요청 없이 `DIRECT_TOOLS`, fixed-extraction은 Luna high, read-heavy-exploration은 local·strong oracle이면 Luna high, 그 외는 Terra medium과 evidence capsule, implementation은 Terra medium, decision/unknown은 Astra low로 시작한다. risk=critical 또는 risk=material이면서 reversible=false이면 Astra high이 우선한다. 모델 선택과 도구 권한은 독립이다.

history에는 현재 outcome의 실패 route·실패 유형·실제 증거 참조를 유지한다. 환경·권한·일시 장애는 `REPAIR_REQUIRED`; Luna 추출 실패는 Terra로, Terra 실패는 Astra로 이동하며 critical high 하한을 유지한다. 자동 승격은 실패 두 번에서 멈춘다. `astraEffort`·`effortReason`·`effortEvidence`로 high/xhigh를 처음부터 요청할 수 있다. Astra max는 `maxBudgetAuthorized`, ultra는 `allowUltra`·`ultraReason`·`ultraBudgetAuthorized`와 host 지원이 필요하다. 소진·예산 미승인은 `NEEDS_NEW_EVIDENCE`다. `REQUESTED`만 호스트 확인 단계로 진행하며, 실패 이력을 지워 반복하지 않는다.

`specialistEffort`·`effortReason`·`effortEvidence`로 선택된 Luna의 high/xhigh/max 또는 Terra의 medium/high를 지정한다. Luna max는 추가 승인 없이 허용된다. Astra 전용 입력과 혼용하거나 모델·위험 하한을 바꿀 수 없다. 과거 low 경로는 실패 이력과 명시적 비교 대조군으로만 유지한다.

helper는 요청값만 반환한다. 출력 `riskBand`는 `ROUTINE`·`CRITICAL`·`QUALIFICATION-REQUIRED` 중 하나이며 task shape를 대체하지 않는다. 모델 route의 effective 값은 null이고 modelEscalation은 NOT_PROVEN이다. deterministic 결과는 모델 route가 아니므로 modelEscalation은 NOT_APPLICABLE이다. 관찰 비교 함수는 별도로 고정한 taskId·role·sandbox와 model·effort를 비교하지만 출처 인증이나 결과 승인을 하지 않는다. 실제 도구 schema로 모델과 effort를 함께 전달해야 한다.

## 실행·승인

모델 전환 시 역할·sandbox·owned surface·writer 수는 불변이다. 같은 thread에서 필수 설정을 바꿀 수 없다면 정확한 변경본·증거를 checkpoint하고 이전 작성자와 프로세스 종료를 관찰한 뒤 단일 인계한다. 미확인 종료는 새 작성자 허가가 아니다. Reviewer의 보고는 증거이며 최종 승인은 Lead가 소유한다.
