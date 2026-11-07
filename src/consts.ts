// 블로그 이름과 소개는 여기서 바꾸면 전체에 반영된다. 실명은 쓰지 않는다 (AGENTS.md 참고).
export const SITE_TITLE = '게임 개발 노트';
export const SITE_DESCRIPTION = '게임을 만들며 부딪힌 문제를 직접 재 보고 풀어 본 기록';
export const AUTHOR = 'Cha-nu';
export const GITHUB_URL = 'https://github.com/Cha-nu';

export const CATEGORIES = {
  'game-math': { title: '게임 수학', description: '벡터, 회전, 보간, 좌표계' },
  physics: { title: '게임 물리', description: '힘과 적분, 충돌, 비행·차량 물리' },
  algorithm: { title: '알고리즘', description: '자료구조, 탐색, 길찾기, 최적화' },
  unreal: { title: '언리얼 엔진', description: 'C++, GAS, 네트워크 복제, 렌더링' },
  cs: { title: 'CS 지식', description: '운영체제, 메모리, 네트워크, 동시성' },
} as const;
export type CategoryKey = keyof typeof CATEGORIES;
export const CATEGORY_KEYS = Object.keys(CATEGORIES) as [CategoryKey, ...CategoryKey[]];

export const SERIES: Record<string, { title: string; description: string; upcoming?: string[] }> = {
  'flight-theory': {
    title: '게임 비행 이론',
    description: '롤·피치·요부터 실속까지, 비행 게임을 만들며 부딪히는 문제를 하나씩 풀어 본다.',
    upcoming: ['4편: 조종면과 토크, 안정성'],
  },
};
