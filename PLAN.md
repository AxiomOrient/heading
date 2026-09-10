# Heading — 남은 검증과 정책 개선

## P0. 실제 host route 확인

지원되는 Codex host에서 계정의 model/effort catalog와 실제 tool schema를 먼저 관찰한다. model과 effort를 함께 요청하고 task ID·role·sandbox·candidate revision·requested/effective 값을 대조한다. profile 이름, prompt, 모델 자기소개는 증거가 아니다. host 지원이나 관찰이 없으면 `NOT_PROVEN`으로 남긴다.

## P0. plugin 기반 native intake 평가

`scripts/run-evals.py`는 격리된 local marketplace에서 플러그인을 설치한 뒤 intake만 평가한다. 동일 source revision과 schema를 사용한다.

```bash
python3 -B scripts/run-evals.py --dry-run --limit 1 --route luna-high
python3 -B scripts/run-evals.py --dry-run --limit 1 --route terra-high
python3 -B scripts/run-evals.py --dry-run --limit 1 --route terra-medium
python3 -B scripts/run-evals.py --dry-run --limit 1 --route astra-low
```

인증된 실행은 사용자가 명시적으로 제공한 credential로만 수행한다. runner의 trace와 stderr를 보존하고 requested 값으로 effective 값을 채우지 않는다. intake 성공은 구현 성능이나 route 최적성의 증거가 아니다.

## P1. 사전 약속된 route 비교

| work shape | 비교 후보 | 수락 기준 |
| --- | --- | --- |
| fixed extraction | Luna low(대조군) / high / xhigh / max | 동일 input·oracle·재작업·독립 검토 |
| read-heavy exploration | Luna high / xhigh / Terra medium / high / Astra low | capsule 품질·source coverage·시간·token·review |
| implementation | Terra medium / high / Astra low / high | 실제 회귀·수락률·재작업·독립 검토 |

Astra 판단은 low/medium/high/xhigh를 같은 문제에서 비교하고, 첫 시도 성공률과 재시도를 포함한 최종 수락 비용을 따로 측정한다.

실행 전 base revision, tools, acceptance oracle, budget, 표본 수, 허용 편차, 중단 규칙을 고정한다. 실패·blocked·재시도·review finding을 분모에서 제거하지 않는다. `route-benchmark-plan.json`의 required fields를 모두 남긴다.

## P2. 정책 변경 원칙

공식 계약과 host 지원 범위 안에서 후보 정책을 변경할 수 있지만, 같은 조건의 benchmark 없이 최적이라고 승격하지 않는다. 모델 설명이나 단일 성공 사례만으로 승격하지 않는다. 정책·routing cases·문서·검증 digest를 한 revision에서 함께 갱신한다.
