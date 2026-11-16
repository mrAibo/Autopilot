#!/usr/bin/env node
// Execute the actual Dashboard script in a minimal DOM-free Node sandbox.
// Never load remote scripts, install packages, or access the network.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const page = fs.readFileSync(path.join(__dirname, '..', 'skills', 'autopilot',
    'phases', 'dashboard-template.html'), 'utf8');
const scripts = [...page.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
    .map(match => match[1]);
const code = scripts.find(s => s.includes('function render(lang)') && s.includes('const STAGE_IDS'));
assert.ok(code, 'Dashboard render script not found');

function render(state, options = {}) {
  const app = {innerHTML: '', classList: {add() {}, remove() {}},
               addEventListener() {}, querySelectorAll() {return []}};
  const link = {hidden: true, parentNode: {hidden: true}, textContent: ''};
  const document = {
    documentElement: {setAttribute() {}, removeAttribute() {}, lang: 'ru'},
    getElementById(id) {return id === 'app' ? app : id === 'link' ? link : null},
    querySelectorAll() {return []},
    addEventListener() {},
    createElement() {return {remove() {}}},
    title: ''
  };
  const sandbox = {
    STATE: state, document, navigator: {language: 'ru-RU'},
    location: {protocol: 'file:'},
    localStorage: {getItem(key) {return key === 'autopilot-lang' ? options.lang || null : key === 'autopilot-view' ? options.view || null : null}, setItem() {}, removeItem() {}},
    matchMedia() {return {matches: false, addEventListener() {}}},
    setTimeout() {return 1}, clearTimeout() {}, setInterval() {},
    Date, Intl, Math, Number, String, Object, Array, JSON, console,
    scrollY: 0, scrollTo() {}, addEventListener() {},
  };
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, {timeout: 5000, filename: 'dashboard-template-inline.js'});
  if (options.bootError) {
    sandbox.__testError = options.bootError;
    vm.runInContext('bootFail(__testError)', sandbox, {timeout: 2000});
  }
  return {html: app.innerHTML, title: document.title};
}

const injection = '<img src=x onerror=alert(1)>';
const base = {
  title: 'Normal project', slug: 'demo', dir: '2026-demo--wip',
  mode: 'semi', depth: 'strict', rev: 1,
  startedAt: '2026-10-26T08:00:00Z',
  updatedAt: '2026-10-26T09:00:00Z',
  finishedAt: null,
  stages: ['preflight','manifest','briefing','spec','plan','build','review','final']
    .map(id => ({id, status: id === 'build' ? 'active' : 'pending'})),
  tickets: [{id:'01',title:'Safe task', status:'pending',wave:1,blockedBy:[]}],
  requirements: {total:0,dropped:0}, gates: {}, log: []
};
// Темы показывают разные поля («Сейчас» не показывает, например, волну): сырой тег не должен
// попасть ни в одну тему, а экранированным текстом поле обязано быть видно хотя бы в одной.
const VIEWS = ['now','overview','timeline','requirements','resources','summary','classic','compact','quality'];
function assertEscaped(name, state, expected) {
  let shown = false, shownExpected = !expected;
  for (const view of VIEWS) {
    const {html, title} = render(state, {view});
    assert.ok(html.includes('class="cockpit-rail"'), name + ' [' + view + ']: dashboard render did not complete');
    assert.ok(!html.includes(injection), name + ' [' + view + ']: raw hostile tag reached innerHTML');
    assert.ok(title.includes('autopilot'), name + ' [' + view + ']: document title missing');
    shown = shown || html.includes('&lt;img');
    shownExpected = shownExpected || html.includes(expected);
  }
  assert.ok(shown, name + ': hostile content absent as escaped text in every view');
  assert.ok(shownExpected, name + ': expected element not shown');
}
assertEscaped('test counts', {...base, tests: {passed: injection, failed: 0}});
assertEscaped('failed test count', {...base, tests: {passed: 3, failed: injection}});
assertEscaped('task wave', {...base,
  tickets: [{...base.tickets[0], wave: injection}]});
assertEscaped('gate error', {...base,
  gates: {G1: {ok: false, open: injection}}});
assertEscaped('gate accepted total', {...base,
  gates: {G1: {ok: true, total: injection}}});
assertEscaped('gate planning error', {...base,
  gates: {G3: {ok: false, problems: injection}}});

// Arbitrary ticket text is already escaped and must remain visible.
assertEscaped('task title', {...base,
  tickets: [{...base.tickets[0], title: injection}]});

const englishState = {...base, gates: {G3: {ok: false, problems: injection}}};
let englishShown = false;
for (const view of VIEWS) {
  const english = render(englishState, {lang: 'en', view});
  assert.ok(english.html.includes('class="cockpit-rail"'));
  assert.ok(!english.html.includes(injection));
  englishShown = englishShown || english.html.includes('&lt;img');
}
assert.ok(englishShown, 'english: hostile content absent as escaped text in every view');

const boot = render(base, {bootError: injection});
assert.ok(boot.html.includes('&lt;img'));
assert.ok(!boot.html.includes(injection));

const normal = render({...base, tests: {passed: 4, failed: 0}});
assert.ok(normal.html.includes('Safe task'));
assert.ok(normal.html.includes('4'));
assert.ok(normal.html.includes('cockpit-rail'));
console.log('Dashboard rendered-state injection checks OK (7 hostile, 1 English, 1 boot error, 1 normal)');
