'use strict';
/* A no-network browser API simulation for the public sharing helper. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const text = fs.readFileSync('docs/js/share.js', 'utf8');
const BASE = 'https://ejronin.github.io/1ADAAR/';

function simulate(options = {}) {
  const status = {
    children: [], hidden: true, textContent: '',
    replaceChildren() {this.children.length = 0;this.textContent = '';},
    append(el) {this.children.push(el);}
  };
  const clipboard = [];
  const native = [];
  const inputs = [];
  const ctx = {
    URL, location: {href: BASE},
    window: {},
    navigator: {
      clipboard: options.clipboardDenied ? undefined : {writeText: async value => {clipboard.push(value);}},
      ...(options.native ? {share: async value => {native.push(value);}} : {})
    },
    document: {
      createElement(tag) {
        const item = {
          tag, value: '', focus() {}, selected: false,
          append(child) {this.child = child;},
          setAttribute() {},
          select() {this.selected = true;}
        };
        inputs.push(item);return item;
      }
    }
  };
  vm.runInNewContext(text, ctx, {filename: 'share.js'});
  return {share: ctx.window.OneADAARShare.share, clipboard, native, status, inputs};
}
(async () => {
  const report = BASE + 'players.html#player-' + 'a'.repeat(64);
  const intro = '🐺 Check out my stats on the OneAverageDan WARDOGS Community Server!\n\n📊 View my 1ADAAR player profile:';
  const outro = '🎮 Join the 1AD Discord: https://discord.gg/e9B69UkE53';
  const message = {intro, outro};
  const normal = simulate();
  await normal.share(report, 'Player stats', normal.status, message);
  assert.equal(normal.clipboard.length, 1);
  assert.equal(normal.clipboard[0], [intro, report, outro].join('\n\n'));
  assert.equal(normal.status.hidden, false);
  assert.match(normal.status.textContent, /Profile message copied/);
  const n = simulate({native: true});
  await n.share(report, 'Player stats', n.status, message);
  assert.equal(n.native.length, 1);
  assert.equal(n.native[0].url, report);
  assert.equal(n.native[0].text, [intro, outro].join('\n\n'));
  assert.equal(n.clipboard.length, 0);
  const plain = simulate();
  await plain.share(BASE + 'index.html#match-99', 'Match recap', plain.status);
  assert.equal(plain.clipboard[0], BASE + 'index.html#match-99');
  const denied = simulate({clipboardDenied: true});
  await denied.share(report, 'Player stats', denied.status, message);
  const field = denied.inputs.find(x => x.tag === 'textarea');
  assert.ok(field);
  assert.equal(field.value, [intro, report, outro].join('\n\n'));
  assert.ok(field.selected);
  assert.equal(denied.status.hidden, false);
  console.log('4 browser share-path regression tests passed.');
})().catch(err => {console.error(err);process.exitCode = 1;});
