#!/usr/bin/env node

/**
 * render-ecommerce-html.js
 *
 * Converts the E-Commerce & Marketplaces markdown chapter into a polished HTML page.
 *
 * Features:
 * - markdown-it for Markdown to HTML conversion
 * - Mermaid diagrams rendered in-browser via CDN
 * - highlight.js for code block syntax highlighting
 * - Left sidebar chapter navigator
 * - Right sidebar table of contents with anchor links
 * - Collapsible nav panels
 * - Dark/light theme toggle
 * - Responsive layout
 * - Clean typography
 *
 * Usage:
 *   cd SystemDesign
 *   npm install markdown-it
 *   node scripts/render-ecommerce-html.js
 *
 * Output: dist/ecommerce.html
 */

const fs = require('fs');
const path = require('path');

// Try to load markdown-it, fall back to basic conversion
let md;
try {
  const MarkdownIt = require('markdown-it');
  md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true
  });
} catch (e) {
  console.log('markdown-it not found. Installing...');
  const { execSync } = require('child_process');
  execSync('npm install markdown-it', { cwd: path.resolve(__dirname, '..'), stdio: 'inherit' });
  const MarkdownIt = require('markdown-it');
  md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true
  });
}

const INPUT_FILE = path.resolve(__dirname, '../system-design-mastery/05-real-world-systems/18-ecommerce-marketplaces.md');
const OUTPUT_FILE = path.resolve(__dirname, '../dist/ecommerce.html');

// Read markdown
const markdown = fs.readFileSync(INPUT_FILE, 'utf-8');

// Custom renderer: convert mermaid code blocks to div elements for client-side rendering
const defaultFence = md.renderer.rules.fence;
md.renderer.rules.fence = function (tokens, idx, options, env, self) {
  const token = tokens[idx];
  if (token.info.trim() === 'mermaid') {
    return `<div class="mermaid">${token.content}</div>`;
  }
  // For other code blocks, add language class for highlight.js
  const lang = token.info.trim();
  const langClass = lang ? ` class="language-${lang}"` : '';
  const escaped = token.content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  return `<pre><code${langClass}>${escaped}</code></pre>`;
};

// Render markdown to HTML
let htmlContent = md.render(markdown);

// Extract headings for TOC
const headings = [];
const headingRegex = /<h([1-4])[^>]*id="([^"]*)"[^>]*>(.*?)<\/h[1-4]>/gi;

// Add IDs to headings and collect them for TOC
let headingIndex = 0;
htmlContent = htmlContent.replace(/<h([1-6])>(.*?)<\/h[1-6]>/gi, (match, level, text) => {
  const plainText = text.replace(/<[^>]+>/g, '');
  const id = plainText
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .substring(0, 80);
  const uniqueId = `${id}-${headingIndex++}`;
  headings.push({ level: parseInt(level), text: plainText, id: uniqueId });
  return `<h${level} id="${uniqueId}">${text}</h${level}>`;
});

// Generate TOC HTML
function generateTOC(headings) {
  let toc = '';
  for (const h of headings) {
    if (h.level <= 3) {
      const indent = (h.level - 1) * 16;
      const cls = `toc-h${h.level}`;
      toc += `<a href="#${h.id}" class="${cls}" style="padding-left: ${indent}px">${h.text}</a>\n`;
    }
  }
  return toc;
}

// Generate chapter nav (links to asset files)
const chapters = [
  { name: 'Main Chapter', file: 'ecommerce.html', active: true },
  { name: 'API Reference', file: '../assets/ecommerce/ecommerce-api-examples.md' },
  { name: 'Database Schema', file: '../assets/ecommerce/ecommerce-schema.md' },
  { name: 'Event Catalog', file: '../assets/ecommerce/ecommerce-events.md' },
  { name: 'Glossary', file: '../assets/ecommerce/ecommerce-glossary.md' },
  { name: 'Runbooks', file: '../assets/ecommerce/ecommerce-runbooks.md' },
];

const chapterNav = chapters.map(ch => {
  const cls = ch.active ? 'chapter-link active' : 'chapter-link';
  return `<a href="${ch.file}" class="${cls}">${ch.name}</a>`;
}).join('\n');

const tocHTML = generateTOC(headings);

