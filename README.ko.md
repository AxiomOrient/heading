# Heading 0.1.0

Heading은 제품 작업을 다섯 방향으로 나누는 명시적 Codex 스킬입니다.

```text
$heading-prototype  무엇을 만들지 결정
$heading-build      결정된 동작을 제품으로 완성
$heading-sweep      동작을 보존하며 복잡도 제거
$heading-grow       출시된 변경의 제품 효과 측정
$heading-maintain   기존 시스템의 위험·장애·변경 통제
```

## 사용법

한 줄이면 충분합니다.

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
Lead       GPT-5.6 Sol high    라우팅·범위·통합·최종 판정
Planner    GPT-5.6 Luna max    읽기 전용 탐색·리서치·계획
Executor   GPT-5.6 Luna max    유일한 제품 writer
Reviewer   GPT-5.6 Terra high  독립 read-only 리뷰
Architect  GPT-5.6 Terra xhigh 비국소 경계 자문
```

- writable outcome은 한 번에 하나입니다.
- 동일 outcome의 구현·수리·재검증은 같은 Executor thread를 사용합니다.
- Reviewer는 수정하거나 Executor를 직접 지휘하지 않고 Lead에게만 보고합니다.
- Luna/Terra 사용 비율은 고정하지 않습니다.

## 설치

지원 조건: POSIX, Python 3.11 이상. 설치 결과는 20 files입니다.

```bash
./verify-source-package.sh

./scripts/install.sh --dry-run
./scripts/install.sh
./scripts/install.sh --check

codex --profile heading
```

설치기는 비파괴 방식입니다. 기존 파일이나 네임스페이스를 삭제하지 않으며, Heading 네임스페이스 충돌이 있으면 먼저 정리한 뒤 설치해야 합니다.

Heading은 실행 증거를 내부 판단에 사용하지만, 답변 길이는 작업에 맞춥니다. 단순한 일은 짧게, 복잡하거나 위험한 일은 판단에 필요한 증거까지 설명합니다. 원시 결과 필드가 필요하면 요청하면 됩니다.

스킬별 최적 사용법은 [PLAYBOOK.ko.md](PLAYBOOK.ko.md)에 있습니다.

## 배포 경계

배포 가능한 source는 다섯 스킬, reference, tests, 설치기와 검증 스크립트입니다.
설치기는 호출자가 선택한 Codex profile에 파일을 쓰며, 기존 namespace를 조용히
교체하거나 runtime binary를 패키징하지 않습니다. `./verify-source-package.sh`는
결정적인 source package를 검증합니다. Native Codex 실행, 모델 동작, 인증이 필요한
evaluation은 별도 증거이며 source 검증만으로 입증되지 않습니다.
