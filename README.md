# screw-problem

처음 보는 개발 과제(앱, 업무 자동화, 데이터 처리)를 Codex와 끝까지 구현하기 위한 스킬 모음입니다. 내가 문제를 이해하고 방향을 정하면, AI가 계획하고 구현합니다.

| 스킬 | 하는 일 |
|---|---|
| `screw-setup` | 처음 한 번. 역할, 모델, 멀티에이전트, 공통 제약 설정 |
| `drill-pilot` | 내가 문제를 이해하도록 질문을 주고받음 |
| `drill` | 현업 인터뷰, 질문지 작성, 회의록을 요건으로 정리 |
| `gap-assist` | 기획안이나 요건에서 빠진 것을 찾아 선택지와 추천 제시 |
| `when-you-encounter-problem` | 모르는 문제의 최소 행동 가이드: 구체화, 할 일 목록, 지침 4종 초안 |
| `crew` | Codex 세션 여러 개에 역할을 나눠 함께 구현 |

## 원칙

- 목표는 구현이다. 승인된 범위는 멈추지 않고 테스트하며 만든다.
- 멈추는 곳은 둘: 커밋 전(무엇을 짰는지 설명, 질문 최대 3개, 컨펌), 기존 지시로 풀 수 없는 모호함이나 충돌.
- 명확한 요구를 어긴 구현은 묻지 않고 고친다.
- 사람이 보는 곳은 `HANDOFF.md` 맨 위 '지금' 하나(crew는 `_crew/사용자_검토.md`). 나머지는 AI용이다.
- 지침과 문서는 짧게 쓴다. 개조식, 한 항목 한 줄, 같은 말 되풀이 금지.
- 내 답 중 계속 적용될 것은 `AGENTS.md`의 '사용자 기준'에 규칙으로 쌓인다.
- 테스트 먼저, 원인 확인 후 수정, 실행 증거 없이 완료 금지. [Superpowers](https://github.com/obra/superpowers)를 참고했다.
- 커밋 전 클린 코드, 구조, 보안 점검표로 변경분을 본다. 보안 치명 항목이 있으면 커밋하지 않는다.

## 설치

```bash
git clone https://github.com/HUNIooth/screw-problem.git
mkdir -p ~/.agents/skills
cp -R screw-problem/{screw-setup,drill-pilot,drill,gap-assist,when-you-encounter-problem,crew} ~/.agents/skills/
```

Codex를 다시 열고 `$screw-setup`부터 합니다. 그다음은 `$스킬이름`으로 부르거나 "요구사항 정리해 줘"처럼 말하면 켜집니다.

Claude Code에서도 쓰려면:

```bash
mkdir -p ~/.claude/skills
for s in screw-setup drill-pilot drill gap-assist when-you-encounter-problem crew; do
  ln -sfn ~/.agents/skills/$s ~/.claude/skills/$s
done
```

## 쓰는 순서

`screw-setup` → `drill-pilot`(문제 이해) → 필요하면 `drill`, `gap-assist` → `when-you-encounter-problem`(구체화, 할 일, 지침) → 크면 `crew`. 따로 써도 됩니다.

`when-you-encounter-problem`가 TODO.md와 지침 4종(AGENTS, PLAN, ENVIRONMENT, HANDOFF)을 만들면, 프로젝트 맨 위 폴더에서 새 Codex 세션을 열고 `<HANDOFF.md 경로> 읽고 시작해`라고 하면 이어서 구현합니다. 세부 규칙은 스킬이 정하지 않고 문답으로 함께 채웁니다. 하위 폴더에서 열면 바깥 파일을 못 고칠 수 있습니다.

## crew

1. 작업 폴더에서 `$crew`. 처음이면 킥오프를 고릅니다.
2. 킥오프가 `_crew/`에 요구사항, 계획, 세션별 시작 문장을 씁니다. 끝나면 이 세션은 노티가 됩니다.
3. 새 세션을 열어 `_crew/EXECUTION.md`의 시작 문장을 붙여 넣습니다.
4. 결정이 필요하면 노티가 알리고 `_crew/사용자_검토.md`에 올립니다. 그 한 장만 보면 됩니다.

## 파일 정리 지침

[guides/AGENTS.md](guides/AGENTS.md)는 임시 파일 위치, 이름, 원본 보존, 지우기 규칙입니다. 모든 세션에 적용하려면:

```bash
cat screw-problem/guides/AGENTS.md >> ~/.codex/AGENTS.md
```
