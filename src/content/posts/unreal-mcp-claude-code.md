---
title: "Claude Code로 언리얼 에디터 다루기: Unreal MCP 연결과 활용"
published: 2026-11-09T12:00:00+09:00
description: "Epic Games가 공개한 Claude Code 플러그인과 언리얼 5.8의 Unreal MCP로 에디터를 직접 조작하는 방법을 정리합니다. 지금 켜야 하는 플러그인은 Unreal MCP와 All Toolsets 두 개입니다."
category: 언리얼 엔진
tags: ["Unreal Engine", "MCP", "Claude Code", "AI"]
image: /images/unreal-mcp-claude-code/01_connection.png
draft: false
---

> 이 글은 2026년 11월 9일 기준으로 [Epic Games 공식 문서](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)와 [Claude Code 플러그인 저장소](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin)(버전 3.1.2)를 읽고 정리한 것입니다. Unreal MCP는 실험(Experimental) 기능이라 이름과 설정이 바뀔 수 있습니다. 사용하는 엔진 버전에서 확인하세요.

---
## 들어가며

AI에게 언리얼 코드를 물어보면 답은 받을 수 있습니다. 하지만 액터를 배치하거나 블루프린트를 고치는 일은 결국 제가 에디터에서 손으로 해야 했습니다.

언리얼 엔진 5.8에는 에디터 안에서 MCP(Model Context Protocol) 서버를 여는 **Unreal MCP** 플러그인이 들어 있습니다. 그리고 Epic Games는 Claude Code가 이 서버를 잘 쓰도록 돕는 플러그인을 따로 공개했습니다. 이 글에서는 두 가지를 연결하는 순서와, 연결한 뒤 무엇을 시킬 수 있는지 정리합니다.

먼저 자주 나오는 질문부터 답하겠습니다. **지금도 EditorToolset과 MCP 플러그인을 설치해야 하나.** 공식 안내 기준으로 에디터에서 켜야 하는 플러그인은 `Unreal MCP`(`ModelContextProtocol`)와 `All Toolsets`(`AllToolsets`) 두 개입니다. 자세한 내용은 바로 아래 절에서 다룹니다.

---
## 무엇을 켜야 하나

연결은 세 조각으로 이루어집니다. 에디터 안의 MCP 서버, 서버에 도구를 공급하는 툴셋, 그리고 Claude Code 쪽 설정입니다.

![Claude Code의 .mcp.json이 HTTP로 에디터 안의 Unreal MCP에 연결되고, Unreal MCP는 Toolset Registry와 All Toolsets의 도구를 내보내는 구조도](/images/unreal-mcp-claude-code/01_connection.png)

*빨간 테두리가 에디터에서 직접 켜야 하는 플러그인입니다. Claude 플러그인은 연결 자체가 아니라 연결을 어떻게 쓸지 알려 주는 역할입니다.*

| 이름 | 어디에 | 하는 일 | 필수 |
| --- | --- | --- | --- |
| Unreal MCP (`ModelContextProtocol`) | 언리얼 에디터 | MCP 서버와 통신 담당 | 예 |
| All Toolsets (`AllToolsets`) | 언리얼 에디터 | 기본 툴셋을 한 번에 켜서 실제 도구를 공급 | 예 |
| Toolset Registry | 언리얼 에디터 | 툴셋을 등록하는 곳. 위 플러그인을 켜면 자동으로 켜짐 | 자동 |
| Terminal | 언리얼 에디터 | 에디터 안에서 AI 에이전트를 실행 | 선택 |
| Unreal Engine Skills for Claude Code | Claude Code | 사용법을 담은 스킬과 시작 훅 | 권장 |

### EditorToolset은 따로 켜야 하나

초기 안내 글 중에는 `ModelContextProtocol`과 `EditorToolset`을 켜라고 한 것이 있습니다. 지금 공식 안내는 다릅니다. Claude Code 플러그인 저장소는 2026년 6월 26일 버전 3.0.3에서 `AllToolsets`를 필수 플러그인으로 문서에 추가했습니다. 근거는 다음과 같습니다.

- `Unreal MCP`만 켜면 서버는 뜨지만 도구가 하나도 나오지 않습니다. 도구는 툴셋 플러그인이 공급하기 때문입니다.
- `AllToolsets`는 기본 툴셋을 한꺼번에 켜 주는 에디터 전용 묶음 플러그인입니다. 기본값이 꺼져 있어서 직접 켜야 합니다.
- 도구 일부만 노출하고 싶으면 `AllToolsets` 대신 원하는 툴셋 플러그인을 하나씩 켭니다. `EditorToolset`을 개별로 켜는 것은 이 경우에 해당합니다.

