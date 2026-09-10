# Heading 0.5.0

Heading은 다섯 제품 작업 트랙과 선택적 오케스트레이션 트랙을 제공하는 이식 가능한 skills 플러그인입니다.

```text
$heading-prototype  무엇을 만들지 결정
$heading-build      결정된 동작을 제품으로 완성
$heading-sweep      동작을 보존하며 복잡도 제거
$heading-grow       출시된 변경의 제품 효과 측정
$heading-maintain   기존 시스템의 위험·장애·변경 통제
$heading-orchestrate 잠긴 outcome을 관측 가능한 위임으로 조율
```

## 사용법

한 줄이면 충분합니다.

다섯 제품 트랙(`prototype`, `build`, `sweep`, `grow`, `maintain`)은 암시 호출 대상입니다. 자연어로 작업을 설명하면 Codex가 설명문을 바탕으로 맞는 트랙을 선택할 수 있습니다. `$heading-…`로 시작 트랙을 명시할 수 있지만, 요청과 증거가 다른 트랙을 가리키면 Heading이 계속 자동 보정합니다. `$heading-orchestrate`는 outcome과 증명이 잠긴 뒤에만 유효한 위임이므로 의도적으로 명시 호출 전용입니다.

```text
$heading-prototype 이 기능이 필요한지 검증해
$heading-build 첨부 프로젝트를 배포 가능하게 완성해
$heading-sweep 현재 동작은 유지하고 최대한 단순화해
$heading-grow 첫 작업 성공률을 높여
$heading-maintain 간헐적 데이터 유실을 안전하게 고쳐
```

결과를 좌우하는 제약 하나를 함께 주면 더 정확합니다.

```text
$heading-sweep 공개 API는 유지하고 내부 구조만 단순화해
```

## 잘못 고른 트랙

호출한 스킬은 **힌트**입니다. 실제 트랙은 작업 전에 요청과 증거로 판정합니다.

```text
$heading-build 이 아이디어를 사람들이 원하는지 검증해
```

위 요청은 같은 대화에서 자동으로 `prototype`으로 보정해 진행합니다. 사용자가 다시 호출하거나 새 세션을 만들 필요가 없습니다. 트랙은 보정 후 현재 outcome에만 잠깁니다.

## 기본 동작

- `PROCEED`가 기본입니다. 누락값은 저장소·첨부·테스트·로그·기존 결정과 보수적인 기본값으로 채웁니다.
- 이상하거나 불가능한 표현은 가장 가까운 검증 가능한 목표로 정규화합니다.
- 방법만 잘못됐다면 그 방법만 버리고 안전하고 정직한 방법으로 계속합니다.
- `ASK`는 결과를 실제로 바꾸는 선택을 증거로 해결할 수 없을 때 질문 하나만 합니다.
- `REFUSE`는 목표 자체에 안전하고 승인된 정직한 형태가 없을 때만 사용합니다.
- 도구·플랫폼이 없으면 가능한 작업은 계속하고 해당 증거만 `NOT_PROVEN`으로 남깁니다. 모든 유용한 작업이 불가능할 때만 실행 결과가 `BLOCKED`가 될 수 있습니다.

## 역할과 작업별 모델

**역할은 권한을, 작업의 증거는 모델을 결정합니다.** 선택적 Lead 프로파일은 호스트 호환성이 확인된 GPT-5.6 Luna를 low effort로 사용하고, 하위 작업 기본값으로 Luna high를 제공합니다. 스킬을 읽는 것만으로 현재 채팅의 모델이 바뀌지는 않습니다.

| 작업 형태 | 후보 요청 |
| --- | --- |
| 결정적인 사전 점검 또는 기계적 검사 | direct 도구; 모델 요청 없음 |
| 강한 oracle이 있는 고정 추출 | GPT-5.6 Luna `high` |
| 범위가 좁고 검증 가능한 탐색 / 넓거나 검증 기준이 약한 탐색 | Luna `high` / Terra `medium`; evidence capsule 필수 |
| 강한 oracle이 있는 명확한 구현 | GPT-5.6 Terra `medium` |
| 여러 경계의 판단 또는 형태 미확정 | GPT-6 Astra `low` |
| 치명적 위험 또는 비가역·고영향 작업 | Astra `high` |

