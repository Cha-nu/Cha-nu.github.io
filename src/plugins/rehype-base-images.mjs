// Markdown 본문의 "/images/...", "/videos/..." 경로(img, video, source) 앞에 base를 붙인다.
// 저장소가 "아이디.github.io"가 아니라 "아이디.github.io/저장소" 아래에 배포될 때 이미지가 깨지지 않게 하기 위함.
export default function rehypeBaseImages({ base = '/' } = {}) {
  const prefix = base.endsWith('/') ? base.slice(0, -1) : base;
  const walk = (node) => {
    if (node.type === 'element' && ['img', 'video', 'source'].includes(node.tagName)) {
      for (const key of ['src', 'poster']) {
        const v = node.properties?.[key];
        if (typeof v === 'string' && v.startsWith('/') && !v.startsWith('//') && prefix && !v.startsWith(prefix + '/')) {
          node.properties[key] = prefix + v;
        }
      }
      if (node.tagName === 'img') {
        node.properties.loading ??= 'lazy';
        node.properties.decoding ??= 'async';
      }
    }
    node.children?.forEach(walk);
  };
  return (tree) => walk(tree);
}
