// JEV 중복/유사도 검증 스크립트
// 용법: node check-duplicates.mjs <후보 스킬 디렉터리> [더...]
// 후보 스킬의 description을 기존 스킬(user + builtin) 전체와 비교해 유사도 상위를 보고한다.
// 유사도 = description 토큰 Jaccard (임베딩 대신 로컬 경량 근사). 0.5 이상이면 본문 대조 필요.
import { promises as fs } from 'node:fs';
import path from 'node:path';

const SKILLS_ROOT = 'C:/Users/soka7/.aside/u/0/skills';
const STOP = new Set(['the','and','for','use','when','with','that','this','not','you','your','are','have','has','from','asked','using','or','to','of','in','on','a','an']);

function tokenize(s) {
  const t = s.toLowerCase().replace(/[^a-z0-9가-힣]+/g, ' ').split(/\s+/);
  return new Set(t.filter(w => w.length >= 2 && !STOP.has(w)));
}

function jaccard(a, b) {
  let inter = 0;
  for (const x of a) if (b.has(x)) inter++;
  const union = new Set([...a, ...b]).size;
  return union === 0 ? 0 : inter / union;
}

async function readDesc(p) {
  const raw = await fs.readFile(p, 'utf8');
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) return '';
  const fm = m[1];
  const d = (fm.match(/^description:\s*([\s\S]*?)(?=\n\w[\w-]*:|$)/m) || [])[1] || '';
  return d.trim().replace(/^"|"$/g, '').replace(/\\"/g, '"');
}

async function globSkillFiles(dir) {
  const files = [];
  const stack = [dir];
  while (stack.length) {
    const d = stack.pop();
    let entries;
    try { entries = await fs.readdir(d, { withFileTypes: true }); } catch { continue; }
    for (const e of entries) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) stack.push(p);
      else if (e.name === 'SKILL.md') files.push(p);
    }
  }
  return files;
}

async function collectExisting() {
  const out = [];
  for (const base of [path.join(SKILLS_ROOT, 'user'), path.join(SKILLS_ROOT, 'builtin')]) {
    for (const f of await globSkillFiles(base)) {
      out.push({ file: f, name: path.basename(path.dirname(f)), desc: await readDesc(f) });
    }
  }
  return out;
}

async function main() {
  const candidates = process.argv.slice(2);
  if (candidates.length === 0) throw new Error('후보 스킬 디렉터리를 인자로 넘기세요');
  const existing = await collectExisting();
  console.log(`기존 스킬 ${existing.length}개와 비교\n`);

  for (const candDir of candidates) {
    const candFile = path.join(candDir, 'SKILL.md');
    const candName = path.basename(candDir);
    const candDesc = await readDesc(candFile);
    const candTokens = tokenize(candDesc + ' ' + candName.replace(/-/g, ' '));

    const scores = existing
      .filter(e => !e.file.startsWith(path.resolve(candDir)))
      .map(e => ({ name: e.name, scope: e.file.includes('\\builtin\\') ? 'builtin' : 'user', score: jaccard(candTokens, tokenize(e.desc + ' ' + e.name.replace(/-/g, ' '))) }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);

    console.log(`=== 후보: ${candName} ===`);
    for (const s of scores) {
      const flag = s.score >= 0.5 ? '  <-- 중복 가능성, 본문 대조 필요' : '';
      console.log(`  ${(s.score * 100).toFixed(0).padStart(3)}%  [${s.scope}] ${s.name}${flag}`);
    }
    console.log('');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
