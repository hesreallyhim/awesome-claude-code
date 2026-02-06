#!/usr/bin/env node
/**
 * Agent System Test — Verifies all components are properly configured
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

let passed = 0;
let failed = 0;

function check(name, condition) {
  if (condition) {
    console.log(`  ✓ ${name}`);
    passed++;
  } else {
    console.log(`  ✗ ${name}`);
    failed++;
  }
}

function fileExists(p) {
  return fs.existsSync(path.join(ROOT, p));
}

console.log('');
console.log('AI Agent System — Verification');
console.log('══════════════════════════════════');

// ── Skills ────────────────────────────────────
console.log('\nSkills (knowledge base):');
const skills = ['x', 'linkedin', 'github', 'video-editing', 'screen-recording', 'coding', 'research', 'promo'];
for (const s of skills) {
  check(`skills/${s}-skill.md`, fileExists(`skills/${s}-skill.md`));
}

// ── Claude Skills (slash commands) ────────────
console.log('\nClaude Skills (slash commands):');
const slashCmds = ['train-skill', 'run-skill', 'full-pipeline', 'browse', 'create-video', 'post-x', 'post-linkedin', 'publish-github'];
for (const s of slashCmds) {
  check(`/claude/skills/${s}/SKILL.md`, fileExists(`.claude/skills/${s}/SKILL.md`));
}

// ── Subagents ─────────────────────────────────
console.log('\nSubagents:');
const agents = ['researcher', 'coder', 'publisher', 'video-creator', 'promoter', 'skill-trainer'];
for (const a of agents) {
  check(`.claude/agents/${a}.md`, fileExists(`.claude/agents/${a}.md`));
}

// ── Hooks ─────────────────────────────────────
console.log('\nHooks:');
check('.claude/settings.json', fileExists('.claude/settings.json'));
check('scripts/hooks/pre-bash.sh', fileExists('scripts/hooks/pre-bash.sh'));
check('scripts/hooks/post-edit.sh', fileExists('scripts/hooks/post-edit.sh'));
check('scripts/hooks/post-bash.sh', fileExists('scripts/hooks/post-bash.sh'));
check('scripts/hooks/notify.sh', fileExists('scripts/hooks/notify.sh'));

// ── Scripts ───────────────────────────────────
console.log('\nScripts:');
check('scripts/browser.js', fileExists('scripts/browser.js'));
check('scripts/screenshot.js', fileExists('scripts/screenshot.js'));
check('scripts/record-demo.js', fileExists('scripts/record-demo.js'));
check('scripts/setup.sh', fileExists('scripts/setup.sh'));
check('scripts/run-pipeline.sh', fileExists('scripts/run-pipeline.sh'));

// ── Remotion ──────────────────────────────────
console.log('\nRemotion video project:');
check('src/index.ts', fileExists('src/index.ts'));
check('src/Root.tsx', fileExists('src/Root.tsx'));
check('src/compositions/ExplainerVideo.tsx', fileExists('src/compositions/ExplainerVideo.tsx'));
check('src/compositions/DemoVideo.tsx', fileExists('src/compositions/DemoVideo.tsx'));
check('src/compositions/ShortVideo.tsx', fileExists('src/compositions/ShortVideo.tsx'));
check('src/components/Title.tsx', fileExists('src/components/Title.tsx'));
check('src/components/CodeBlock.tsx', fileExists('src/components/CodeBlock.tsx'));
check('src/components/Caption.tsx', fileExists('src/components/Caption.tsx'));
check('src/components/Transition.tsx', fileExists('src/components/Transition.tsx'));

// ── Config ────────────────────────────────────
console.log('\nConfiguration:');
check('CLAUDE.md', fileExists('CLAUDE.md'));
check('config/.env.example', fileExists('config/.env.example'));
check('.gitignore', fileExists('.gitignore'));
check('package.json', fileExists('package.json'));

// ── Dependencies ──────────────────────────────
console.log('\nDependencies:');
check('node_modules/puppeteer-core', fileExists('node_modules/puppeteer-core'));

// ── Summary ───────────────────────────────────
console.log('\n══════════════════════════════════');
console.log(`Results: ${passed} passed, ${failed} failed, ${passed + failed} total`);
if (failed === 0) {
  console.log('All checks passed!');
} else {
  console.log(`${failed} item(s) need attention.`);
}
console.log('');
process.exit(failed > 0 ? 1 : 0);
