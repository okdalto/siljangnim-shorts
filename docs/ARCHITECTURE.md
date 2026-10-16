# 스킬 제작 구조

대화 중인 에이전트가 [SKILL.md](../SKILL.md)를 읽고 기획·대본·디자인·검수를 맡는다. `./shorts`는 필요한 제작 단계만 실행하는 CLI다.

```text
에이전트 → shorts → cli.py → Workspace
                              ├─ script / design / asset: 버전 저장
                              ├─ speech: Media → Comfy 음성 → 실제 발화 정렬
                              ├─ preview / render: Remotion → 썸네일·영상·SRT
                              └─ review: 해당 렌더의 검수 기록
```

## 코드 구성

| 경로 | 역할 |
|---|---|
| `shorts_app/cli.py` | 명령·프로세스 잠금·작업 완료 대기 |
| `shorts_app/agent_workspace.py` | revision 충돌 검사, 불변 소스, 자산 가져오기, 발화·렌더 상태 |
| `shorts_app/media.py`, `comfy.py` | 음성 생성·캐시, 발화 정렬, 자막 내보내기 |
| `shorts_app/model.py`, `store.py`, `graphics.py` | 해시·원자적 JSON 저장·자막 줄바꿈 |
| `remotion/agent-render.mjs`, `agent-root.tsx`, `layout.tsx` | 자유형 디자인, 공통 한영 자막·브랜드 엔딩, 최종 합성 |
| `motion/` | 에이전트가 작성하는 Manim Scene의 고정된 실행 환경 |
| `shorts_app/agent_viewer.py`, `agent_viewer/` | 내부 뷰어가 없을 때의 읽기 전용 결과 화면 |
| `examples/revenge-morph/` | 현재 홍보 영상의 모션·합성·편집 소스 |

## 수정과 캐시

script 변경은 speech·preview·delivery·review를 무효화한다. 유료 음성 캐시는 유지하므로 같은 영어 대사는 재사용한다. design 변경은 speech를 유지하며 preview·delivery·review만 무효화한다. 렌더마다 디자인·timeline·자산을 별도 폴더에 스냅샷한다. 결과 검수 기록은 해당 revision과 렌더에 연결한다.

Manim은 실제 발화 시점에 맞춘 60fps 무음 클립을 만든다. CLI로 가져온 클립을 자유형 TSX에서 배치하고 Remotion이 음성·자막을 합성한다. `layout.tsx`의 상하 270px 여백을 영상과 썸네일에서 공유한다.

기존 `agent-projects/` 작업 상태와 `.cache/`의 키 형식은 유지한다. 로컬 렌더러는 에이전트가 작성·검토한 코드를 실행하며 OS 샌드박스가 아니다. 원본 음성 캐시·발화 정렬·최종 승인 영상은 코드 정리로 수정하지 않는다.