정리하면 `Unreal MCP` + `All Toolsets` 두 개를 켜면 됩니다. Epic 공식 문서에는 `EditorToolset`이라는 이름이 따로 나오지 않습니다. 켰는데도 기대한 툴셋이 보이지 않으면 콘솔에서 `ModelContextProtocol.RefreshTools`를 실행하고, 그래도 없으면 해당 툴셋 플러그인이 켜져 있는지 확인합니다.

---
## 연결하는 순서

### 1. 에디터에서 플러그인 켜기

**Edit > Plugins**에서 `Unreal MCP`와 `All Toolsets`를 검색해 켜고 에디터를 다시 시작합니다. `.uproject`를 직접 고쳐도 됩니다.

```json
"Plugins": [
  { "Name": "ModelContextProtocol", "Enabled": true },
  { "Name": "AllToolsets", "Enabled": true }
]
```

### 2. MCP 서버 켜기

서버는 기본으로 꺼져 있습니다. 세 가지 방법 중 하나를 씁니다.

- 콘솔에서 한 번만: `ModelContextProtocol.StartServer`
- 매번 자동으로: **Edit > Editor Preferences > General > Model Context Protocol**의 **Auto Start Server**를 켭니다.
- 실행 인자로: `-ModelContextProtocolStartServer`

자동 시작 설정은 `Saved/Config/<플랫폼>Editor/EditorPerProjectUserSettings.ini`에 저장됩니다. 사람마다 다른 설정이라 소스 관리에는 들어가지 않습니다.

```ini
[/Script/ModelContextProtocolEngine.ModelContextProtocolSettings]
bAutoStartServer=True
```

기본 주소는 `http://127.0.0.1:8000/mcp`입니다. 8000번 포트를 다른 프로그램이 쓰고 있으면 `ModelContextProtocol.StartServer 8100`처럼 포트를 바꿉니다.

### 3. Claude Code 설정 파일 만들기

에디터 콘솔에서 다음 명령을 실행하면 Claude Code가 읽는 `.mcp.json`이 만들어집니다.

```text
ModelContextProtocol.GenerateClientConfig ClaudeCode
```

런처로 설치한 엔진이면 `.uproject` 옆에, 소스 빌드면 `Engine/` 폴더가 있는 작업 공간 루트에 생깁니다. 내용은 다음과 같습니다. 에디터를 켜기 전이라면 직접 써도 됩니다.

