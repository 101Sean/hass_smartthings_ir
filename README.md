# 🏠 SmartThings IR Controller

> 갤럭시 홈 미니의 IR 블래스터를 통해 에어컨, TV, 셋톱박스를 Home Assistant에서 제어하는 커스텀 통합

---

## 📌 개요

이 통합은 **SmartThings 공식 통합**을 기반으로 동작하며, 갤럭시 홈 미니의 IR 명령을 활용하여 에어컨, TV, 셋톱박스를 **Climate / Media Player 엔티티**로 변환합니다.

| 기기 | 엔티티 | 제어 기능 |
|------|--------|-----------|
| 에어컨 | Climate | 온도, 모드, 팬 속도 |
| TV | Media Player | 전원, 볼륨, 채널 |
| 셋톱박스 | Media Player | 전원, 볼륨, 채널 |

---

## 📋 필수 요구사항

- **Home Assistant 2026.5.0 이상**
- **SmartThings 공식 통합**이 설정되어 있어야 함 (OAuth 인증 완료)

---

## 🔧 설치 및 설정

### 1️⃣ 설치

**HACS (권장)**
1. HACS → `⋮` → `Custom repositories`
2. URL: `https://github.com/101Sean/smartthings-ir`
3. 카테고리: `Integration`
4. 설치 후 Home Assistant 재시작

**수동 설치**
1. [릴리즈](https://github.com/101Sean/smartthings-ir/releases) 다운로드
2. `/config/custom_components/`에 `smartthings_ir` 폴더 복사
3. Home Assistant 재시작

---

### 2️⃣ 통합 추가

1. `설정` → `기기 및 서비스` → `➕ 통합구성요소 추가`
2. **SmartThings IR Controller** 선택
3. 입력:

| 필드 | 설명 | 예시 |
|------|------|------|
| 이름 | 기기 이름 | "거실 에어컨" |
| 기기 ID | SmartThings UUID | `6e2fae23-1b49-474b-8d8d-9d4a16c6c474` |
| 유형 | `ac` / `tv` / `settop` | `ac` |

### SmartThings UUID 확인 방법
- SmartThings Developer Workspace → `My devices` → 기기 선택 → `Device ID`

---

## 🎮 대시보드 추가

### 에어컨 (Climate 카드)
```yaml
type: climate
entity: climate.거실_에어컨
```

### TV (타일 카드)
```yaml
type: tile
entity: media_player.거실_tv
name: TV
color: indigo
vertical: false
features_position: bottom
features:
  - type: media-player-next-track    # 채널 업
  - type: media-player-previous-track # 채널 다운
```

---

**Made with ❤️ by 101Sean**
