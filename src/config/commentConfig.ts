import type { CommentConfig } from "../types/config";
import { SITE_LANG } from "./siteConfig";

// 评论系统配置
export const commentConfig: CommentConfig = {
	// GitHub 로그인 댓글·반응(좋아요)은 Giscus(GitHub Discussions)로 받는다.
	// 저장소에서 Discussions를 켜고 giscus 앱을 설치한 뒤 categoryId를 채우고 enable을 true로 바꾼다.
	enable: false, // 启用评论功能。当设置为 false 时，评论组件将不会显示在文章区域。
	system: "giscus", // 评论系统选择: "twikoo" | "giscus"
	twikoo: {
		envId: "https://twikoo.vercel.app",
		lang: SITE_LANG,
	},
	giscus: {
		repo: "Cha-nu/Cha-nu.github.io",
		repoId: "R_kgDOVmDHdg",
		category: "Announcements",
		categoryId: "your-category-id",
		mapping: "pathname",
		strict: "0",
		reactionsEnabled: "1",
		emitMetadata: "0",
		inputPosition: "top",
		theme: "preferred_color_scheme",
		// 블로그 색에 맞춘 테마 (public/giscus/)
		themeLight: "/giscus/light.css",
		themeDark: "/giscus/dark.css",
		lang: SITE_LANG,
		loading: "lazy",
	},
};
