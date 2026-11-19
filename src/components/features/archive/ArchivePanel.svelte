<script lang="ts">
import I18nKey from "@i18n/i18nKey";
import { i18n } from "@i18n/translation";
import { formatDateToYYYYMMDD, getPostDateParts } from "@utils/date-utils";
import { comparePublishedDatesDescending } from "@utils/post-date-utils";
import { onMount } from "svelte";
import type { ArchivePanelProps, Group, Post } from "./types";

let {
	tags = $bindable([]),
	categories = $bindable([]),
	sortedPosts = [],
}: ArchivePanelProps = $props();

const params = new URLSearchParams(window.location.search);
tags = params.has("tag") ? params.getAll("tag") : [];
categories = params.has("category") ? params.getAll("category") : [];
const uncategorized = params.get("uncategorized");

let groups = $state<Group[]>([]);

function formatDate(date: Date, dateOnly: boolean) {
	return formatDateToYYYYMMDD(date, dateOnly).slice(5);
}

function formatTag(tagList: string[]) {
	return tagList.map((t) => `#${t}`).join(" ");
}

onMount(async () => {
	let filteredPosts: Post[] = sortedPosts;

	if (tags.length > 0) {
		filteredPosts = filteredPosts.filter(
			(post) =>
				Array.isArray(post.data.tags) &&
				post.data.tags.some((tag) => tags.includes(tag)),
		);
	}

	if (categories.length > 0) {
		filteredPosts = filteredPosts.filter(
			(post) => post.data.category && categories.includes(post.data.category),
		);
	}

	if (uncategorized) {
		filteredPosts = filteredPosts.filter((post) => !post.data.category);
	}

	// 按发布时间倒序排序，确保不受置顶影响
	filteredPosts = filteredPosts
		.slice()
		.sort((a, b) =>
			comparePublishedDatesDescending(
				a.data.published,
				b.data.published,
				a.id,
				b.id,
			),
		);

	const grouped = filteredPosts.reduce(
		(acc, post) => {
			const year = getPostDateParts(
				post.data.published,
				post.data._publishedDateOnly,
			).year;
			if (!acc[year]) {
				acc[year] = [];
			}
			acc[year].push(post);
			return acc;
		},
		{} as Record<number, Post[]>,
	);

	const groupedPostsArray = Object.keys(grouped).map((yearStr) => ({
		year: Number.parseInt(yearStr, 10),
		posts: grouped[Number.parseInt(yearStr, 10)],
	}));

	groupedPostsArray.sort((a, b) => b.year - a.year);

	groups = groupedPostsArray;
});
</script>

<div class="card-base px-8 py-6">
	{#each groups as group (group.year)}
		<div>
			<div class="flex flex-row w-full items-center h-15">
				<div
					class="w-[15%] md:w-[10%] transition text-2xl font-bold text-right text-75"
				>
					{group.year}
				</div>
				<div class="w-[15%] md:w-[10%]">
					<div
						class="h-3 w-3 bg-none rounded-full outline outline-(--primary) mx-auto
                  -outline-offset-2 z-50"
					></div>
				</div>
				<div class="w-[70%] md:w-[80%] transition text-left text-50">
					{group.posts.length}
					{i18n(
						group.posts.length === 1
							? I18nKey.postCount
							: I18nKey.postsCount,
					)}
				</div>
			</div>

			<!--
				사용자 요청으로 타임라인 줄 목록을 프로젝트 목록과 같은 카드(앨범) 격자로 바꿨다.
				테마 원본은 날짜·점·제목·태그를 한 줄로 늘어놓는 목록이다. 테마를 업데이트할 때 이 블록이 충돌 지점이다.
			-->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6 items-start mt-2 mb-8">
				{#each group.posts as post (post.id)}
					<a
						href={post.url || `/posts/${post.id}/`}
						aria-label={post.data.title}
						class="archive-card group relative block rounded-xl border border-black/10 dark:border-white/10 overflow-hidden transition-all duration-300 hover:shadow-xl hover:-translate-y-1"
					>
						<div
							class="aspect-video overflow-hidden relative bg-linear-to-br from-(--primary)/5 to-(--primary)/10"
						>
							{#if post.data.image}
								<img
									src={post.data.image}
									alt=""
									class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
									loading="lazy"
								/>
							{:else}
								<div class="w-full h-full flex items-center justify-center px-4">
									<span
										class="text-2xl font-bold text-(--primary)/25 select-none tracking-wide text-center"
									>
										{post.data.category ?? ""}
									</span>
								</div>
							{/if}
						</div>

						<div class="p-5">
							<div class="flex items-center justify-between mb-2 text-xs">
								<span class="text-50">
									{group.year}-{formatDate(
										post.data.published,
										post.data._publishedDateOnly,
									)}
								</span>
								{#if post.data.category}
									<span
										class="shrink-0 ml-3 px-2 py-0.5 rounded-md bg-(--primary)/10 text-(--primary) font-medium"
									>
										{post.data.category}
									</span>
								{/if}
							</div>

							<h3
								class="archive-clamp font-bold text-black/90 dark:text-white/90 group-hover:text-(--primary) transition-colors duration-200 mb-2"
							>
								{post.data.title}
							</h3>

							{#if post.data.description}
								<p
									class="archive-clamp text-sm text-black/60 dark:text-white/60 mb-3"
								>
									{post.data.description}
								</p>
							{/if}

							<div
								class="text-xs text-30 whitespace-nowrap text-ellipsis overflow-hidden"
							>
								{formatTag(post.data.tags)}
							</div>
						</div>
					</a>
				{/each}
			</div>
		</div>
	{/each}
</div>

<style>
	.archive-clamp {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
