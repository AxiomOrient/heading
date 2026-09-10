# ADR-0001: work shape와 역할·모델 능력 분리

상태: ACCEPTED FOR SOURCE; native qualification pending. 날짜: 2026-09-10.

## 맥락

역할의 권한과 모델 능력을 결합하면 동일 outcome에 대한 writer ownership과 route 근거가 흐려진다. 읽기 중심 탐색, 좁은 고정 추출, 구현, 경계 판단은 요구하는 작업 형태와 증거가 다르다. 공식 모델 설명은 후보 선택에 도움이 되지만 계정별 host availability나 Heading 성능 최적성을 증명하지 않는다.

## 결정

역할 파일에는 역할·sandbox·행동 계약만 둔다. Lead가 실제 task facts와 필수 `shape`로 current policy route를 선택하고 host 호출에 model과 effort를 함께 지정한다. deterministic preflight는 direct tools, fixed extraction은 Luna high, read-heavy exploration은 좁은 범위·강한 oracle이면 Luna high, 그 외 Terra medium와 evidence capsule, clear implementation은 Terra medium, cross-boundary decision은 Astra low, critical risk는 Astra high를 요청한다. Ultra는 task-specific reason, `ultraBudgetAuthorized: true`, native host support가 모두 있을 때만 요청한다.

## 결과와 한계

요청값과 host 관찰값은 분리한다. 모델 route는 host metadata가 없으면 `NOT_PROVEN`이고, 한 outcome에는 writer 하나만 둔다. 병렬화는 명시적으로 독립인 read-heavy evidence work에만 제한하며 capsule은 authority나 final acceptance가 아니다. 현재 정책은 candidate이며 [공식 자료 분석](../../plugins/heading/skills/heading-orchestrate/references/RESEARCH-2026-09-10.md)과 [라우팅 프로토콜](../../plugins/heading/skills/heading-orchestrate/references/MODEL-ROUTING.md)에 근거한다.
