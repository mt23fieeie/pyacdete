import fs from 'node:fs';
import path from 'node:path';
import { marked } from 'marked';
import katex from 'katex';

const { version } = JSON.parse(fs.readFileSync('package.json', 'utf8'));

const pages = [
  {
    name: 'h1_response', source: 'reference.md', file: 'index.html',
    description: 'Python Acoustic Device Testing — H1 loudspeaker magnitude and phase API, theory, parameters and a verified SMARD example.',
    summary: 'H1 loudspeaker magnitude and phase response API reference.',
    reviewNotice: ' Its content has been reviewed by a human, but is not guaranteed to be free of errors.'
  },
  {
    name: 'single_tone_thd', source: 'reference-thd.md', file: 'single-tone-thd.html',
    description: 'Python Acoustic Device Testing — single-tone loudspeaker total harmonic distortion API.',
    summary: 'Single-tone loudspeaker total harmonic distortion API reference.',
    reviewNotice: ''
  },
  {
    name: 'estimate_delay', source: 'reference-delay.md', file: 'delay-estimation.html',
    description: 'Time-domain cross-correlation delay estimation API with a reproducible SMARD 2000 example.',
    summary: 'Time-domain delay estimation API reference.',
    reviewNotice: ''
  }
];

function renderMarkdown(source) {
  const equations = [];
  let markdown = fs.readFileSync(source, 'utf8');
  markdown = markdown.replace(/\$\$([\s\S]*?)\$\$/g, (_, tex) => {
    const key = `PYACDETEMATHBLOCK${equations.length}END`;
    equations.push({ key, tex: tex.trim(), display: true });
    return `\n\n${key}\n\n`;
  });
  markdown = markdown.replace(/\$([^\n$]+)\$/g, (_, tex) => {
    const key = `PYACDETEMATHINLINE${equations.length}END`;
    equations.push({ key, tex, display: false });
    return key;
  });
  let body = marked.parse(markdown, { gfm: true }).replace(/\b(href|src)="docs\//g, '$1="');
  for (const eq of equations) {
    const rendered = katex.renderToString(eq.tex, {
      displayMode: eq.display, throwOnError: true, trust: false,
      output: 'htmlAndMathml', strict: 'error'
    });
    body = eq.display
      ? body.replace(`<p>${eq.key}</p>`, `<div class="math-block">${rendered}</div>`)
      : body.replace(eq.key, rendered);
  }
  const headings = [];
  body = body.replace(/<h([1-3])>([\s\S]*?)<\/h\1>/g, (_, level, text) => {
    const plain = text.replace(/<[^>]+>/g, '');
    const id = plain.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    headings.push({ level: Number(level), text: plain, id });
    return `<h${level} id="${id}">${text}<a class="anchor" href="#${id}" aria-label="Link to ${plain}">#</a></h${level}>`;
  });
  body = body.replace(/<table>/g, '<div class="table-scroll"><table>').replace(/<\/table>/g, '</table></div>');
  body = body.replace(/<pre>/g, '<div class="code-block"><button class="copy-code" type="button" aria-label="Copy code">Copy</button><pre>').replace(/<\/pre>/g, '</pre></div>');
  const parameters = [...body.matchAll(/<dt id="(param-[^"]+)"><code>([^<]+)<\/code>/g)]
    .map(([, id, text]) => ({ level: 3, text, id }));
  return { body, headings, parameters };
}

function buildPage(page) {
  const { body, headings, parameters } = renderMarkdown(page.source);
  const sections = headings.filter(h => h.level === 2);
  const toc = sections.map(h => `<li><a href="#${h.id}">${h.text}</a></li>`).join('');
  const sectionLinks = sections.map(h => `<a href="#${h.id}">${h.text}</a>`).join('');
  const home = page.file === 'index.html' ? '#main' : './';
  const navigation = pages.map(p => p === page
    ? `<a class="function-link selected" href="#main" aria-current="page">${p.name}</a><div class="side-sections">${sectionLinks}</div>`
    : `<a class="function-link" href="${p.file}">${p.name}</a>`).join('\n');
  const html = `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="${page.description}">
<meta name="theme-color" content="#f7f9fc">
<title>pyacdete.loudspeaker.${page.name} — pyacdete API Reference</title>
<link rel="stylesheet" href="assets/katex/katex.min.css"><link rel="stylesheet" href="assets/style.css">
<script src="assets/app.js" defer></script>
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="topbar"><div class="topbar-inner">
<button class="menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false">☰</button>
<a class="brand" href="${home}">pyacdete<span class="version">${version}</span></a>
<span class="library-name">Python Acoustic Device Testing</span>
<div class="search-wrap"><label class="sr-only" for="doc-search">Find in this reference</label><input id="doc-search" type="search" placeholder="Find in this reference…" autocomplete="off"><kbd>/</kbd><div id="search-results" role="list" hidden></div></div>
<span class="language" aria-label="Documentation language">EN</span>
</div></header>
<div class="layout">
<aside class="sidebar" aria-label="Main navigation">
<a class="side-home" href="${home}">API reference</a><p class="sidebar-caption">Python Acoustic Device Testing</p>
<nav><p class="nav-group">Loudspeaker</p>${navigation}</nav>
<div class="sidebar-footer"><span>pyacdete ${version}</span><span>English documentation</span></div>
</aside>
<main id="main" class="document"><div class="breadcrumbs"><a href="${home}">API reference</a><span>›</span><span>loudspeaker</span></div><div class="page-actions"><a href="downloads/loudspeaker.py" download>View source</a></div>
${body}
<footer class="page-footer"><p>Python Acoustic Device Testing · pyacdete ${version}</p><p>${page.summary}</p><p>This website was built with assistance from ChatGPT.${page.reviewNotice} Please send feedback to <a href="mailto:1220010941@student.must.edu.mo">1220010941@student.must.edu.mo</a>.</p></footer>
</main>
<aside class="on-this-page" aria-label="On this page"><p>On this page</p><nav><ul>${toc}</ul></nav><a class="back-top" href="#main">Back to top ↑</a></aside>
</div>
<div class="menu-scrim" hidden></div>
<script type="application/json" id="search-index">${JSON.stringify([...headings, ...parameters]).replace(/</g,'\\u003c')}</script>
</body></html>`;
  fs.writeFileSync(path.join('docs', page.file), html);
  console.log(`Built ${page.file}: ${headings.length} headings.`);
}

fs.mkdirSync('docs/assets/katex', { recursive: true });
fs.copyFileSync('node_modules/katex/dist/katex.min.css', 'docs/assets/katex/katex.min.css');
fs.cpSync('node_modules/katex/dist/fonts', 'docs/assets/katex/fonts', { recursive: true });
fs.copyFileSync('python/pyacdete/pyacdete/loudspeaker.py', 'docs/downloads/loudspeaker.py');
fs.copyFileSync('python/pyacdete/examples/smard_delay.py', 'docs/downloads/smard_delay.py');
for (const page of pages) buildPage(page);
