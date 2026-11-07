import rss from '@astrojs/rss';
import { SITE_TITLE, SITE_DESCRIPTION } from '../../consts';
import { getPosts, getDevlogs } from '../../lib/posts';

export async function GET(context) {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const items = [
    ...(await getPosts()).map((p) => ({ title: p.data.title, description: p.data.description, pubDate: p.data.pubDate, link: `${base}/posts/${p.id}/` })),
    ...(await getDevlogs()).map((d) => ({ title: `[개발일지] ${d.data.title}`, description: d.data.description, pubDate: d.data.pubDate, link: `${base}/devlog/${d.id}/` })),
  ].sort((a, b) => b.pubDate.valueOf() - a.pubDate.valueOf());
  return rss({ title: SITE_TITLE, description: SITE_DESCRIPTION, site: context.site, items });
}
