// JEV 라우팅 테이블 자동 갱신 스크립트
// 새 사용자 스킬 설치 후 실행: node refresh-table.mjs
// - 기존 테이블의 수동 큐레이션된 행(유형/키워드)은 보존
// - 새 스킬이 있으면 description에서 트리거 키워드를 추출해 행을 자동 추가
import { promises as fs } from 'node:fs';
import path from 'node:path';

const USER_ROOT = 'C:/Users/soka7/.aside/u/0/skills/user';
const JEV_FILE = path.join(USER_ROOT, 'jev', 'SKILL.md');

async function readFrontmatter(p) {
  const raw = await fs.readFile(p, 'utf8');
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return {};
  const fm = m[1];
  const desc = (fm.match(/^description:\s*([\s\S]*?)(?=\n\w[\w-]*:|$)/m) || [])[1]?.trim() || '';
  return { desc: desc.replace(/^"|"$/g, '').replace(/\\"/g, '"') };
}

function extractKeywords(desc) {
  const cut = desc.split(/do not use/i)[0];
  const quoted = [...cut.matchAll(/["']([^"']{3,45})["']/g)].map(m => m[1]);
  const when = (cut.match(/use when(?: asked to)?\s+([^.!?]+)/i) || [])[1] || '';
  const words = when.split(/[,;]| or | and /).map(s => s.trim()).filter(s => s.length >= 3);
  const set = new Set();
  for (const q of quoted.slice(0, 4)) set.add(q);
  for (const w of words.slice(0, 6)) set.add(w);
  return [...set].slice(0, 8).join(', ');
}

async function main() {
  const jevRaw = await fs.readFile(JEV_FILE, 'utf8');
  const headerStart = jevRaw.indexOf('## 유형 분류 및 매칭 키워드');
  const rulesStart = jevRaw.indexOf('## 규칙');
  if (headerStart < 0 || rulesStart < 0) throw new Error('jev SKILL.md 구조를 찾을 수 없음');

  const tableBlock = jevRaw.slice(headerStart, rulesStart);
  const kept = new Map(); // skill -> row text
  for (const line of tableBlock.split(/\r?\n/)) {
    const m = line.match(/^\|\s*([^|]+?)\s*\|\s*([a-z0-9-]+)\s*\|\s*([^|]*)\s*\|$/);
    if (m) kept.set(m[2], line);
  }

  const dirs = (await fs.readdir(USER_ROOT, { withFileTypes: true }))
    .filter(d => d.isDirectory() && d.name !== 'jev')
    .map(d => d.name)
    .sort();

  const rows = [];
  let added = 0;
  for (const name of dirs) {
    if (kept.has(name)) { rows.push(kept.get(name)); continue; }
    const { desc } = await readFrontmatter(path.join(USER_ROOT, name, 'SKILL.md'));
    const kw = extractKeywords(desc);
    rows.push(`| ${name} | ${name} | ${kw || '미분류 - 첫 사용 시 키워드 보강'}`);
    added++;
  }

  const newTable = [
    '## 유형 분류 및 매칭 키워드',
    '',
    '| 유형 | 스킬 | 키워드 |',
    '|---|---|---|',
    ...rows,
    '',
  ].join('\n');

  const out = jevRaw.slice(0, headerStart) + newTable + jevRaw.slice(rulesStart);
  await fs.writeFile(JEV_FILE, out, 'utf8');
  console.log(`스킬 ${dirs.length}개, 신규 추가 ${added}개, 보존 ${kept.size}개`);
  if (added > 0) console.log('신규 행의 유형/키워드는 자동 생성이므로 첫 사용 시 다듬을 것');
}

main().catch(e => { console.error(e.message); process.exit(1); });