Luna는 high 기본에 xhigh/max를, Terra는 medium 기본에 high를 처음부터 선택할 수 있습니다. Luna max는 이미 승인되어 추가 허락이 필요 없습니다. Sol은 활성 라우팅에서 제외합니다. 복잡한 판단은 `astraEffort`, `effortReason`, `effortEvidence`로 첫 시도부터 `high`·`xhigh`를 선택할 수 있습니다. 저비용 경로의 실패를 먼저 요구하지 않습니다. Astra `max`·`ultra`는 예외 예산 계약과 호스트 지원이 필요합니다. 선택적 프로파일은 호스트 호환성이 확인된 GPT-5.6 Luna를 low effort로 사용하고, 하위 모델 Luna high와 동시 하위 작업 최대 두 개를 요청합니다. 기존 세션은 바꾸지 않습니다.

0.5.0의 모든 패킷은 작업 `shape`를 선언하고 현재의 닫힌 패킷 schema를 사용합니다. 비교 평가 계획에는 현재 route key만 넣습니다. 이 설정은 **후보 기본 정책**입니다. 실측된 최적값이나 서로 다른 모델의 성능 동등성을 주장하지 않습니다. UI의 `Light`는 `low`에 대응합니다. 정확한 모델 ID와 허용 effort는 [버전 정책](plugins/heading/skills/heading-orchestrate/references/model-policy.json)을 사용합니다.

Lead는 승인과 최종 판단, Planner·Reviewer·Architect는 읽기 전용, Executor는 유일한 위임 작성자를 맡습니다. Reviewer는 실제 변경을 독립적으로 검토하고 Lead에게만 보고합니다. 역할 파일에서는 모델·추론 강도를 제거했습니다. 최신 Codex에서 이 값이 호출 시 설정보다 우선하기 때문입니다. dispatch는 두 값을 함께 전달하고 요청값과 실제 호스트 관찰값을 분리합니다. 미관찰은 `modelEscalation: NOT_PROVEN`이며 전환 성공이 아닙니다. 결정적 direct 작업은 숨은 모델 호출이 아니라 `NOT_APPLICABLE`입니다.

같은 outcome의 수리는 가능한 한 같은 Executor를 유지합니다. 필수 모델 변경을 같은 thread에 적용할 수 없다면 변경본·증거를 보존하고, 기존 작성자와 소유 프로세스의 종료를 관찰한 뒤 작성자 하나에게 인계합니다. 선택적 위임이 없으면 별도로 선언한 direct 경로를 사용할 수 있지만, 필수 모델·권한·검토를 조용히 대체하지 않습니다.

정확한 도구 조회는 직접 실행하고, 해석이 필요한 조사는 승인된 scout 하나를 기본으로 사용합니다. 독립 질문일 때만 최대 둘을 사용합니다. `fork_turns="none"`과 필요한 근거만 담은 패킷으로 전체 대화 상속을 줄입니다. 각 scout는 원시 context·쓰기 권한·최종 판단 대신 제한된 [evidence capsule](plugins/heading/skills/heading-orchestrate/references/EVIDENCE-CAPSULE.md)을 반환합니다.

[라우팅·작업 패킷](plugins/heading/skills/heading-orchestrate/references/MODEL-ROUTING.md), [2026-09-10 공식 자료 분석](plugins/heading/skills/heading-orchestrate/references/RESEARCH-2026-09-10.md), [미실행 비교 평가 계획](evals/route-benchmark-plan.json)을 참고합니다.

## 플러그인 설치

주 배포물은 `plugins/heading/` 플러그인입니다. Agent Plugins 표준의 `plugin.json`과 Codex의 `.codex-plugin/plugin.json`이 같은 여섯 skill 폴더를 가리킵니다.

```bash
./verify-source-package.sh
python3 -B scripts/smoke-plugin-install.py

codex plugin marketplace add /absolute/path/to/heading
codex plugin add heading@heading
codex plugin list --json
```

Git 저장소에서는 로컬 경로 대신 `AxiomOrient/heading --ref main`을 사용합니다. repo marketplace를 추가한 뒤 데스크톱 앱을 재시작하고 **Heading Plugins**에서 **Heading**을 설치합니다. marketplace 파일은 `.agents/plugins/marketplace.json`이며 저장소 루트 기준 `./plugins/heading`을 가리킵니다.

## 선택적 실행 프로파일

지원 조건: POSIX, Python 3.11 이상. 선택적 프로파일 설치 결과는 5 files이며, 플러그인 skill 폴더를 전역 skill namespace에 복사하지 않습니다.

이 절은 별도의 로컬 `heading` 런타임 프로파일을 의도적으로 사용할 때만 적용합니다. 플러그인 스킬 설치·검색·암시 호출에는 필요하지 않습니다.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh
./scripts/install.sh --check

