import { getCollection, type CollectionEntry } from 'astro:content';
import { CATEGORIES, type CategoryKey } from '../consts';

export type Post = CollectionEntry<'posts'>;
export type Devlog = CollectionEntry<'devlogs'>;
export type Project = CollectionEntry<'projects'>;

/** base 경로를 붙인 내부 링크 */
export function url(path = '') {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const clean = path.replace(/^\//, '');
  return `${base}/${clean}`;
}
/** 외부 주소는 그대로, 내부 경로는 base를 붙인다 */
export function asset(src?: string) {
  if (!src) return undefined;
  return /^https?:\/\//.test(src) ? src : url(src);
}

/** 기술 블로그(/blog) 안의 경로 */
export const blogUrl = (path = '') => url(`blog/${path.replace(/^\//, '')}`);
export const postUrl = (p: Post) => blogUrl(`posts/${p.id}/`);
export const devlogUrl = (d: Devlog) => blogUrl(`devlog/${d.id}/`);
export const categoryUrl = (c: CategoryKey) => blogUrl(`category/${c}/`);
export const tagSlug = (t: string) => t.trim().toLowerCase().replace(/\s+/g, '-');
export const tagUrl = (t: string) => blogUrl(`tags/${tagSlug(t)}/`);
export const seriesUrl = (s: string) => blogUrl(`series/${s}/`);
/** 포트폴리오(/) 안의 경로 */
export const projectUrl = (p: Project) => url(`projects/${p.id}/`);
export const categoryTitle = (c: CategoryKey) => CATEGORIES[c].title;

const visible = ({ data }: { data: { draft: boolean } }) => import.meta.env.DEV || !data.draft;
const byDateDesc = (a: { data: { pubDate: Date } }, b: { data: { pubDate: Date } }) =>
  b.data.pubDate.valueOf() - a.data.pubDate.valueOf();

export async function getPosts() {
  const all = await getCollection('posts', visible);
  return all.sort((a, b) => byDateDesc(a, b) || (b.data.seriesOrder ?? 0) - (a.data.seriesOrder ?? 0));
}
export async function getSeriesPosts(series: string) {
  return (await getPosts())
    .filter((p) => p.data.series === series)
    .sort((a, b) => (a.data.seriesOrder ?? 0) - (b.data.seriesOrder ?? 0));
}
// 개발일지가 하나도 없을 때 빈 컬렉션 경고가 빌드마다 쌓이지 않게 파일이 있는지 먼저 본다
const HAS_DEVLOGS = Object.keys(import.meta.glob('../content/devlogs/**/*.md')).length > 0;

export async function getDevlogs() {
  if (!HAS_DEVLOGS) return [];
  return (await getCollection('devlogs', visible)).sort((a, b) => byDateDesc(a, b) || b.id.localeCompare(a.id));
}
/** 한 프로젝트의 개발일지 (오래된 순) */
export async function getProjectDevlogs(projectId: string) {
  return (await getDevlogs()).filter((d) => d.data.project.id === projectId).reverse();
}
export async function getProjects() {
  return (await getCollection('projects', visible)).sort((a, b) => a.data.order - b.data.order);
}
/** 글 + 개발일지의 모든 태그와 개수 */
export async function getAllTags() {
  const map = new Map<string, { name: string; count: number }>();
  for (const e of [...(await getPosts()), ...(await getDevlogs())]) {
    for (const t of e.data.tags) {
      const k = tagSlug(t);
      const cur = map.get(k);
      map.set(k, { name: cur?.name ?? t, count: (cur?.count ?? 0) + 1 });
    }
  }
  return [...map.entries()].map(([slug, v]) => ({ slug, ...v })).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}

export function formatDate(d: Date) {
  return new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }).format(d);
}
/** 한국어 기준 대략적인 읽기 시간 (분당 500자) */
export function readingMinutes(body = '') {
  const text = body.replace(/```[\s\S]*?```/g, '').replace(/!\[.*?\]\(.*?\)/g, '').replace(/<[^>]+>/g, '');
  return Math.max(1, Math.round(text.length / 500));
}
