# 실장님 Shorts

**에이전트에 붙여 대화로 쇼츠를 만들고 고치는 스킬입니다.**

주제를 주면 사용 중인 에이전트가 대본을 쓰고, 음성·자막·설명 모션·썸네일을 제작합니다. 결과를 내부 뷰어로 보고 같은 대화에서 수정합니다. [SKILL.md](SKILL.md)가 제작 규약이며, 동봉한 스크립트는 음성 생성·발화 정렬·렌더링을 돕습니다.

[이 스킬로 만든 홍보 영상·썸네일](https://github.com/okdalto/siljangnim-shorts/releases/tag/v1.0.0) · [홍보 예제 설명](docs/PROMO.md)

## 설치와 사용

Codex의 스킬 폴더에 설치합니다.

```sh
git clone https://github.com/okdalto/siljangnim-shorts.git ~/.codex/skills/siljangnim-shorts
```

이미 받은 저장소는 심볼릭 링크로 연결해도 됩니다. 다른 에이전트에서는 해당 호스트의 스킬 설치 방식을 따르거나 `SKILL.md`를 읽도록 지정합니다.

> “실장님 Shorts 스킬로 쇼츠 과잉을 비꼬는 홍보 영상을 만들어 줘. 썸네일도 같이.”
>
> “첫 장면의 카드가 옆에서 밀려오게 바꿔 줘. 음성은 유지하고 위아래 여백은 대칭으로.”

에이전트가 기획과 수정 판단을 맡습니다. 별도 편집 앱이나 MCP 연결은 필요하지 않습니다. 제작에는 코드 실행과 이미지·영상 확인이 가능한 에이전트 환경이 필요합니다.

## 제작 환경

동봉한 도구를 쓸 때는 macOS/Linux, Python 3.12, uv, Node.js 22+, FFmpeg/ffprobe를 준비한 뒤 실행합니다.

```sh
cd ~/.codex/skills/siljangnim-shorts
./scripts/setup.sh
```

설명 모션은 Manim, 최종 합성은 Remotion을 사용합니다. Manim에는 Cairo/Pango와 `uv sync --project motion --locked`가 추가로 필요합니다.

기본 음성은 Comfy Router의 ElevenLabs George입니다. `COMFY_API_KEY` 또는 `~/.config/siljangnim-shorts/comfy-token`으로 키를 제공하며 서비스 크레딧을 사용합니다. 같은 대사의 음성은 캐시를 재사용합니다. [명령·환경·저장 경로](references/production-tools.md)

## 제작 기준과 전달 파일

1080×1920·60fps, 위아래 270px 대칭 여백, 영어 음성에 맞춘 한영 자막, 도형 변화로 설명하는 모션과 원본 실장님 로고 엔딩을 기본으로 합니다. 썸네일은 별도로 만듭니다.

승인된 영상 한 편의 Drive 전달 파일은 세 개입니다.

| 파일 | 내용 |
|---|---|
| `<주제>_final.mp4` | 한영 자막이 포함된 최종 영상 |
| `<주제>_thumbnail.png` | 최종 썸네일 |
| `<주제>_caption_KO_EN.txt` | 한국어 본문 → 영어 본문 → 공통 해시태그 최대 5개 |

[전달·검증 절차](docs/DRIVE_DELIVERY.md)

## 저장소 안내

| 경로 | 역할 |
|---|---|
| [SKILL.md](SKILL.md) | 에이전트가 읽는 공통 제작·수정·검수 규약 |
| [references/](references/) | 필요할 때 읽는 도구 사용법과 디자인 계약 |
| `shorts`, `shorts_app/`, `scripts/` | 제작 보조 명령과 Python 구현 |
| `motion/`, `remotion/`, `assets/` | 모션·합성 환경과 공용 브랜드 자산 |
| [examples/revenge-morph/](examples/revenge-morph/) | 홍보 영상의 구체적인 소스·편집 도구 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 제작 흐름과 코드 구성 |

작업물은 `agent-projects/`, 캐시는 `.cache/`에 저장되며 Git에서 제외됩니다. 코드 실행 도구이므로 에이전트가 작성·검토한 소스만 실행합니다.

## 개발과 출처

[검증 방법](docs/VERIFICATION.md). 내부 뷰어가 없는 환경에서는 `./shorts view`로 읽기 전용 결과 화면을 엽니다.

GPL-3.0-or-later. [실장님](https://github.com/okdalto/siljangnim)의 브랜드 자산과 기존 쇼츠 제작 코드를 재사용합니다. [출처·라이선스](THIRD_PARTY_NOTICES.md). Remotion과 외부 음성 서비스에는 각 제공자의 조건이 적용됩니다.