```json
{
  "mcpServers": {
    "unreal-mcp": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

`ClaudeCode` 대신 `Cursor`, `VSCode`, `Gemini`, `Codex`, `All`도 넣을 수 있습니다. Claude Code는 이 파일이 있는 폴더에서 실행해야 연결을 찾습니다.

### 4. Claude Code 플러그인 설치

Claude Code에서 다음 명령을 실행합니다. 공식 플러그인 마켓플레이스(`claude-plugins-official`)에 올라와 있습니다.

```text
/plugin install unreal-engine-skills-for-claude-code@claude-plugins-official
```

마켓플레이스가 보이지 않으면 `/plugin marketplace add anthropics/claude-plugins-official`을 먼저 실행합니다. 팀 전체가 쓰게 하려면 프로젝트의 `.claude/settings.json`에 다음을 넣고 커밋합니다.

```json
{
  "enabledPlugins": {
    "unreal-engine-skills-for-claude-code@claude-plugins-official": true
  }
}
```

이 플러그인에는 MCP 서버 설정이 들어 있지 않습니다. 연결은 3단계의 `.mcp.json`이 맡고, 플러그인은 다음 세 가지를 더합니다.

| 구성 | 하는 일 |
| --- | --- |
| `unreal-mcp` 스킬 | 도구를 찾고 부르는 순서, 저장·컴파일·PIE 관련 안전 규칙 |
| `create-toolset`, `unreal-skill` 스킬 | 새 툴셋이나 프로젝트 전용 에이전트 스킬을 만들 때 쓰는 안내 |
| `SessionStart` 훅 | 작업 폴더에서 `.uproject`를 찾아 "언리얼 프로젝트"라고 Claude에게 알림 |

Windows에서는 훅이 bash 스크립트라서 Git Bash나 WSL이 필요합니다. bash가 없어도 MCP 도구는 동작하고, 시작할 때 프로젝트 안내 한 줄만 빠집니다.

### 5. 연결 확인

1. 에디터 Output Log에 MCP 서버 시작 메시지가 있는지 봅니다.
2. Claude Code에서 `/mcp`를 실행해 `unreal-mcp`가 연결됐는지 봅니다.
3. "현재 레벨의 액터 목록을 보여 줘"처럼 읽기만 하는 요청을 해 봅니다. 목록이 나오면 연결이 끝난 것입니다.

---
## Claude가 도구를 찾는 방식

툴셋에는 수백 개의 도구가 있습니다. 이걸 처음부터 모두 Claude에게 알려 주면 설명만으로 대화 공간(컨텍스트)을 많이 차지합니다. 그래서 Unreal MCP는 기본으로 <strong>도구 검색(tool search)</strong>을 켜 둡니다.

![요청에서 list_toolsets, describe_toolset, call_tool을 거쳐 결과 확인으로 이어지는 다섯 단계 흐름도](/images/unreal-mcp-claude-code/02_tool_search.png)

*처음 보이는 도구는 세 개의 메타 도구뿐입니다. 실제 도구는 필요할 때 찾아서 `call_tool`로 부릅니다.*

- `list_toolsets`: 어떤 툴셋이 등록돼 있는지 봅니다.
- `describe_toolset`: 고른 툴셋의 함수 이름과 인자 형식을 읽습니다.
- `call_tool`: 툴셋 이름, 함수 이름, 인자를 넘겨 실행합니다. 결과는 같은 차례에 돌아옵니다.

그래서 사용자가 도구 이름을 외울 필요는 없습니다. "블루프린트를 만들어 줘"라고 하면 Claude가 블루프린트 툴셋을 찾아 읽고 부릅니다. 모든 도구를 처음부터 보이게 하려면 설정에서 `bEnableToolSearch=False`로 바꿀 수 있지만, 처음 주고받는 도구 설명이 그만큼 커집니다.

---
## 무엇을 시킬 수 있나

플러그인 README가 나열한 영역은 다음과 같습니다. 아래 요청 문장은 이해를 돕기 위한 예시입니다.

| 영역 | 요청 예시 |
| --- | --- |
| 액터와 레벨 | "PlayerStart 주변에 큐브 다섯 개를 원형으로 배치해 줘" |
| 블루프린트, 위젯 | "`BP_Door`에 `bIsLocked` 변수를 추가하고 컴파일해 줘" |
| 에셋, 데이터 테이블 | "`DT_Enemy`의 행을 읽어서 체력이 100 이하인 것만 보여 줘" |
| 머티리얼, Niagara, Sequencer | "`M_Base`로 색만 다른 머티리얼 인스턴스 세 개를 만들어 줘" |
| C++과 테스트 | "방금 고친 C++를 Live Coding으로 컴파일하고 에러를 정리해 줘" |
| 에디터 | "뷰포트 스크린샷을 찍고 Output Log의 경고를 모아 줘" |

C++을 고친 뒤에는 `LiveCodingToolset.CompileLiveCoding`이 쓰입니다. 컴파일이 실제로 끝날 때까지 기다렸다가 MSVC 에러를 돌려주기 때문에, IDE로 넘어가지 않고 고치기와 컴파일을 이어서 할 수 있습니다.

프로젝트마다 규칙이 다르다면 <strong>에이전트 스킬(Agent Skill)</strong>을 등록해 둘 수 있습니다. 폴더 구조, 이름 규칙, 정해진 작업 순서 같은 내용입니다. Claude는 작업 전에 `AgentSkillToolset.ListSkills`로 프로젝트 스킬을 확인하고, 맞는 것이 있으면 일반 규칙보다 먼저 따릅니다. 만드는 법은 플러그인의 `unreal-skill` 스킬이 안내합니다.

---
## 쓰기 전에 알아 둘 점

이 연결은 Claude가 에디터를 직접 바꿀 수 있게 합니다. 편한 만큼 조심할 부분도 분명합니다.

**저장하고 커밋한 뒤 시작합니다.** MCP 도구는 살아 있는 `UObject`를 바로 고칩니다. 여러 에셋을 한 번에 옮기거나 지울 수 있고, 컴파일을 거친 변경은 되돌리기(Undo)가 안 될 수 있습니다. 긴 작업 전에는 저장과 커밋으로 돌아갈 지점을 만듭니다.

**권한 확인을 끄지 않습니다.** `ProgrammaticToolset.execute_tool_script`는 에디터 안에서 임의의 Python을 실행합니다. `--dangerously-skip-permissions`로 Claude Code를 실행하면 이런 호출도 확인 없이 지나갑니다. README는 이 플러그인을 쓰는 동안 그 옵션을 쓰지 말라고 권합니다.

**로컬에서만 씁니다.** 서버는 기본으로 `localhost`에만 열리고 인증이 없습니다. 같은 컴퓨터의 다른 프로세스는 접속할 수 있으므로, 공용 컴퓨터에서 켜거나 포트를 밖으로 열지 않습니다.

**컴파일과 PIE 중에는 기다립니다.** C++나 셰이더를 컴파일하는 중에는 호출이 멈추거나 이상하게 실패합니다. Play-in-Editor 중에는 에셋 생성 같은 에디터 전용 도구가 다르게 동작합니다. 결과가 이상하면 PIE가 켜져 있는지 먼저 봅니다.

**결과를 꼭 읽습니다.** 블루프린트 컴파일이나 위젯 생성은 실패해도 예외 없이 실패 상태만 돌려줄 때가 있습니다. 성공이라고 분명히 나오지 않으면 다음 단계로 넘어가지 않습니다.

에디터를 두 개 이상 띄운다면 둘 다 8000번 포트를 쓰려고 합니다. 프로젝트마다 다른 포트(8100, 8101처럼)를 정하고, 각 `.mcp.json`도 같은 포트로 맞춥니다.

---
## 막혔을 때

| 증상 | 확인할 것 |
| --- | --- |
| `/mcp`에 `unreal-mcp`가 없음 | Claude Code를 `.mcp.json`이 있는 폴더에서 실행했는지, 에디터에서 서버가 켜졌는지 |
| 연결은 되는데 도구가 없음 | `All Toolsets`를 켰는지. 켠 뒤라면 `ModelContextProtocol.RefreshTools` |
| "Failed to listen on port" | 포트를 바꾸고 `GenerateClientConfig ClaudeCode`를 다시 실행 |
| 호출이 멈추거나 실패함 | 컴파일, 레벨 로딩, PIE 중인지 |

---
## 언제 무엇을 쓰나

| 쓰는 곳 | 방법 | 이유 | 예시 |
| --- | --- | --- | --- |
| 혼자 처음 써 볼 때 | `All Toolsets` + 콘솔에서 서버 시작 | 설정이 가장 적음 | 레벨 액터 목록 읽기 |
| 매일 쓰는 프로젝트 | Auto Start Server + `.mcp.json` | 에디터만 켜면 바로 연결 | 블루프린트 변수 추가 |
| 팀 프로젝트 | `.claude/settings.json`에 플러그인 등록 + 에이전트 스킬 | 팀원 모두 같은 규칙으로 동작 | 이름 규칙에 맞춘 에셋 생성 |
| 노출 범위를 줄이고 싶을 때 | `AllToolsets` 대신 개별 툴셋 플러그인 | 필요한 도구만 열림 | 머티리얼 작업만 허용 |

---
## 복습 질문

답을 먼저 떠올린 다음 눌러서 확인해 보세요.

<details>
<summary>1. Unreal MCP 플러그인만 켰는데 Claude가 쓸 도구가 없다고 합니다. 왜 그럴까요.</summary>

Unreal MCP는 서버와 통신만 맡고, 도구는 툴셋 플러그인이 공급합니다. `All Toolsets`를 켜거나 필요한 툴셋 플러그인을 개별로 켠 뒤 `ModelContextProtocol.RefreshTools`를 실행합니다.

</details>

<details>
<summary>2. Claude Code 플러그인을 설치하지 않아도 연결이 되나요.</summary>

됩니다. 연결 자체는 에디터가 만든 `.mcp.json`이 맡습니다. 플러그인은 도구를 찾는 순서와 안전 규칙을 담은 스킬, 프로젝트를 알려 주는 시작 훅을 더해서 Claude가 연결을 더 정확하게 쓰도록 돕습니다.

</details>

<details>
<summary>3. 처음에 보이는 MCP 도구가 세 개뿐인 이유는 무엇인가요.</summary>

도구 검색이 기본으로 켜져 있기 때문입니다. 수백 개 도구의 설명을 처음부터 보내지 않고, `list_toolsets`, `describe_toolset`으로 필요한 것만 찾아 `call_tool`로 부릅니다. 대화 공간을 아끼고 도구 목록이 중간에 바뀌지 않게 하려는 설계입니다.

</details>

---
## 마치며

지금 기준으로 필요한 것은 에디터의 `Unreal MCP`와 `All Toolsets` 두 플러그인, 서버 시작, `.mcp.json` 생성입니다. Claude Code 플러그인은 필수는 아니지만, 도구를 찾는 순서와 안전 규칙을 알려 주므로 함께 설치하는 편이 낫다고 생각합니다.

Unreal MCP는 아직 실험 기능이라 이 글의 이름과 설정도 바뀔 수 있습니다. 바뀐 내용을 확인하면 이 글을 고치겠습니다.

**참고 자료**

- [Unreal MCP in Unreal Editor (Epic Games 공식 문서)](https://dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor)
- [Unreal Engine Skills for Claude Code 플러그인 (GitHub)](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin)
