# Heading 0.3.3

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

## 역할

```text
Lead       GPT-5.6 Sol medium 기본; 중요한 판정은 high
Planner    GPT-5.6 Luna xhigh 기본; 중요한 위험은 지원 시 max
Executor   GPT-5.6 Luna xhigh 기본; 중요한 위험은 지원 시 max
Reviewer   GPT-5.6 Terra high 기본; 중요한 위험은 지원 시 GPT-5.6 Sol
Architect  GPT-5.6 Terra xhigh; 중요한 위험은 지원 시 GPT-5.6 Sol
```

- writable outcome은 한 번에 하나입니다.
- 동일 outcome의 구현·수리·재검증은 같은 Executor thread를 사용합니다. 위임을 사용할 수 없거나, 허용되지 않거나, 작은 로컬 변경에는 과도하면 Lead가 같은 소유권·증거 잠금 아래 선언된 `executionMode: DIRECT`로 직접 수행할 수 있습니다.
- Reviewer는 수정하거나 Executor를 직접 지휘하지 않고 Lead에게만 보고합니다.
- Luna/Terra 사용 비율은 고정하지 않습니다.
- 중요한 위험에서는 Lead가 role·sandbox·소유 표면·writer 수·Reviewer 독립성을 바꾸지 않고 더 높은 모델 tier를 명시적으로 요청할 수 있습니다: Luna -> Terra, Terra -> Sol. 치명적·비가역 위험은 지원 시 Sol을 직접 요청할 수 있습니다. task surface가 지원하면 모델·추론 강도 override를 dispatch에 전달합니다. `requestedModel`, `effectiveModel`, `requestedReasoningEffort`, `effectiveReasoningEffort`, `modelEscalationReason`을 기록하고, 불가하면 기본 모델을 유지하며 `modelEscalation: NOT_PROVEN`을 남깁니다.

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

지원 조건: POSIX, Python 3.11 이상. 호환용 프로파일 설치 결과는 5 files이며, 플러그인 skill 폴더를 전역 skill namespace에 복사하지 않습니다.

이 절은 별도의 로컬 `heading` 런타임 프로파일을 의도적으로 사용할 때만 적용합니다. 플러그인 스킬 설치·검색·암시 호출에는 필요하지 않습니다.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh
./scripts/install.sh --check

codex --profile heading
```

이 프로파일은 작업 단계의 런타임 선택지이며 플러그인 배포 방식이 아닙니다. 플러그인 사용자는 설치할 필요가 없습니다. 다섯 제품 스킬은 설치된 플러그인만으로 동작합니다. 설치기는 비파괴 방식입니다. 기존 파일이나 네임스페이스를 삭제하지 않습니다. `--install-legacy-skills`는 명시적인 호환용 탈출구일 뿐이며, 같은 이름의 설치된 플러그인을 가릴 수 있으므로 일반 플러그인 배포에는 사용하지 않습니다.

Heading은 실행 증거를 내부 판단에 사용하지만, 답변 길이는 작업에 맞춥니다. 단순한 일은 짧게, 복잡하거나 위험한 일은 판단에 필요한 증거까지 설명합니다. 원시 결과 필드가 필요하면 요청하면 됩니다.

스킬별 최적 사용법은 [PLAYBOOK.ko.md](PLAYBOOK.ko.md)에 있습니다.

## 위임 경계

`$heading-orchestrate`는 다섯 트랙 중 하나가 outcome과 증명을 잠근 뒤에만 사용합니다. direct 작업, 관측된 native 역할, 사용자가 승인한 user-visible task 세 경로만 사용합니다. 사용자가 요구한 모델·역할·reviewer·쓰기 경계·task surface를 조용히 대체하지 않으며, 런타임 사실이 없으면 완료로 바꾸지 않고 `NOT_PROVEN`으로 남깁니다. 사용자가 그 위임 경로를 필수로 요구하지 않았다면, 선택적 위임 경로가 없다는 사실만으로 범위가 잠긴 직접 작업을 막지 않습니다.

## 배포 경계

배포 가능한 source는 `plugins/heading/`입니다. 여섯 skill, reference, portable manifest, Codex manifest만 포함합니다. `plugin.json`은 portable Agent Plugins manifest이고 `.codex-plugin/plugin.json`은 Codex manifest입니다. 둘은 같은 `heading` 이름과 버전을 가지며, skill 경로 `./skills/`는 Codex manifest에만 있습니다. 별도 `runtime/heading/`에는 선택적 profile과 role template이 있습니다. repository marketplace는 로컬·팀 테스트용이고, public directory 제출은 별도의 게시자 심사 단계입니다. 선택적 profile 설치기는 사용자가 선택한 Codex profile에만 쓰며 플러그인을 대체하지 않습니다.

`./verify-source-package.sh`는 결정적인 source package와 두 manifest 계약을 검증합니다. `scripts/smoke-plugin-install.py`는 격리된 Codex home에서 로컬 marketplace 등록, 설치, enabled 상태, cache manifest 동등성을 별도로 검증합니다. 확률적인 암시 선택은 새 interactive chat에서만 관측할 수 있습니다. Native Codex 실행, 모델 동작, 인증이 필요한 evaluation, public directory 승인 여부는 별도 증거입니다.
