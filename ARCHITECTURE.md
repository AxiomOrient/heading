# Heading — 실제 구조와 소유권

```text
사용자 입력 / 저장소 관찰
  → SKILL intake: effective track 선택
  → METHOD: outcome · owned surface · done · evidence 고정
  → Lead: task facts와 필수 work shape 작성
  → model_routing.select: 순수한 요청 계산
  → host adapter: 실제 지원 계약 확인 후 model + effort 요청
  → host metadata: 실제 task · model · effort · role · sandbox 관찰
  → 단일 작성자 작업 → 독립 검토 → Lead 승인
```

| 책임 | authoritative owner | 증거 |
| --- | --- | --- |
| 제품 분류·방법·완료 | 5개 SKILL과 각 METHOD | 계약·변경 경로·테스트 |
| 라우팅 값과 한계 | `model-policy.json` | 버전·공식 source·회귀 사례 |
| 요청 계산 | `model_routing.py` | 17개 고정 사례·1,296 task-fact 조합 |
| read-heavy handoff | `evidence_capsule.py` | 닫힌 schema·source reference |
| 역할·권한 | 4개 runtime role TOML | read-only 3, writer 1 |
| 실제 모델·프로세스 | 실행 호스트 | host metadata·task ID·로그 |
| 수락 | Lead | 독립 검토와 최종 상태 |
| 선택적 profile 설치 | `scripts/install.py` | 비파괴 preflight·write·check |

`shape`는 모든 packet의 필수 값이다. `riskBand`는 `ROUTINE`, `CRITICAL`, 또는 `QUALIFICATION-REQUIRED`로 계산되는 설명 필드이며 shape를 대신하지 않는다. 결정적 preflight는 모델 요청 없이 `DIRECT_TOOLS`를 반환한다. 모델 route는 요청값만 반환하며 effective 값은 host metadata 없이는 null이다.

profile은 새 Lead 세션의 초기 요청이다. plugin manifest나 `agents/openai.yaml`은 모델 switch가 아니다. helper는 API를 호출하지 않고 host adapter는 별도 I/O 경계다. 응답의 자기 주장이나 요청 메타데이터를 실제 모델 실행의 근거로 올리지 않는다.
