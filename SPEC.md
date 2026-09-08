# Heading 0.4.1 — 규격

## 유지 계약

5개 implicit 제품 스킬, 1개 explicit-only orchestration 스킬, 4개 native child 역할을 유지한다. 기존 27개 mode, METHOD·결과 schema, 182개 mode/intake/dialogue 사례는 변경하지 않았다. intake는 `PROCEED / ASK / REFUSE`이며 `NOT_PROVEN`은 증거 상태다. 선택적 profile 설치는 5 files이고 기본적으로 전역 skill을 복사하지 않는다.

## 모델 요청 계약

정본은 `plugins/heading/skills/heading-orchestrate/references/model-policy.json`이다. 입력 fact는 clarity, scope, reversible, oracle, risk다. 다섯 긍정 조건을 모두 충족할 때만 easy다. risk=critical 또는 risk=material이면서 reversible=false이면 critical, 나머지는 hard다. 모델 선택과 도구 권한은 독립이다.

history에는 현재 outcome의 실패 route·실패 유형·실제 증거 참조를 유지한다. 환경·권한·일시 장애는 `REPAIR_REQUIRED`; 추론 실패는 정책 ladder를 따르며, Luna max와 Astra ultra는 각각의 예산·근거 조건이 필요하다. 소진·예산 미승인은 `NEEDS_NEW_EVIDENCE`다. `REQUESTED`만 호스트 확인 단계로 진행하며, 실패 이력을 지워 반복하지 않는다.

helper는 요청값만 반환한다. effective 값은 null, modelEscalation은 NOT_PROVEN이다. 관찰 비교 함수는 별도로 고정한 taskId·role·sandbox와 model·effort를 비교하지만 출처 인증이나 결과 승인을 하지 않는다. 실제 도구 schema로 모델과 effort를 함께 전달해야 한다.

## 실행·승인

모델 전환 시 역할·sandbox·owned surface·writer 수는 불변이다. 같은 thread에서 필수 설정을 바꿀 수 없다면 정확한 변경본·증거를 checkpoint하고 이전 작성자와 프로세스 종료를 관찰한 뒤 단일 인계한다. 미확인 종료는 새 작성자 허가가 아니다. Reviewer의 보고는 증거이며 최종 승인은 Lead가 소유한다.
