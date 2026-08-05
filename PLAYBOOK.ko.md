# Heading 스킬별 최적 사용법

## 공통

가장 좋은 요청은 **스킬 + 원하는 결과 + 절대 바꾸면 안 되는 조건 하나**입니다.

```text
$heading-<track> <원하는 결과>. <핵심 제약>.
```

긴 양식은 필요 없습니다. 트랙을 잘못 골라도 Heading이 작업 전에 자동 보정합니다.

## Prototype

**사용:** 무엇을 만들지 아직 결정하지 못했을 때.

```text
$heading-prototype 이 동기화 방식이 사용자의 신뢰를 높이는지 검증해. 실제 데이터는 쓰지 마.
```

모드: `desirability`, `workflow`, `feasibility`, `viability`, `generative-quality`

최적 흐름: 가장 위험한 가정 하나 → 가장 싼 가역 probe → 대표 입력·과업 관찰 → `ADOPT | REJECT | ITERATE | INCONCLUSIVE`.

피할 것: 완성도 높은 데모 자체를 성공으로 간주하기, 합성 증거를 실제 사용자 증거처럼 표현하기, 좋은 출력만 선택하기.

## Build

**사용:** 제품 의미는 결정됐고 실제 동작·통합·배포를 완성해야 할 때.

```text
$heading-build 승인된 파일 동기화 기능을 실제 iOS 진입점부터 영속 저장과 복구까지 완성해. 기존 데이터는 보존해.
```

모드: `product-slice`, `library-api`, `service`, `adapter`, `data-change`, `delivery-infra`

최적 흐름: 실제 entry 추적 → 가장 작은 완전한 vertical slice → 적용되는 위험만 hardening → 실제 target 또는 권위 있는 fixture로 증명.

피할 것: disconnected scaffold, mock-only proof, 성공 응답 stub, 검증하지 않은 production-ready 주장.

## Sweep

**사용:** 제품 의미를 바꾸지 않고 삭제·통합·리팩터링·UI 단순화·성능 개선을 할 때.

```text
$heading-sweep 공개 API와 오류 의미는 유지하고 중복 상태와 wrapper를 제거해.
```

모드: `delete`, `collapse`, `refactor`, `ui`, `performance`

최적 흐름: 보존 oracle과 기준선 확보 → 한 seam만 변경 → 같은 입력으로 전후 비교 → 복잡도가 실제로 줄었을 때만 유지.

피할 것: 테스트 삭제, 오류 숨김, 측정 없는 최적화, 복잡도를 다른 계층으로 이동하기.

## Grow

**사용:** 출시된 제품과 데이터가 있고 사용자·제품 결과를 측정하며 개선할 때.

```text
$heading-grow 신규 사용자의 첫 작업 성공률을 높여. D7 유지율은 가드레일로 보존해.
```

모드: `randomized`, `sequential`, `switchback`, `holdout-rollout`, `observational`

최적 흐름: 가설 하나 + primary metric 하나 → 계측·노출·데이터 품질 확인 → 작은 treatment → 사전 판정 규칙으로 `KEEP | ROLLBACK | ITERATE | NOT_PROVEN`.

피할 것: 지표 조작, 사후 segment 선택, 다크패턴, 관측 자료로 인과를 단정하기.

## Maintain

**사용:** 기존 시스템의 장애·결함·보안·용량·계획 변경·데이터 복구를 다룰 때.

```text
$heading-maintain 간헐적 데이터 유실을 재현하고 복구해. 데이터 보존이 최우선이야.
```

모드: `incident`, `defect`, `security`, `reliability-capacity`, `planned-change`, `data-repair`

최적 흐름: 영향 확인 → 활성 피해 격리 → 원인 경계 수정 → 복구·회귀 검증 → 변경 후 관측.

피할 것: 로그 삭제, 인증 우회, 백업 없는 데이터 수정, 중단 기준 없는 production chaos.

## 잘못된 방법을 요청했을 때

Heading은 가능한 한 목표를 유지합니다.

```text
"테스트를 지워서 통과시켜"  → 테스트를 지우지 않고 원인을 수정
"성공 숫자를 만들어"        → 실제 측정 설계로 전환
"인증을 꺼서 해결해"         → 승인된 최소 권한·격리·복구 경로 사용
"대상 도구가 없어"           → 가능한 구현과 정적 검증은 수행, 해당 증거만 NOT_PROVEN
```

목표 자체가 기만·무단 접근·증거 파괴이고 안전한 대체 목표를 거부할 때만 `REFUSE`합니다.
