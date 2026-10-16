# 홍보 예제: Fight the Flood

[승인된 영상·썸네일](https://github.com/okdalto/siljangnim-shorts/releases/tag/v1.0.0). 약 37.7초, 1080×1920·60fps. 이 광고도 실장님 Shorts 스킬을 따라 에이전트가 제작했다.

## 최종 연출

- 중앙의 쇼츠 카드 한 장이 주변으로 방사형 복제된다. 우리 카드가 옆에서 밀고 들어와 기존 카드를 밀어내며, 많은 카드가 흐르다가 감속해 “Naturally” 발화에 마지막 한 장이 남는다.
- 에이전트가 대본·음성·자막·모션을 만들고 같은 대화에서 고치는 과정을 도형 변화로 설명한다. 모션 안에는 작은 설명 글자를 넣지 않는다.
- “No separate app.” 뒤 0.5초 쉰다. 이어 “Burn electricity. Waste cooling water.”를 말한다.
- “Fight the flood. By adding to it.” 뒤 약 1초 쉰다. 같은 스킬로 제작했다는 고지를 보여 주고 원본 실장님 로고로 끝난다.
- 썸네일은 검은 배경, 큰 영어 제목 **FIGHT THE FLOOD.**, 빨간 재생 토큰 × 청록색 물방울, 영상 토큰으로 만든 파도다. 영상과 썸네일 모두 위아래 여백을 대칭으로 유지한다.

## 소스와 재사용 범위

[examples/revenge-morph/](../examples/revenge-morph/)는 이 영상의 소스와 단계별 편집 도구다. `opening.tsx`는 카드 도입부, `motion.py`는 설명 모션, `final.tsx`는 합성, `thumbnail-prompt.txt`는 썸네일 양식이다.

후처리 스크립트는 특정 중간 영상과 자막을 입력으로 받는다. 특히 `pause-after-app.py`는 이 영상의 1424프레임을 기준으로 동작한다. 새 주제에는 그대로 적용하지 말고 실제 발화 시점을 다시 측정한다. 저장소 소스만으로 승인본을 한 명령에 재현할 수 있는 구조는 아니다. 음성 캐시·중간 결과·생성 썸네일은 별도로 필요하다.

공통 제작 규칙은 [SKILL.md](../SKILL.md), 최종 전달 파일은 [Drive 전달 규약](DRIVE_DELIVERY.md)을 따른다.
