# Heading — 근거 기반 변경 분석

## 기준

입력 `heading.zip`의 git HEAD `4f8ae76`과 0.3.3 실제 소스를 기준으로 조사했다. 기준본의 일반·최적화 validator는 통과했다. 기준본 전체 unittest 실행은 컨테이너 timeout으로 끝까지 관찰되지 않았으므로 과거 전체 성공을 이번 결과로 재사용하지 않았다.

## 확인한 문제와 수정

기존 role TOML이 모델·추론 강도를 고정했다. 기존 문서는 호출 override가 이를 바꿀 수 있다고 가정했다. 2026-09-07에 확인한 공식 custom-agent 계약은 role 파일 설정을 우선한다. 따라서 역할의 권한만 유지하고 두 설정을 제거했다. 모델은 작업별 dispatch가 둘 다 전달한다. 근거는 RESEARCH의 S6다.

역할별 고정 ladder는 국소 작업과 복잡한 작업을 구별하지 못했다. 이제 easy를 다섯 긍정 조건의 교집합으로 정의하고 불확실성을 Astra에 보낸다. 위험·비가역성은 별도 effort floor를 가진다. 이 선택은 Heading 정책이지 공식 성능 우열의 실측 결과가 아니다.

요청값과 실행값이 섞일 위험을 분리했다. helper 결과는 요청으로만 남고, 호스트 필드 비교도 출처 인증과 최종 승인에서 분리한다. 환경 실패에 더 많은 추론을 배정하지 않는다. 이전 상위 모델의 실패 이력을 낮은 경로로 초기화하지 않는다.

평가 runner는 TimeoutExpired의 부분 stdout/stderr가 bytes일 수 있는데 text 쓰기에 바로 전달했다. 해당 경로를 명시적으로 decode하고 timeout·spawn failure·exit·duration을 기록하도록 수정했다. grading 전에 PASS를 출력하던 순서도 변경했다.

## 유지·제거 판단

KEEP: 5개 트랙, 기존 METHOD·schema·182개 사례, 4개 역할, 독립 검토, 선택적 direct 경로, 비파괴 설치기. REMOVE: role별 고정 모델, 운영 규칙의 이전 모델 ladder. INTEGRATE: 모델 ID·지원 effort·default·한도를 단일 정책으로, 공통 라우팅 의미를 공유 reference로 통합.

## 남은 불확실성

[UNVERIFIED] 이 계정·클라이언트에서 Astra/Luna 요청이 실제 적용되는지. [UNVERIFIED] 이 정책이 동일 작업 기준 비용·지연·품질에서 최적인지. 공식 문서 조회와 결정적 테스트는 이 두 가지를 증명하지 않는다.
