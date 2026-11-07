import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';
import { CATEGORY_KEYS } from './consts';

/** 지식 글: 게임 수학, 물리, 알고리즘, 언리얼, CS */
const posts = defineCollection({
  loader: glob({ base: './src/content/posts', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    category: z.enum(CATEGORY_KEYS),
    series: z.string().optional(),
    seriesOrder: z.number().optional(),
    tags: z.array(z.string()).default([]),
    cover: z.string().optional(),
    project: reference('projects').optional(),
    draft: z.boolean().default(false),
  }),
});

/** 개발일지: 프로젝트를 만들며 남기는 기록 */
const devlogs = defineCollection({
  loader: glob({ base: './src/content/devlogs', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    project: reference('projects'),
    tags: z.array(z.string()).default([]),
    cover: z.string().optional(),
    video: z.string().optional(), // 대표 영상: /videos/... 의 mp4 또는 YouTube 주소
    draft: z.boolean().default(false),
  }),
});

/** 프로젝트: 포트폴리오 카드와 상세 페이지 */
const projects = defineCollection({
  loader: glob({ base: './src/content/projects', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    period: z.string(),             // 예: "2026.03 ~ 2026.06"
    status: z.enum(['진행 중', '완료', '중단']).default('완료'),
    team: z.string().optional(),     // 예: "개인", "4인 팀 (클라이언트 2)"
    role: z.string().optional(),     // 내가 맡은 부분
    engine: z.string().optional(),   // 예: "Unreal Engine 5.4"
    stack: z.array(z.string()).default([]),
    cover: z.string().optional(),
    video: z.string().optional(),
    links: z.array(z.object({ label: z.string(), url: z.string() })).default([]),
    order: z.number().default(100),  // 작을수록 앞에
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts, devlogs, projects };
