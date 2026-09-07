# Heading — 실제 구조와 소유권

```text
사용자 입력 / 저장소 관찰
  → SKILL intake: effective track 선택
  → METHOD: outcome · owned surface · done · evidence 고정
  → Lead: 실제 task facts와 실패 이력 작성
  → model_routing.select: 결정적 요청 생성
  → host adapter: 지원 계약 확인, 모델+추론 요청
  → host metadata: 실제 task · model · effort · role · sandbox 관찰
  → 단일 작성자 작업 → 독립 검토 → Lead 승인
```

| 책임 | authoritative owner | 증거 |
| --- | --- | --- |
| 제품 분류·방법·완료 | 5개 SKILL과 각 METHOD | 계약·변경 경로·테스트 |
| 라우팅 값과 제한 | model-policy.json | 버전·공식 source·회귀 사례 |
| 사실 기반 선택 | model_routing.py select | 33개 고정 사례·216개 fact 조합 |
| 역할·권한 | 4개 runtime role TOML | read-only 3, writer 1 |
| 실제 모델·프로세스 | 실행 호스트 | 호스트 metadata·task ID·로그 |
| 수락 | Lead | 독립 검토와 최종 상태 |
| 설치 | scripts/install.py | 비파괴 preflight·write·check |

profile은 새 Lead 세션의 초기 요청이다. plugin manifest나 agents/openai.yaml은 모델 switch가 아니다. 모델 API를 직접 호출하는 새 서비스·자체 agent framework·숨은 provider fallback은 추가하지 않았다. Codex native surface는 외부 I/O 경계다.

helper 파일 읽기와 CLI는 I/O, select는 순수 로직, 관찰 비교는 입력 필드 비교다. 네이티브 eval runner는 별도 adapter이며 intake만 실행한다. 응답의 자기 주장이나 요청 메타데이터를 실제 모델 실행의 근거로 올리지 않는다.
