# ADR-0001: 역할과 모델 능력 분리

상태: ACCEPTED FOR SOURCE; native qualification pending. 날짜: 2026-09-07.

## 맥락

기존 role 파일의 고정 model/effort는 공식 custom-agent precedence에 따라 task dispatch보다 우선했다. role과 모델 능력이 결합되어 사용자 요구인 어려운 작업=Astra, 쉬운 작업=Luna를 정확히 표현할 수 없었다.

## 결정

역할 파일에는 역할·sandbox·행동 계약만 남긴다. Lead가 실제 task facts로 버전 정책에서 route를 선택하고 호스트 호출에 model+effort를 함께 지정한다. 요청과 관찰을 별도 기록한다. Astra low는 복잡성 기본, Luna xhigh는 다섯 조건을 모두 만족하는 쉬운 작업 기본, critical은 Astra high다. max는 실패·예산·탐색 조건이 있을 때만 사용한다.

## 대안

role별 고정 모델은 거부했다. Astra/Luna별로 role을 복제하면 같은 권한의 복수 소유자가 생기고 유지비가 늘어난다. 모든 작업 Astra max도 비용·시간 최적성을 증명하지 못한다. 현재 세션 모델을 프롬프트 문장만으로 바꾸었다고 간주하는 방식은 실제 제어가 아니므로 거부했다.

## 결과와 한계

공개 스킬 이름·역할 이름·권한·트랙 METHOD는 유지한다. 같은 thread의 모델 변경이 불가능할 때는 관찰된 종료 후 동일 outcome을 단일 인계한다. 이 규칙은 안전한 수리 연속성을 보존하지만 native 실행 검증이 필요하다. 공식 모델 지원은 특정 계정에서의 제공이나 Heading 성능 최적성을 증명하지 않는다.

근거: [공식 자료 분석](../../plugins/heading/skills/heading-orchestrate/references/RESEARCH-2026-09-07.md), [라우팅 프로토콜](../../plugins/heading/skills/heading-orchestrate/references/MODEL-ROUTING.md).
