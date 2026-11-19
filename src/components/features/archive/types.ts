export interface ArchivePanelProps {
	tags: string[];
	categories: string[];
	sortedPosts: Post[];
}

export interface Post {
	id: string;
	url?: string;
	data: {
		title: string;
		tags: string[];
		category?: string;
		published: Date;
		_publishedDateOnly: boolean;
		alias?: string;
		permalink?: string;
		// 카드(앨범) 보기용. 사용자 요청으로 추가.
		description?: string;
		image?: string;
	};
}

export interface Group {
	year: number;
	posts: Post[];
}
