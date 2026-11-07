import type { ProfileConfig } from "../types/config";

// 个人资料配置
export const profileConfig: ProfileConfig = {
	avatar: "/assets/home/avatar.webp", // '/' 로 시작하면 public 기준
	name: "Chanus",
	bio: "Unreal Engine 5 · C++ 게임 클라이언트 개발",
	typewriter: {
		enable: false,
		speed: 80,
	},
	links: [
		{
			name: "GitHub",
			icon: "fa7-brands:github",
			url: "https://github.com/Cha-nu",
		},
		{
			name: "RSS",
			icon: "fa7-solid:rss",
			url: "/rss.xml",
		},
	],
};