// Build final HTML
const finalHTML = `<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>18. E-Commerce & Marketplaces — Core Commerce</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" id="hljs-light">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css" id="hljs-dark" disabled>
  <style>
    /* === CSS Variables === */
    :root {
      --bg: #faf9f6;
      --bg-secondary: #f0ede6;
      --text: #2c2c2c;
      --text-secondary: #555;
      --border: #ddd;
      --accent: #d4763a;
      --accent-hover: #c06428;
      --code-bg: #f5f2eb;
      --sidebar-bg: #f5f2eb;
      --sidebar-width: 280px;
      --header-height: 56px;
      --font-body: 'Georgia', 'Palatino Linotype', serif;
      --font-ui: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
      --shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    [data-theme="dark"] {
      --bg: #1a1a2e;
      --bg-secondary: #16213e;
      --text: #e0e0e0;
      --text-secondary: #aaa;
      --border: #333;
      --accent: #e67e22;
      --accent-hover: #f39c12;
      --code-bg: #0f3460;
      --sidebar-bg: #16213e;
      --shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    /* === Reset & Base === */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; font-size: 16px; }
    body {
      font-family: var(--font-body);
      background: var(--bg);
      color: var(--text);
      line-height: 1.7;
      min-height: 100vh;
    }

    /* === Header === */
    .header {
      position: fixed; top: 0; left: 0; right: 0;
      height: var(--header-height);
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 20px;
      z-index: 100;
      box-shadow: var(--shadow);
    }
    .header-brand {
      font-family: var(--font-ui);
      font-weight: 700; font-size: 1rem;
      color: var(--accent);
      text-decoration: none;
    }
    .header-actions { display: flex; gap: 8px; align-items: center; }
    .header-btn {
      background: none; border: 1px solid var(--border);
      padding: 6px 12px; border-radius: 6px; cursor: pointer;
      font-family: var(--font-ui); font-size: 0.85rem;
      color: var(--text); transition: all 0.2s;
    }
    .header-btn:hover { background: var(--accent); color: #fff; border-color: var(--accent); }

    /* === Progress Bar === */
    .progress-bar {
      position: fixed; top: var(--header-height); left: 0;
      height: 3px; background: var(--accent);
      z-index: 101; transition: width 0.1s;
      width: 0%;
    }

    /* === Layout === */
    .page-shell {
      display: flex;
      margin-top: var(--header-height);
      min-height: calc(100vh - var(--header-height));
    }

    /* === Left Sidebar === */
    .sidebar-left {
      width: var(--sidebar-width);
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border);
      position: fixed; top: var(--header-height); bottom: 0; left: 0;
      overflow-y: auto; padding: 20px 16px;
      transition: transform 0.3s;
      z-index: 50;
    }
    .sidebar-left.collapsed { transform: translateX(-100%); }
    .sidebar-left h3 {
      font-family: var(--font-ui); font-size: 0.75rem;
      text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--text-secondary); margin-bottom: 12px;
    }
    .chapter-link {
      display: block; padding: 8px 12px; margin-bottom: 4px;
      border-radius: 6px; text-decoration: none;
      font-family: var(--font-ui); font-size: 0.9rem;
      color: var(--text); transition: all 0.2s;
    }
    .chapter-link:hover { background: var(--bg); }
    .chapter-link.active { background: var(--accent); color: #fff; font-weight: 600; }

    /* === Right Sidebar (TOC) === */
    .sidebar-right {
      width: var(--sidebar-width);
      position: fixed; top: var(--header-height); bottom: 0; right: 0;
      overflow-y: auto; padding: 20px 16px;
      border-left: 1px solid var(--border);
      background: var(--sidebar-bg);
      transition: transform 0.3s;
      z-index: 50;
    }
    .sidebar-right.collapsed { transform: translateX(100%); }
    .sidebar-right h3 {
      font-family: var(--font-ui); font-size: 0.75rem;
      text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--text-secondary); margin-bottom: 12px;
    }
    .toc-h1, .toc-h2, .toc-h3 {
      display: block; padding: 4px 8px; margin-bottom: 2px;
      border-radius: 4px; text-decoration: none;
      font-family: var(--font-ui); font-size: 0.8rem;
      color: var(--text-secondary); transition: all 0.2s;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .toc-h1 { font-weight: 700; color: var(--text); font-size: 0.85rem; }
    .toc-h2 { font-weight: 600; }
    .toc-h3 { font-size: 0.75rem; }
    .toc-h1:hover, .toc-h2:hover, .toc-h3:hover {
      background: var(--bg); color: var(--accent);
    }
    .toc-h1.active, .toc-h2.active, .toc-h3.active {
      color: var(--accent); font-weight: 700;
    }

    /* === TOC Search/Filter === */
    .toc-filter {
      width: 100%; padding: 6px 10px; margin-bottom: 12px;
      border: 1px solid var(--border); border-radius: 6px;
      font-family: var(--font-ui); font-size: 0.8rem;
      background: var(--bg); color: var(--text);
    }

    /* === Main Content === */
    .main-content {
      flex: 1;
      margin-left: var(--sidebar-width);
      margin-right: var(--sidebar-width);
      padding: 40px 60px 80px;
      max-width: 100%;
      transition: margin 0.3s;
    }
    .main-content.left-collapsed { margin-left: 0; }
    .main-content.right-collapsed { margin-right: 0; }
    .main-content.both-collapsed { margin-left: 0; margin-right: 0; }

    /* === Typography === */
    h1 { font-size: 2.2rem; margin: 0 0 24px; border-bottom: 3px solid var(--accent); padding-bottom: 12px; }
    h2 { font-size: 1.6rem; margin: 48px 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; color: var(--accent); }
    h3 { font-size: 1.3rem; margin: 32px 0 12px; }
    h4 { font-size: 1.1rem; margin: 24px 0 8px; }
    p { margin-bottom: 16px; }
    ul, ol { margin: 0 0 16px 24px; }
    li { margin-bottom: 4px; }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; }
    strong { font-weight: 700; }
    hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

    /* === Code === */
    code {
      font-family: var(--font-mono);
      background: var(--code-bg);
      padding: 2px 6px; border-radius: 4px;
      font-size: 0.85em;
    }
    pre {
      background: var(--code-bg);
      padding: 16px 20px; border-radius: 8px;
      overflow-x: auto; margin-bottom: 20px;
      border: 1px solid var(--border);
    }
    pre code {
      background: none; padding: 0;
      font-size: 0.85rem; line-height: 1.5;
    }

    /* === Tables === */
    table {
      width: 100%; border-collapse: collapse;
      margin-bottom: 20px; font-size: 0.9rem;
    }
    th, td {
      padding: 10px 14px; border: 1px solid var(--border);
      text-align: left; vertical-align: top;
    }
    th {
      background: var(--bg-secondary);
      font-family: var(--font-ui);
      font-weight: 600; font-size: 0.85rem;
    }
    tr:nth-child(even) { background: var(--bg-secondary); }

    /* === Mermaid === */
    .mermaid {
      margin: 20px 0; padding: 20px;
      background: var(--bg-secondary);
      border-radius: 8px; border: 1px solid var(--border);
      text-align: center; overflow-x: auto;
    }

    /* === Blockquote === */
    blockquote {
      border-left: 4px solid var(--accent);
      padding: 12px 20px; margin: 16px 0;
      background: var(--bg-secondary);
      border-radius: 0 8px 8px 0;
    }

    /* === Responsive === */
    @media (max-width: 1200px) {
      .sidebar-right { display: none; }
      .main-content { margin-right: 0; }
    }
    @media (max-width: 900px) {
      .sidebar-left { display: none; }
      .main-content { margin-left: 0; padding: 24px 20px; }
    }
    @media (max-width: 600px) {
      h1 { font-size: 1.6rem; }
      h2 { font-size: 1.3rem; }
      table { font-size: 0.8rem; }
      th, td { padding: 6px 8px; }
    }

    /* === Scroll to top === */
    .scroll-top {
      position: fixed; bottom: 24px; right: 24px;
      width: 44px; height: 44px; border-radius: 50%;
      background: var(--accent); color: #fff;
      border: none; cursor: pointer; font-size: 1.2rem;
      display: none; align-items: center; justify-content: center;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      z-index: 200; transition: opacity 0.3s;
    }
    .scroll-top.visible { display: flex; }
  </style>
</head>
<body>
  <!-- Header -->
  <header class="header">
    <a href="#" class="header-brand">System Design Mastery</a>
    <div class="header-actions">
      <button class="header-btn" id="toggle-left" title="Toggle chapter nav">&#9776; Chapters</button>
      <button class="header-btn" id="toggle-right" title="Toggle table of contents">TOC &#9776;</button>
      <button class="header-btn" id="toggle-theme" title="Toggle dark/light theme">&#9790; Theme</button>
    </div>
  </header>

  <!-- Progress Bar -->
  <div class="progress-bar" id="progress-bar"></div>

  <!-- Page Shell -->
  <div class="page-shell">
    <!-- Left Sidebar: Chapter Navigator -->
    <nav class="sidebar-left" id="sidebar-left">
      <h3>Chapter Resources</h3>
      ${chapterNav}
    </nav>

    <!-- Main Content -->
    <main class="main-content" id="main-content">
      ${htmlContent}
    </main>

    <!-- Right Sidebar: Table of Contents -->
    <aside class="sidebar-right" id="sidebar-right">
      <h3>Table of Contents</h3>
      <input type="text" class="toc-filter" id="toc-filter" placeholder="Filter sections...">
      <div id="toc-links">
        ${tocHTML}
      </div>
    </aside>
  </div>

  <!-- Scroll to Top -->
  <button class="scroll-top" id="scroll-top" title="Scroll to top">&uarr;</button>

  <!-- Scripts -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/sql.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/json.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/bash.min.js"></script>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({
      startOnLoad: true,
      theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'default',
      securityLevel: 'loose',
      flowchart: { useMaxWidth: true, htmlLabels: true },
      sequence: { useMaxWidth: true }
    });
  </script>
  <script>
    // Highlight.js
    hljs.highlightAll();

    // Theme toggle
    const themeBtn = document.getElementById('toggle-theme');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('sd-theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateHljsTheme(savedTheme);

    themeBtn.addEventListener('click', () => {
      const current = html.getAttribute('data-theme');
      const next = current === 'light' ? 'dark' : 'light';
      html.setAttribute('data-theme', next);
      localStorage.setItem('sd-theme', next);
      updateHljsTheme(next);
    });

    function updateHljsTheme(theme) {
      document.getElementById('hljs-light').disabled = theme === 'dark';
      document.getElementById('hljs-dark').disabled = theme === 'light';
    }

    // Sidebar toggles
    const leftSidebar = document.getElementById('sidebar-left');
    const rightSidebar = document.getElementById('sidebar-right');
    const mainContent = document.getElementById('main-content');

    document.getElementById('toggle-left').addEventListener('click', () => {
      leftSidebar.classList.toggle('collapsed');
      mainContent.classList.toggle('left-collapsed');
    });

    document.getElementById('toggle-right').addEventListener('click', () => {
      rightSidebar.classList.toggle('collapsed');
      mainContent.classList.toggle('right-collapsed');
    });

    // Progress bar
    window.addEventListener('scroll', () => {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = window.scrollY;
      const progress = docHeight > 0 ? (scrolled / docHeight) * 100 : 0;
      document.getElementById('progress-bar').style.width = progress + '%';

      // Scroll to top button
      const scrollBtn = document.getElementById('scroll-top');
      if (scrolled > 500) {
        scrollBtn.classList.add('visible');
      } else {
        scrollBtn.classList.remove('visible');
      }
    });

    // Scroll to top
    document.getElementById('scroll-top').addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // TOC filter
    document.getElementById('toc-filter').addEventListener('input', (e) => {
      const filter = e.target.value.toLowerCase();
      const links = document.querySelectorAll('#toc-links a');
      links.forEach(link => {
        const text = link.textContent.toLowerCase();
        link.style.display = text.includes(filter) ? 'block' : 'none';
      });
    });

    // Active TOC highlighting on scroll
    const tocLinks = document.querySelectorAll('#toc-links a');
    const headingElements = [];
    tocLinks.forEach(link => {
      const id = link.getAttribute('href').substring(1);
      const el = document.getElementById(id);
      if (el) headingElements.push({ el, link });
    });

    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          let current = null;
          for (const { el, link } of headingElements) {
            if (el.getBoundingClientRect().top <= 100) {
              current = link;
            }
          }
          tocLinks.forEach(l => l.classList.remove('active'));
          if (current) current.classList.add('active');
          ticking = false;
        });
        ticking = true;
      }
    });
  </script>
</body>
</html>`;

// Write output
fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
fs.writeFileSync(OUTPUT_FILE, finalHTML, 'utf-8');

console.log('HTML generated successfully!');
console.log('Output: ' + OUTPUT_FILE);
console.log('Open in browser: file://' + OUTPUT_FILE);
