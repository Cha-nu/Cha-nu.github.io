import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

import { postGlob } from "./loaders/post-loader";

const postsCollection = defineCollection({
	loader: postGlob({ pattern: "**/*.{md,mdx}", base: "./src/content/posts" }),
	schema: z.object({
		title: z.string(),
		published: z.date(),
		updated: z.date().optional(),
		draft: z.boolean().optional().default(false),
		description: z.string().optional().default(""),
		image: z.string().optional().default(""),
		tags: z.array(z.string()).optional().default([]),
		category: z.string().optional().nullable().default(""),
		lang: z.string().optional().default(""),
		pinned: z.boolean().optional().default(false),
		// 기본값을 없앴다. 값이 없으면 commentConfig.optIn에 따라 댓글을 켜고 끈다.
		comment: z.boolean().optional(),
		priority: z.number().optional(),
		author: z.string().optional().default(""),
		sourceLink: z.string().optional().default(""),
		licenseName: z.string().optional().default(""),
		licenseUrl: z.string().optional().default(""),

		/* Page encryption fields */
		encrypted: z.boolean().optional().default(false),
		password: z.string().optional().default(""),
		passwordHint: z.string().optional().default(""),
		hideHomeContent: z.boolean().optional(),

		/* 관련 프로젝트 id (src/content/projects 파일 이름). 개발일지는 필수로 단다. */
		project: z.string().optional(),

		/* Posts alias */
		alias: z.string().optional(),

		/* Custom permalink - 自定义固定链接，优先级高于 alias */
		permalink: z.string().optional(),

		/* For internal use */
		prevTitle: z.string().default(""),
		prevSlug: z.string().default(""),
		nextTitle: z.string().default(""),
		nextSlug: z.string().default(""),
		_publishedDateOnly: z.boolean(),
		_updatedDateOnly: z.boolean(),
	}),
});
const specCollection = defineCollection({
	loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/spec" }),
	schema: z.object({}),
});
const projectsCollection = defineCollection({
	loader: glob({ pattern: "**/*.md", base: "./src/content/projects" }),
	schema: z.object({
		title: z.string(),
		summary: z.string(),
		period: z.string(), // 예: "2026.03 ~ 2026.06"
		start: z.string(), // 정렬·카드용 시작 월, 예: "2026-03"
		status: z.enum(["진행 중", "완료", "중단"]).default("완료"),
		team: z.string().optional(),
		role: z.string().optional(),
		engine: z.string().optional(),
		stack: z.array(z.string()).default([]),
		cover: z.string().optional(),
		video: z.string().optional(),
		links: z
			.array(z.object({ label: z.string(), url: z.string() }))
			.default([]),
		order: z.number().default(100), // 작을수록 앞
		draft: z.boolean().default(false),
	}),
});
export const collections = {
	posts: postsCollection,
	projects: projectsCollection,
	spec: specCollection,
};
