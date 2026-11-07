// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { unified } from '@astrojs/markdown-remark';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeBaseImages from './src/plugins/rehype-base-images.mjs';

// GitHub Actions가 저장소 이름을 보고 SITE_URL, BASE_PATH를 넣어 준다 (.github/workflows/deploy.yml)
// 로컬에서는 기본값으로 동작한다.
const SITE = process.env.SITE_URL ?? 'http://localhost:4321';
const BASE = process.env.BASE_PATH ?? '/';

export default defineConfig({
  site: SITE,
  base: BASE,
  trailingSlash: 'ignore',
  integrations: [sitemap()],
  markdown: {
    // Astro 7 기본 처리기(Sätteri) 대신 remark/rehype 처리기를 써서 수식(KaTeX)과 이미지 경로 플러그인을 붙인다
    processor: unified({
      remarkPlugins: [remarkMath],
      rehypePlugins: [rehypeKatex, [rehypeBaseImages, { base: BASE }]],
    }),
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
      wrap: false,
    },
  },
});
