# Heading — 남은 검증과 정책 개선

## P0. 사용자 호스트에서 실제 route 확인

공식 모델 목록과 설치된 Codex의 실제 버전·tool schema·계정 제공 범위를 확인한다. 현재 role 파일에 model/effort가 남아 있으면 staging diff로 교체 대상을 결정한다. source의 문서보다 실제 호스트 동작이 우선이다.

쉬운 국소 작업 하나는 Luna xhigh, 경계가 있는 작업 하나는 Astra low로 요청한다. 호스트 로그에서 요청값과 관찰값, task ID·role·sandbox를 대조한다. 프로파일 이름이나 모델 자기소개는 증거가 아니다. 모델 전환 불가·effort 미지원·관찰 누락은 NOT_PROVEN으로 남긴다.

## P0. 위임 상태 전이 검증

단일 Executor, read-only Reviewer, 실패 증거 반환, 같은 outcome 수리, 모델 변경 요구, 기존 thread 종료 확인, 변경본 보존, 단일 인계를 실제 수행한다. stale result·종료 미관찰·쓰기 중복은 승인하지 않는다. 호스트가 지원하지 않는 제어 API는 추측해서 호출하지 않는다.

## P1. intake 행동 평가

```bash
python3 -B scripts/run-evals.py --dry-run --limit 1 --route astra-low
# 다음 명령은 인증된 Codex가 있는 사용자의 환경에서만 실행한다.
python3 -B scripts/run-evals.py --suite all --route astra-low --auth-file "$HOME/.codex/auth.json"
python3 -B scripts/run-evals.py --suite all --route luna-xhigh --auth-file "$HOME/.codex/auth.json"
```

각 명령은 결과 경로와 격리된 HOME을 사용한다. 인증은 사용자가 명시적으로 제공하며 저장소에 키를 넣지 않는다. runner의 원본 trace를 보존한다. runner는 관찰 모델을 자동 인증하지 않으며 effective 값은 null로 남는다. 그 값을 별도 호스트 증거 없이 채우지 않는다.

## P1. 구현 outcome 평가

| 작업군 | 비교 후보 | 완료 기준 |
| --- | --- | --- |
| 명확한 국소 변경 | Luna high / xhigh / max | 동일 oracle·회귀·수리 횟수 |
| 소유권·상태·복구 문제 | Astra low / medium / high | 실제 실패 재현·근본 수정·독립 검토 |
| 비가역 고영향 | Astra high / xhigh, 승인된 max | 승인 경계·복구·오류 거부 |

Luna high는 비교 baseline일 뿐 배포 기본 route가 아니다. `--route`는 정책에 등록한 후보만 받는다. 추가 baseline은 공식 지원값을 확인해 별도 통제된 native 명령으로 평가하거나 정책·회귀를 함께 변경한다.

동일 입력·revision·도구·완료 기준을 사용하고 실패·중단·재시도를 분모에서 제거하지 않는다. 합격 outcome당 비용과 end-to-end 지연, 재작업, 독립 검토 실패를 비교한다. 표본 수·허용 편차·예산을 실행 전에 고정하고 결과를 본 뒤 목표를 바꾸지 않는다. intake 점수로 구현 성능을 대체하지 않는다.

## P2. 공식 계약 변경 시 갱신

모델 ID·effort·role 우선순위·profile 위치를 공식 출처와 실제 호스트에서 재확인한다. 버전 정책·관련 테스트·연구 일자를 함께 갱신한다. 과거 문서의 가격이나 capability를 자동으로 현재 사실로 취급하지 않는다.