codex --profile heading
```

이 프로파일은 작업 단계의 런타임 선택지이며 플러그인 배포 방식이 아닙니다. 플러그인 사용자는 설치할 필요가 없습니다. 다섯 제품 스킬은 설치된 플러그인만으로 동작합니다. 설치기는 비파괴 방식이며 기존 파일이나 네임스페이스를 삭제하지 않습니다. 0.5.0은 skill 폴더를 두 번째 전역 namespace로 복사하지 않습니다.

Heading은 실행 증거를 내부 판단에 사용하지만, 답변 길이는 작업에 맞춥니다. 단순한 일은 짧게, 복잡하거나 위험한 일은 판단에 필요한 증거까지 설명합니다. 원시 결과 필드가 필요하면 요청하면 됩니다.

스킬별 최적 사용법은 [PLAYBOOK.ko.md](PLAYBOOK.ko.md)에 있습니다.

## 위임 경계

`$heading-orchestrate`는 다섯 트랙 중 하나가 outcome과 증명을 잠근 뒤에만 사용합니다. direct 작업, 관측된 native 역할, 사용자가 승인한 user-visible task 세 경로만 사용합니다. 사용자가 요구한 모델·역할·reviewer·쓰기 경계·task surface를 조용히 대체하지 않으며, 런타임 사실이 없으면 완료로 바꾸지 않고 `NOT_PROVEN`으로 남깁니다. 사용자가 그 위임 경로를 필수로 요구하지 않았다면, 선택적 위임 경로가 없다는 사실만으로 범위가 잠긴 직접 작업을 막지 않습니다.

## 배포 경계

배포 가능한 source는 `plugins/heading/`입니다. 여섯 skill, reference, 결정적 라우팅 helper, portable manifest, Codex manifest를 포함합니다. `plugin.json`은 portable Agent Plugins manifest이고 `.codex-plugin/plugin.json`은 Codex manifest입니다. 둘은 같은 `heading` 기본 릴리스를 가리키며 skill 경로 `./skills/`는 Codex manifest에만 있습니다. 로컬 Codex cachebuster는 portable 릴리스를 바꾸지 않고 Codex manifest에만 `+codex.*` suffix를 더할 수 있습니다. 별도 `runtime/heading/`에는 선택적 profile과 role template이 있습니다. repository marketplace는 로컬·팀 테스트용이고, public directory 제출은 별도의 게시자 심사 단계입니다. 선택적 profile 설치기는 사용자가 선택한 Codex profile에만 쓰며 플러그인을 대체하지 않습니다.

`./verify-source-package.sh`는 결정적인 source package와 두 manifest 계약을 검증합니다. `scripts/smoke-plugin-install.py`는 격리된 Codex home에서 로컬 marketplace 등록, 설치, enabled 상태, cache manifest 동등성을 별도로 검증합니다. 확률적인 암시 선택은 새 interactive chat에서만 관측할 수 있습니다. Native Codex 실행, 모델 동작, 인증이 필요한 evaluation, public directory 승인 여부는 별도 증거입니다.

## 기존 설치의 업데이트

이 ZIP은 소스를 고도화한 결과입니다. 사용자 계정이나 실제 설치를 변경하지 않았습니다. 비파괴 설치기는 내용이 다른 기존 관리 파일을 덮어쓰지 않고 거부합니다. 기존 profile과 role 파일을 백업하고 새 경로에 staging한 뒤 비교하십시오. 실행 중인 작성자를 종료하고 사용자 수정사항을 보존하면서 검토한 관리 파일만 교체해야 합니다. Codex home 전체를 삭제하지 않습니다. 이전 role 파일의 모델 키가 남으면 작업별 라우팅을 방해합니다.

```bash
# STAGE는 소스 폴더 밖의 새 경로로 지정합니다.
STAGE="$(mktemp -d)"
./scripts/install.sh --dry-run --codex-home "$STAGE/codex"
./scripts/install.sh --codex-home "$STAGE/codex"
./scripts/install.sh --check --codex-home "$STAGE/codex"
```

staging 경로를 실제 사용자 경로로 자동 승격하지 않습니다. 플러그인 설치와 선택적 profile 설치는 별개입니다.

## Canonical documents

- [Identity and evolution](IDENTITY_AND_EVOLUTION.md): identity, invariants and permitted change.
- [Specification](SPEC.md) · [Architecture](ARCHITECTURE.md): contracts and authoritative owners.
- [Analysis](ANALYSIS.md) · [Implementation status](IMPLEMENTATION_STATUS.md): observed defects, changes and remaining proof.
- [Validation](VALIDATION.md) · [Plan](PLAN.md) · [Routing decision](docs/adr/0001-task-based-model-routing.md).
