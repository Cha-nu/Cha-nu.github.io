# Cha-nu.github.io

게임 개발 블로그 겸 포트폴리오입니다. → https://cha-nu.github.io/

- **글** `/posts/…` — 개발일지(프로젝트별 기록)와 지식 글(예: 게임 비행 이론 시리즈)
- **프로젝트** `/projects/` — 만든 게임 소개. 같은 프로젝트의 개발일지가 상세 페이지에 모입니다.

[Astro](https://astro.build/)와 [Mizuki](https://github.com/matsuzaka-yuki/Mizuki) 테마(Apache-2.0, 원본 [Fuwari](https://github.com/saicaca/fuwari)는 MIT)를 바탕으로 한국어 UI, 프로젝트 컬렉션, 배너·아바타를 바꿔 만들었습니다. 테마 라이선스는 `LICENSE`, `LICENSE.MIT`, `THIRD_PARTY_NOTICES.md`에 있습니다.

## 로컬에서 실행

pnpm이 필요합니다.

```bash
pnpm install
pnpm dev      # http://localhost:4321
pnpm build    # dist/
```

## 새 글 쓰기

`templates/`의 틀을 복사해서 시작하세요. 자세한 규칙은 [AGENTS.md](AGENTS.md)에 있습니다.

| 종류 | 위치 | 주소 | 틀 |
| --- | --- | --- | --- |
| 개발일지 | `src/content/posts/` (`category: 개발일지`, `project: <id>`) | `/posts/파일이름/` | `templates/devlog.md` |
| 지식 글 | `src/content/posts/` | `/posts/파일이름/` | `templates/post.md` |
| 프로젝트 | `src/content/projects/` | `/projects/파일이름/` | `templates/project.md` |

- 그림은 `public/images/`, 영상은 `public/videos/`(mp4) 또는 YouTube 주소.
- 수식은 `$$ ... $$`, `$ ... $` (KaTeX).
- 사이트 이름·메뉴·사이드바·배너는 `src/config/`에서 바꿉니다.

## 배포

`main`에 push하면 GitHub Actions가 빌드해 GitHub Pages에 올립니다. (Settings → Pages → Source: GitHub Actions)
