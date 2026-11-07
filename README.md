# Cha-nu.github.io

Astro로 만든 정적 사이트입니다. 한 저장소에서 두 사이트를 냅니다.

- **포트폴리오** — `https://cha-nu.github.io/` (프로젝트 소개)
- **게임 기술 블로그** — `https://cha-nu.github.io/blog/` (개발일지 중심, 지식 글 시리즈 포함)

 `main` 브랜치에 push하면 GitHub Actions가 빌드해서 GitHub Pages에 배포합니다.

## 로컬에서 실행

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # dist/ 에 결과물
```

## 새 글 쓰기

글 종류는 세 가지이고, 기술 블로그의 기본은 개발일지입니다. `templates/`의 틀을 복사해서 시작하세요. 자세한 작성 규칙은 [AGENTS.md](AGENTS.md)에 있습니다.

| 종류 | 위치 | 주소 | 틀 |
| --- | --- | --- | --- |
| 개발일지 | `src/content/devlogs/` | `/blog/devlog/파일이름/` | `templates/devlog.md` |
| 지식 글 | `src/content/posts/` | `/blog/posts/파일이름/` | `templates/post.md` |
| 프로젝트 | `src/content/projects/` | `/projects/파일이름/` | `templates/project.md` |

지식 글 frontmatter 예시:

```markdown
---
title: "글 제목"
description: "목록과 검색 결과에 보일 한두 줄 설명"
pubDate: 2026-11-10
category: physics        # game-math | physics | algorithm | unreal | cs
series: flight-theory   # 시리즈에 넣을 때만 (src/consts.ts 의 SERIES 키)
seriesOrder: 4          # 시리즈 안에서의 순서
tags: ["Unreal Engine"]
cover: /images/flight-4/01_cover.png   # 공유 미리보기 이미지 (선택)
draft: false            # true면 배포되지 않음
---

본문...
```

- 동영상은 `public/videos/`에 mp4로 두거나 YouTube 주소를 씁니다.
- 그림은 `public/images/` 아래에 두고 `![설명](/images/폴더/파일.png)` 로 씁니다. 저장소 이름에 맞는 경로는 빌드할 때 자동으로 붙습니다.
- 수식은 `$$ ... $$` (블록) 또는 `$ ... $` (문장 안)으로 씁니다. KaTeX로 렌더링됩니다.
- 예전 주소(`/posts/...` 등)는 `astro.config.mjs`의 `redirects`로 `/blog/...`에 연결됩니다.
- 포트폴리오·블로그 이름, 기술 스택, 시리즈 정보는 `src/consts.ts` 에서 바꿉니다.

## AI 에이전트와 함께 쓰기

`AGENTS.md`에 문체, 글 구조, 그림·영상 규칙, 검수 순서가 정리되어 있습니다. Claude Code는 `CLAUDE.md`를 통해 이 파일을 자동으로 읽습니다. 글의 수치를 만든 스크립트는 `research/`에 있습니다.

## 처음 한 번만: GitHub Pages 켜기

저장소 **Settings → Pages → Build and deployment → Source** 를 **GitHub Actions** 로 바꿉니다.
