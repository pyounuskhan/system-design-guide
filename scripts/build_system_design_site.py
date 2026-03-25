#!/usr/bin/env python3
from __future__ import annotations

import html
import math
import re
import shutil
import subprocess
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, BaseLoader, select_autoescape
from markdown import Markdown


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = ROOT / "system-design-mastery"
OUTPUT_ROOT = ROOT / "system-design-site"
DIAGRAMS_ROOT = OUTPUT_ROOT / "assets" / "diagrams"


PART_DEFINITIONS = [
    {
        "key": "00-design-foundations",
        "order": 0,
        "name": "Part 0: System Design Foundations & Principles",
        "short_name": "Design Foundations",
        "description": "Master the conceptual backbone: design principles, patterns, architecture styles, microservices, scalability, data design, distributed systems, networking, security, observability, deployment, and interview thinking.",
        "theme_class": "part-0",
    },
    {
        "key": "01-foundations",
        "order": 1,
        "name": "Part 1: Foundations",
        "short_name": "Foundations",
        "description": "Build the mental model: what system design is, how requirements work, and how to estimate the shape of a system before implementation.",
        "theme_class": "part-1",
    },
    {
        "key": "02-building-blocks",
        "order": 2,
        "name": "Part 2: Core Building Blocks",
        "short_name": "Core Building Blocks",
        "description": "Learn the components that appear repeatedly in production systems: networking, databases, caching, queues, load balancing, and storage.",
        "theme_class": "part-2",
    },
    {
        "key": "03-distributed-systems",
        "order": 3,
        "name": "Part 3: Distributed Systems",
        "short_name": "Distributed Systems",
        "description": "Focus on the hard parts of scale: consistency, partition tolerance, resilience, and the behavior of systems under failure.",
        "theme_class": "part-3",
    },
    {
        "key": "04-architectural-patterns",
        "order": 4,
        "name": "Part 4: Architectural Patterns",
        "short_name": "Architectural Patterns",
        "description": "Compare common architecture choices and learn when patterns like microservices, event-driven systems, and CQRS actually help.",
        "theme_class": "part-4",
    },
    {
        "key": "05-real-world-systems",
        "order": 5,
        "name": "Part 5: Real-World System Design Examples",
        "short_name": "Real-World Examples",
        "description": "Use a domain-driven atlas of real-world systems across commerce, fintech, social, infrastructure, healthcare, gaming, adtech, and travel to compare architectures in context.",
        "theme_class": "part-5",
    },
    {
        "key": "06-advanced-architecture",
        "order": 6,
        "name": "Part 6: Advanced Architecture",
        "short_name": "Advanced Architecture",
        "description": "Move into production-grade thinking: observability, platform operations, security, cost, and AI-native system design.",
        "theme_class": "part-6",
    },
]


INDEX_TEMPLATE = """<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>System Design Mastery</title>
  <meta name="description" content="A structured roadmap that takes software engineers from beginner system design knowledge to advanced systems architect thinking.">
  <link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/css/styles.css">
  <script defer src="assets/js/app.js"></script>
</head>
<body class="page-home">
  <div class="progress-bar" aria-hidden="true"><span></span></div>

  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">
        <span class="brand-mark">SD</span>
        <span class="brand-text">
          <strong>System Design Mastery</strong>
          <small>Static learning site</small>
        </span>
      </a>
      <nav class="header-nav">
        <a href="#roadmap">Roadmap</a>
        <a href="#chapter-directory">Chapters</a>
        <a href="#study-method">Study Method</a>
      </nav>
      <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle dark mode">
        <span data-theme-label>Dark mode</span>
      </button>
    </div>
  </header>

  <main>
    <section class="hero-section">
      <div class="hero-copy">
        <p class="eyebrow">A structured roadmap for serious system design learning</p>
        <h1>System Design Mastery</h1>
        <p class="hero-lead">
          Learn system design from first principles to architect-level reasoning with a guided sequence
          of chapters, case studies, diagrams, real-world trade-offs, and interview-focused thinking.
        </p>
        <p class="hero-support">
          This site is built from the repository’s Markdown source and organized like a modern technical
          book: start from fundamentals, move through building blocks and distributed systems, and end
          with production architecture, platform operations, and AI-era design.
        </p>
        <div class="hero-actions">
          <a class="button button-primary" href="chapters/{{ first_chapter.slug }}.html">Start with Chapter 1</a>
          <a class="button button-secondary" href="#chapter-directory">Browse the full curriculum</a>
        </div>
      </div>
      <aside class="hero-panel">
        <div class="hero-stat-grid">
          <article class="stat-card">
            <strong>{{ total_chapters }}</strong>
            <span>Detailed chapters</span>
          </article>
          <article class="stat-card">
            <strong>6</strong>
            <span>Learning parts</span>
          </article>
          <article class="stat-card">
            <strong>Beginner</strong>
            <span>To advanced progression</span>
          </article>
          <article class="stat-card">
            <strong>Architect</strong>
            <span>Trade-off driven thinking</span>
          </article>
        </div>
      </aside>
    </section>

    <section class="content-section" id="audience">
      <div class="section-heading">
        <p class="eyebrow">Who this is for</p>
        <h2>Designed for engineers who want to think in systems</h2>
      </div>
      <div class="card-grid card-grid-two">
        {% for audience in audience_cards %}
        <article class="info-card">
          <h3>{{ audience.title }}</h3>
          <p>{{ audience.text }}</p>
        </article>
        {% endfor %}
      </div>
    </section>

    <section class="content-section" id="roadmap">
      <div class="section-heading">
        <p class="eyebrow">Learning journey</p>
        <h2>A step-by-step path from beginner to systems architect</h2>
      </div>
      <div class="roadmap-grid">
        {% for part in parts %}
        <article class="roadmap-card {{ part.theme_class }}">
          <div class="roadmap-meta">Part {{ part.order }}</div>
          <h3>{{ part.short_name }}</h3>
          <p>{{ part.description }}</p>
          <div class="roadmap-footer">
            <span>{{ part.chapters|length }} chapters</span>
            <a href="#part-{{ part.order }}">Open part</a>
          </div>
        </article>
        {% endfor %}
      </div>
    </section>

    <section class="content-section" id="why-learn">
      <div class="section-heading">
        <p class="eyebrow">Why learn this</p>
        <h2>Build the judgment required for real architecture work</h2>
      </div>
      <div class="card-grid card-grid-two">
        {% for point in value_points %}
        <article class="info-card">
          <h3>{{ point.title }}</h3>
          <p>{{ point.text }}</p>
        </article>
        {% endfor %}
      </div>
    </section>

    <section class="content-section chapter-directory" id="chapter-directory">
      <div class="section-heading">
        <p class="eyebrow">Chapter directory</p>
        <h2>Read the book in order or jump to a specific topic</h2>
      </div>
      <div class="directory-toolbar">
        <label class="search-field">
          <span>Filter chapters</span>
          <input
            type="search"
            placeholder="Search by chapter title or part"
            data-filter-input
            data-filter-target="#chapter-directory"
          >
        </label>
      </div>

      {% for part in parts %}
      <section class="directory-part {{ part.theme_class }}" id="part-{{ part.order }}" data-filter-group>
        <div class="directory-part-header">
          <div>
            <p class="eyebrow">Part {{ part.order }}</p>
            <h3>{{ part.short_name }}</h3>
          </div>
          <p>{{ part.description }}</p>
        </div>
        <div class="chapter-card-grid">
          {% for chapter in part.chapters %}
          <a
            class="chapter-card"
            href="chapters/{{ chapter.slug }}.html"
            data-filter-item
            data-title="{{ chapter.title|lower }}"
            data-part="{{ part.short_name|lower }}"
          >
            <div class="chapter-card-top">
              <span class="chapter-kicker">Chapter {{ "%02d"|format(chapter.number) }}</span>
              <span class="chapter-reading">{{ chapter.reading_minutes }} min</span>
            </div>
            <h4>{{ chapter.title }}</h4>
            <p>{{ chapter.excerpt }}</p>
          </a>
          {% endfor %}
        </div>
      </section>
      {% endfor %}
    </section>

    <section class="content-section" id="study-method">
      <div class="section-heading">
        <p class="eyebrow">Suggested study method</p>
        <h2>Use the site like an interactive book, not just a reference</h2>
      </div>
      <div class="study-grid">
        {% for step in study_steps %}
        <article class="study-step">
          <span class="step-number">{{ loop.index }}</span>
          <div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.text }}</p>
          </div>
        </article>
        {% endfor %}
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="footer-inner">
      <p>System Design Mastery is a static learning site generated from the Markdown source in the repository.</p>
      <p>Read in order for the strongest beginner-to-architect progression.</p>
    </div>
  </footer>
</body>
</html>
"""


CHAPTER_TEMPLATE = """<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chapter {{ chapter.number }} · {{ chapter.title }} · System Design Mastery</title>
  <meta name="description" content="{{ chapter.excerpt }}">
  <link rel="icon" href="../assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../assets/css/styles.css">
  <script defer src="../assets/js/app.js"></script>
</head>
<body class="page-chapter {{ chapter.part.theme_class }}">
  <div class="progress-bar" aria-hidden="true"><span></span></div>
  <button class="sidebar-backdrop" type="button" aria-label="Close sidebars" data-overlay-close></button>

  <header class="site-header">
    <div class="header-inner">
      <button class="nav-toggle" type="button" aria-label="Open chapter navigation" data-nav-toggle>
        <span></span>
        <span></span>
        <span></span>
      </button>
      <a class="brand" href="../index.html">
        <span class="brand-mark">SD</span>
        <span class="brand-text">
          <strong>System Design Mastery</strong>
          <small>Interactive learning site</small>
        </span>
      </a>
      <nav class="header-nav">
        <a href="../index.html">Home</a>
        <a href="../index.html#roadmap">Roadmap</a>
        <a href="../index.html#chapter-directory">All chapters</a>
      </nav>
      <div class="header-tools">
        <button class="toc-toggle" type="button" aria-label="Open content navigation" data-toc-toggle>
          <span>Contents</span>
        </button>
        <button class="theme-toggle" type="button" data-theme-toggle aria-label="Toggle dark mode">
          <span data-theme-label>Dark mode</span>
        </button>
      </div>
    </div>
  </header>

  <div class="page-shell">
    <aside class="sidebar sidebar-left" id="site-sidebar" data-sidebar="left">
      <div class="sidebar-inner">
        <div class="sidebar-controls">
          <div class="sidebar-controls-copy sidebar-header">
            <p class="eyebrow">System Design Mastery</p>
            <h2>Chapter navigator</h2>
            <p>Follow the curriculum in order or jump across parts when you need to revisit a concept.</p>
          </div>
          <button
            class="sidebar-toggle"
            type="button"
            data-toggle-sidebar="left"
            aria-label="Toggle chapter navigation"
            aria-expanded="true"
            title="Toggle chapter navigation"
          >
            <span class="toggle-icon" aria-hidden="true">«</span>
          </button>
        </div>
        <span class="sidebar-mini-label" aria-hidden="true">Chapters</span>

        <div class="sidebar-content">
          <label class="search-field search-field-sidebar">
            <span>Jump to chapter</span>
            <input
              type="search"
              placeholder="Filter by title or part"
              data-filter-input
              data-filter-target="#site-sidebar"
            >
          </label>

          <nav class="sidebar-nav" aria-label="Chapter navigation">
            {% for part in parts %}
            <section class="nav-part {{ part.theme_class }}" data-filter-group>
              <div class="nav-part-header">
                <p class="nav-part-kicker">Part {{ part.order }}</p>
                <h3>{{ part.short_name }}</h3>
              </div>
              <ul class="nav-chapter-list">
                {% for item in part.chapters %}
                <li
                  class="nav-chapter-item {% if item.slug == chapter.slug %}is-active{% endif %}"
                  data-filter-item
                  data-title="{{ item.title|lower }}"
                  data-part="{{ part.short_name|lower }}"
                >
                  <a href="{{ item.slug }}.html">
                    <span class="nav-chapter-number">{{ "%02d"|format(item.number) }}</span>
                    <span class="nav-chapter-copy">
                      <strong>{{ item.title }}</strong>
                      <small>{{ item.reading_minutes }} min read</small>
                    </span>
                  </a>
                </li>
                {% endfor %}
              </ul>
            </section>
            {% endfor %}
          </nav>
        </div>
      </div>
    </aside>

    <main class="content-column">
      <div class="breadcrumbs">
        <a href="../index.html">Home</a>
        <span>/</span>
        <a href="../index.html#part-{{ chapter.part.order }}">{{ chapter.part.short_name }}</a>
        <span>/</span>
        <span>Chapter {{ chapter.number }}</span>
      </div>

      <article class="chapter-article">
        <header class="chapter-hero {{ chapter.part.theme_class }}">
          <div class="chapter-hero-top">
            <span class="chapter-kicker">Chapter {{ "%02d"|format(chapter.number) }} of {{ total_chapters }}</span>
            <span class="part-badge">{{ chapter.part.short_name }}</span>
          </div>
          <h1>{{ chapter.title }}</h1>
          <p class="chapter-lead">{{ chapter.excerpt }}</p>
          <div class="chapter-meta-strip">
            <div class="summary-pill">
              <span class="summary-label">Reading time</span>
              <strong>{{ chapter.reading_minutes }} min read</strong>
            </div>
            <div class="summary-pill">
              <span class="summary-label">Focus</span>
              <strong>{{ chapter.part.description }}</strong>
            </div>
            <div class="summary-pill">
              <span class="summary-label">Study cue</span>
              <strong>Read, sketch the system, compare trade-offs, revisit the case study</strong>
            </div>
          </div>
        </header>

        <div class="chapter-body article-body">
          {{ chapter.content|safe }}
        </div>

        <section class="chapter-pagination">
          {% if chapter.previous %}
          <a class="pagination-link pagination-link-prev" href="{{ chapter.previous.slug }}.html">
            <span class="pagination-label">Previous chapter</span>
            <strong>{{ chapter.previous.title }}</strong>
          </a>
          {% endif %}

          <a class="pagination-link pagination-link-home" href="../index.html">
            <span class="pagination-label">Back to home</span>
            <strong>System Design Mastery</strong>
          </a>

          {% if chapter.next %}
          <a class="pagination-link pagination-link-next" href="{{ chapter.next.slug }}.html">
            <span class="pagination-label">Next chapter</span>
            <strong>{{ chapter.next.title }}</strong>
          </a>
          {% endif %}
        </section>
      </article>
    </main>

    <aside class="toc-column sidebar-right" data-sidebar="right">
      <div class="toc-card">
        <div class="sidebar-controls sidebar-controls-right">
          <div class="sidebar-controls-copy">
            <p class="eyebrow">On this page</p>
            <h2>Table of contents</h2>
          </div>
          <button
            class="sidebar-toggle"
            type="button"
            data-toggle-sidebar="right"
            aria-label="Toggle content navigation"
            aria-expanded="true"
            title="Toggle content navigation"
          >
            <span class="toggle-icon" aria-hidden="true">«</span>
          </button>
        </div>
        <span class="sidebar-mini-label" aria-hidden="true">Contents</span>
        <div class="sidebar-content toc-panel-body">
          <div class="toc-content">
            {% if chapter.toc %}
              {{ chapter.toc|safe }}
            {% else %}
              <p class="toc-empty">This chapter does not expose a generated table of contents.</p>
            {% endif %}
          </div>
        </div>
      </div>
    </aside>
  </div>

  <footer class="site-footer">
    <div class="footer-inner">
      <p>Source of truth: Markdown chapters in <code>system-design-mastery/</code>.</p>
      <p>Static output: generated for lightweight hosting on GitHub Pages, Netlify, or Vercel.</p>
    </div>
  </footer>
</body>
</html>
"""


STYLES = """
:root {
  --bg: #f5f2eb;
  --bg-alt: #ede7dc;
  --surface: rgba(255, 253, 248, 0.92);
  --surface-strong: #fffdf9;
  --surface-muted: #f1ece2;
  --surface-ink: #181b21;
  --border: #ddd4c5;
  --border-strong: #cbbfae;
  --text: #1f2430;
  --text-muted: #5f6676;
  --text-soft: #71798b;
  --shadow: 0 16px 40px rgba(44, 32, 18, 0.08);
  --radius-lg: 24px;
  --radius-md: 18px;
  --radius-sm: 12px;
  --ui-font: "Avenir Next", "Segoe UI", "Helvetica Neue", sans-serif;
  --reading-font: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Baskerville, Georgia, serif;
  --mono-font: "JetBrains Mono", "SFMono-Regular", Consolas, "Liberation Mono", monospace;
  --accent: #2563eb;
  --accent-strong: #1d4ed8;
  --accent-soft: rgba(37, 99, 235, 0.12);
  --success: #0f766e;
}

[data-theme="dark"] {
  --bg: #121419;
  --bg-alt: #181c23;
  --surface: rgba(24, 28, 35, 0.88);
  --surface-strong: #1b2028;
  --surface-muted: #202631;
  --surface-ink: #f6f3ed;
  --border: #313846;
  --border-strong: #465066;
  --text: #edf1f7;
  --text-muted: #b7c0d0;
  --text-soft: #95a1b6;
  --shadow: 0 18px 44px rgba(0, 0, 0, 0.34);
  --accent-soft: rgba(96, 165, 250, 0.16);
}

body.part-1 { --accent: #2563eb; --accent-strong: #1d4ed8; }
body.part-2 { --accent: #0f766e; --accent-strong: #0b5f59; }
body.part-3 { --accent: #ca8a04; --accent-strong: #a16207; }
body.part-4 { --accent: #c2410c; --accent-strong: #9a3412; }
body.part-5 { --accent: #0f766e; --accent-strong: #115e59; }
body.part-6 { --accent: #b91c1c; --accent-strong: #991b1b; }

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 36%),
    radial-gradient(circle at top right, rgba(15, 118, 110, 0.08), transparent 34%),
    linear-gradient(180deg, var(--bg-alt), var(--bg) 220px, var(--bg));
  color: var(--text);
  font-family: var(--ui-font);
}

a {
  color: var(--accent-strong);
  text-decoration: none;
}

a:hover { text-decoration: underline; }
img { max-width: 100%; }
code, pre { font-family: var(--mono-font); }

.progress-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 200;
  height: 3px;
  background: transparent;
}

.progress-bar > span {
  display: block;
  width: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--accent-strong));
  transition: width 120ms ease-out;
}

.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  background: rgba(245, 242, 235, 0.72);
  backdrop-filter: blur(16px);
}

[data-theme="dark"] .site-header {
  background: rgba(18, 20, 25, 0.72);
  border-bottom-color: rgba(255, 255, 255, 0.05);
}

.header-inner,
.footer-inner,
.hero-section,
.content-section {
  width: min(100%, 1180px);
  margin: 0 auto;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.95rem 1.5rem;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.85rem;
  color: inherit;
  text-decoration: none;
}

.brand:hover { text-decoration: none; }

.brand-mark {
  display: inline-grid;
  place-items: center;
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 0.9rem;
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: white;
  font-weight: 700;
  letter-spacing: 0.04em;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  line-height: 1.1;
}

.brand-text strong {
  font-size: 0.98rem;
  letter-spacing: 0.02em;
}

.brand-text small {
  color: var(--text-soft);
  font-size: 0.78rem;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-nav a {
  color: var(--text-muted);
  font-size: 0.94rem;
}

.theme-toggle,
.button,
.nav-toggle,
.toc-toggle,
.sidebar-toggle {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 999px;
  font: inherit;
  cursor: pointer;
  transition: transform 140ms ease, border-color 140ms ease, background 140ms ease;
}

.theme-toggle {
  padding: 0.6rem 0.95rem;
  min-width: 7.75rem;
}

.theme-toggle:hover,
.button:hover,
.nav-toggle:hover,
.toc-toggle:hover,
.sidebar-toggle:hover {
  transform: translateY(-1px);
  border-color: var(--border-strong);
  text-decoration: none;
}

.nav-toggle {
  display: none;
  flex-direction: column;
  gap: 0.22rem;
  width: 2.8rem;
  height: 2.8rem;
  justify-content: center;
  align-items: center;
  border-radius: 0.85rem;
}

.nav-toggle span {
  display: block;
  width: 1rem;
  height: 2px;
  border-radius: 999px;
  background: currentColor;
}

.header-tools {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.toc-toggle {
  display: none;
  padding: 0.6rem 0.95rem;
}

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr);
  gap: 2rem;
  align-items: center;
  padding: 4.25rem 1.5rem 2.75rem;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(2.8rem, 5vw, 4.5rem);
  line-height: 0.98;
  letter-spacing: -0.04em;
}

.hero-lead {
  margin: 1.4rem 0 0;
  max-width: 44rem;
  font-size: 1.15rem;
  line-height: 1.8;
  color: var(--text-muted);
}

.hero-support {
  margin: 1rem 0 0;
  max-width: 40rem;
  line-height: 1.8;
  color: var(--text-soft);
}

.eyebrow {
  margin: 0 0 0.8rem;
  color: var(--accent-strong);
  font-size: 0.82rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-weight: 700;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
  margin-top: 1.8rem;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.88rem 1.2rem;
  font-weight: 600;
}

.button-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent-strong));
  color: white;
  border-color: transparent;
}

.button-secondary {
  background: var(--surface);
}

.hero-panel,
.info-card,
.roadmap-card,
.directory-part,
.study-step,
.sidebar-inner,
.toc-card,
.chapter-hero,
.summary-pill,
.pagination-link,
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.hero-panel {
  border-radius: var(--radius-lg);
  padding: 1.2rem;
}

.hero-stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.stat-card {
  border-radius: var(--radius-md);
  padding: 1rem;
  min-height: 8.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.stat-card strong {
  font-size: 1.4rem;
  letter-spacing: -0.03em;
}

.stat-card span {
  color: var(--text-muted);
  line-height: 1.55;
}

.content-section {
  padding: 2rem 1.5rem;
}

.section-heading {
  max-width: 46rem;
  margin-bottom: 1.3rem;
}

.section-heading h2 {
  margin: 0;
  font-size: clamp(1.7rem, 3vw, 2.5rem);
  letter-spacing: -0.03em;
}

.card-grid {
  display: grid;
  gap: 1rem;
}

.card-grid-two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.info-card,
.roadmap-card,
.directory-part,
.study-step,
.chapter-card,
.summary-pill,
.pagination-link,
.toc-card,
.sidebar-inner,
.chapter-hero {
  border-radius: var(--radius-lg);
}

.info-card,
.roadmap-card,
.study-step {
  padding: 1.35rem;
}

.info-card h3,
.roadmap-card h3,
.study-step h3 {
  margin: 0 0 0.7rem;
  font-size: 1.05rem;
}

.info-card p,
.roadmap-card p,
.study-step p {
  margin: 0;
  line-height: 1.72;
  color: var(--text-muted);
}

.roadmap-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.roadmap-card {
  position: relative;
  overflow: hidden;
}

.roadmap-card::before,
.directory-part::before,
.chapter-hero::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 6px;
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
}

.roadmap-meta,
.chapter-kicker,
.nav-part-kicker {
  color: var(--accent-strong);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 700;
}

.roadmap-footer {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 1rem;
  color: var(--text-soft);
  font-size: 0.92rem;
}

.directory-toolbar {
  margin-bottom: 1rem;
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-width: 25rem;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.search-field input {
  width: 100%;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  font: inherit;
}

.directory-part {
  position: relative;
  padding: 1.35rem 1.4rem 1.5rem;
  margin-top: 1rem;
}

.directory-part-header {
  display: flex;
  justify-content: space-between;
  gap: 1.5rem;
  align-items: flex-start;
  margin-bottom: 1rem;
  padding-left: 0.6rem;
}

.directory-part-header h3 {
  margin: 0.2rem 0 0;
  font-size: 1.5rem;
}

.directory-part-header p:last-child {
  max-width: 33rem;
  margin: 0;
  line-height: 1.7;
  color: var(--text-muted);
}

.chapter-card-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.chapter-card {
  display: block;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.15rem;
  color: inherit;
  transition: transform 140ms ease, border-color 140ms ease, box-shadow 140ms ease;
}

.chapter-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: 0 12px 30px rgba(26, 22, 16, 0.09);
  text-decoration: none;
}

.chapter-card-top {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: center;
}

.chapter-card h4 {
  margin: 0.8rem 0 0.65rem;
  font-size: 1.08rem;
}

.chapter-card p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.65;
}

.chapter-reading {
  color: var(--text-soft);
  font-size: 0.88rem;
}

.study-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 1rem;
}

.study-step {
  display: flex;
  gap: 0.9rem;
  align-items: flex-start;
}

.step-number {
  width: 2rem;
  height: 2rem;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-weight: 700;
  flex: 0 0 auto;
}

.site-footer {
  border-top: 1px solid var(--border);
  margin-top: 2rem;
}

.footer-inner {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.4rem 1.5rem 2.4rem;
  color: var(--text-soft);
  font-size: 0.92rem;
}

.page-shell {
  width: min(100%, 1720px);
  margin: 0 auto;
  display: grid;
  --left-column-width: 17rem;
  --right-column-width: 15rem;
  grid-template-columns: var(--left-column-width) minmax(0, 1fr) var(--right-column-width);
  gap: clamp(1.25rem, 2vw, 2rem);
  align-items: start;
  padding: 1.8rem clamp(1rem, 2vw, 1.8rem) 3rem;
  transition: grid-template-columns 220ms ease, gap 220ms ease;
}

.page-shell.content-expanded-left {
  --left-column-width: 4.25rem;
}

.page-shell.content-expanded-right {
  --right-column-width: 4.25rem;
}

.page-shell.content-expanded-both {
  --left-column-width: 4.25rem;
  --right-column-width: 4.25rem;
}

.sidebar,
.toc-column {
  position: sticky;
  top: 5rem;
  align-self: start;
  min-width: 0;
}

.sidebar-inner,
.toc-card {
  padding: 1rem;
  max-height: calc(100vh - 6rem);
  overflow: auto;
  transition: padding 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}

.sidebar-controls {
  display: flex;
  justify-content: space-between;
  gap: 0.85rem;
  align-items: flex-start;
}

.sidebar-controls-copy {
  min-width: 0;
  flex: 1 1 auto;
  transition: opacity 180ms ease, transform 220ms ease, max-height 220ms ease;
}

.sidebar-toggle {
  width: 2.55rem;
  height: 2.55rem;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
}

.toggle-icon {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1;
}

.sidebar-mini-label {
  display: none;
  align-items: center;
  justify-content: center;
  margin: 1.1rem auto 0;
  color: var(--text-soft);
  font-size: 0.8rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  user-select: none;
}

.sidebar-content {
  transition:
    opacity 180ms ease,
    transform 220ms ease,
    max-height 220ms ease,
    margin 220ms ease;
}

.sidebar-right .sidebar-controls {
  align-items: center;
}

.sidebar-left.collapsed .sidebar-inner,
.sidebar-right.collapsed .toc-card {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.sidebar-left.collapsed .sidebar-controls,
.sidebar-right.collapsed .sidebar-controls {
  justify-content: center;
}

.sidebar-left.collapsed .sidebar-controls-copy,
.sidebar-right.collapsed .sidebar-controls-copy,
.sidebar-left.collapsed .sidebar-content,
.sidebar-right.collapsed .sidebar-content {
  opacity: 0;
  transform: translateX(-8px);
  pointer-events: none;
  max-height: 0;
  overflow: hidden;
  margin: 0;
}

.sidebar-right.collapsed .sidebar-controls-copy,
.sidebar-right.collapsed .sidebar-content {
  transform: translateX(8px);
}

.sidebar-left.collapsed .sidebar-mini-label,
.sidebar-right.collapsed .sidebar-mini-label {
  display: inline-flex;
}

.sidebar-header h2 {
  margin: 0.2rem 0 0.55rem;
  font-size: 1.25rem;
}

.sidebar-header p:last-child {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.62;
}

.search-field-sidebar {
  margin: 1rem 0 1.15rem;
}

.nav-part + .nav-part {
  margin-top: 1.2rem;
  padding-top: 1.2rem;
  border-top: 1px solid var(--border);
}

.nav-part-header h3 {
  margin: 0.15rem 0 0;
  font-size: 1rem;
}

.nav-chapter-list {
  list-style: none;
  padding: 0;
  margin: 0.8rem 0 0;
}

.nav-chapter-item + .nav-chapter-item {
  margin-top: 0.35rem;
}

.nav-chapter-item a {
  display: flex;
  gap: 0.8rem;
  align-items: flex-start;
  border-radius: 14px;
  padding: 0.7rem 0.75rem;
  color: inherit;
}

.nav-chapter-item a:hover {
  background: var(--surface-muted);
  text-decoration: none;
}

.nav-chapter-item.is-active a {
  background: var(--accent-soft);
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.nav-chapter-number {
  min-width: 2rem;
  color: var(--accent-strong);
  font-weight: 700;
}

.nav-chapter-copy {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.nav-chapter-copy strong {
  font-size: 0.95rem;
  line-height: 1.35;
}

.nav-chapter-copy small {
  color: var(--text-soft);
}

.content-column {
  min-width: 0;
  width: 100%;
}

.chapter-article {
  width: 100%;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.45rem;
  color: var(--text-soft);
  font-size: 0.92rem;
  margin-bottom: 1rem;
}

.chapter-hero {
  position: relative;
  padding: 1.5rem 1.7rem 1.6rem 1.95rem;
  overflow: hidden;
}

.chapter-hero-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.part-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent-strong);
  font-size: 0.86rem;
  font-weight: 700;
}

.chapter-hero h1 {
  margin: 0.8rem 0 0;
  font-size: clamp(2.15rem, 5vw, 3.4rem);
  line-height: 1.02;
  letter-spacing: -0.04em;
}

.chapter-lead {
  margin: 1rem 0 0;
  max-width: 72ch;
  color: var(--text-muted);
  font-size: 1.08rem;
  line-height: 1.8;
}

.chapter-meta-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;
  margin-top: 1.35rem;
}

.summary-pill {
  padding: 0.95rem 1rem;
  background: var(--surface-strong);
}

.summary-pill strong {
  display: block;
  line-height: 1.55;
  font-size: 0.96rem;
}

.summary-label {
  display: block;
  margin-bottom: 0.35rem;
  color: var(--text-soft);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chapter-body {
  width: min(100%, 1100px);
  max-width: none;
  padding: 2rem 0 0;
}

.article-body {
  font-family: var(--reading-font);
}

.article-body h2,
.article-body h3,
.article-body h4 {
  font-family: var(--ui-font);
  color: var(--surface-ink);
}

[data-theme="dark"] .article-body h2,
[data-theme="dark"] .article-body h3,
[data-theme="dark"] .article-body h4 {
  color: var(--text);
}

.article-body h2 {
  margin: 3rem 0 1rem;
  padding-top: 1.35rem;
  border-top: 1px solid var(--border);
  font-size: 1.65rem;
  scroll-margin-top: 6rem;
}

.article-body h3 {
  margin: 2rem 0 0.8rem;
  font-size: 1.15rem;
  scroll-margin-top: 6rem;
}

.article-body h4 {
  margin: 1.4rem 0 0.6rem;
  font-size: 1rem;
}

.article-body p,
.article-body li,
.article-body td,
.article-body th,
.article-body blockquote {
  font-size: 1.05rem;
  line-height: 1.82;
}

.article-body > p,
.article-body > ul,
.article-body > ol,
.article-body > dl,
.article-body > blockquote {
  max-width: 74ch;
}

.article-body > pre,
.article-body > table,
.article-body > .table-wrapper,
.article-body > .mermaid,
.article-body > .mermaid-diagram,
.article-body > .mermaid-static-diagram,
.article-body > figure {
  max-width: 100%;
}

.article-body ul,
.article-body ol {
  padding-left: 1.3rem;
}

.article-body li + li {
  margin-top: 0.4rem;
}

.article-body strong {
  font-family: var(--ui-font);
}

.article-body a {
  text-decoration: underline;
  text-decoration-color: rgba(0, 0, 0, 0.15);
}

[data-theme="dark"] .article-body a {
  text-decoration-color: rgba(255, 255, 255, 0.22);
}

.article-body blockquote {
  margin: 1.5rem 0;
  padding: 1rem 1.15rem;
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.article-body pre {
  position: relative;
  margin: 1.4rem 0;
  padding: 1rem 1.1rem;
  overflow: auto;
  background: #171a20;
  color: #f9fafb;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

[data-theme="dark"] .article-body pre {
  background: #0d1015;
}

.article-body code {
  background: rgba(15, 23, 42, 0.08);
  border-radius: 6px;
  padding: 0.12rem 0.35rem;
  font-size: 0.92em;
}

.article-body pre code {
  background: transparent;
  padding: 0;
  color: inherit;
}

.copy-button {
  position: absolute;
  top: 0.75rem;
  right: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.08);
  color: white;
  border-radius: 999px;
  padding: 0.32rem 0.7rem;
  font-size: 0.78rem;
  cursor: pointer;
}

.article-body .mermaid {
  margin: 1.6rem 0;
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: #fffdf9;
  overflow: auto;
}

[data-theme="dark"] .article-body .mermaid {
  background: #f6f1e8;
}

.article-body .mermaid-static-diagram {
  margin: 1.6rem 0;
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: #fffdf9;
  overflow: auto;
}

[data-theme="dark"] .article-body .mermaid-static-diagram {
  background: #f6f1e8;
}

.article-body .mermaid-static-diagram img {
  display: block;
  width: 100%;
  height: auto;
}

.table-wrap {
  margin: 1.5rem 0;
  overflow: auto;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--surface-strong);
}

.article-body table {
  width: 100%;
  border-collapse: collapse;
  min-width: 620px;
}

.article-body th,
.article-body td {
  padding: 0.85rem 0.95rem;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
}

.article-body th {
  font-family: var(--ui-font);
  background: var(--surface-muted);
}

.heading-anchor {
  margin-left: 0.55rem;
  color: var(--text-soft);
  font-size: 0.9rem;
  opacity: 0;
  transition: opacity 120ms ease;
}

.article-body h2:hover .heading-anchor,
.article-body h3:hover .heading-anchor {
  opacity: 1;
}

.chapter-pagination {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-top: 2.3rem;
}

.pagination-link {
  display: block;
  padding: 1rem 1.1rem;
  color: inherit;
}

.pagination-link:hover {
  text-decoration: none;
  border-color: var(--border-strong);
}

.pagination-label {
  display: block;
  color: var(--text-soft);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.35rem;
}

.toc-card {
  overflow: auto;
}

.toc-card h2 {
  margin: 0.2rem 0 0.8rem;
  font-size: 1.1rem;
}

.toc-panel-body {
  margin-top: 1rem;
}

.toc-content {
  font-size: 0.95rem;
}

.toc-content .toc ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

.toc-content .toc ul ul {
  margin-left: 0.8rem;
  padding-left: 0.8rem;
  border-left: 1px solid var(--border);
}

.toc-content li + li {
  margin-top: 0.42rem;
}

.toc-content a {
  color: var(--text-muted);
}

.toc-content a.is-active {
  color: var(--accent-strong);
  font-weight: 700;
}

.toc-empty {
  margin: 0;
  color: var(--text-soft);
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  z-index: 70;
  border: 0;
  background: rgba(9, 11, 14, 0.42);
  opacity: 0;
  pointer-events: none;
  transition: opacity 140ms ease;
}

body.nav-open .sidebar-backdrop,
body.toc-open .sidebar-backdrop {
  opacity: 1;
  pointer-events: auto;
}

[hidden] {
  display: none !important;
}

@media (max-width: 1150px) {
  .page-shell {
    grid-template-columns: var(--left-column-width) minmax(0, 1fr);
  }

  .toc-column {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    z-index: 80;
    width: min(20rem, 86vw);
    padding: 1rem;
    transform: translateX(110%);
    transition: transform 180ms ease;
  }

  body.toc-open .toc-column {
    transform: translateX(0);
  }

  .toc-card {
    max-height: calc(100vh - 2rem);
  }

  .study-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 980px) {
  .hero-section,
  .card-grid-two,
  .roadmap-grid,
  .chapter-card-grid,
  .study-grid,
  .chapter-meta-strip,
  .footer-inner {
    grid-template-columns: 1fr;
  }

  .hero-section,
  .directory-part-header,
  .footer-inner {
    display: grid;
  }

  .header-nav {
    display: none;
  }

  .toc-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
}

@media (max-width: 900px) {
  body.nav-open,
  body.toc-open {
    overflow: hidden;
  }

  .nav-toggle {
    display: inline-flex;
  }

  .page-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 80;
    width: min(21rem, 86vw);
    padding: 1rem;
    transform: translateX(-110%);
    transition: transform 160ms ease;
  }

  body.nav-open .sidebar {
    transform: translateX(0);
  }

  .sidebar-inner {
    max-height: calc(100vh - 2rem);
  }

  body.nav-open .sidebar-left.collapsed .sidebar-controls-copy,
  body.nav-open .sidebar-left.collapsed .sidebar-content,
  body.toc-open .sidebar-right.collapsed .sidebar-controls-copy,
  body.toc-open .sidebar-right.collapsed .sidebar-content {
    opacity: 1;
    transform: none;
    pointer-events: auto;
    max-height: none;
  }

  body.nav-open .sidebar-left.collapsed .sidebar-mini-label,
  body.toc-open .sidebar-right.collapsed .sidebar-mini-label {
    display: none;
  }

  body.nav-open .sidebar-left.collapsed .sidebar-controls,
  body.toc-open .sidebar-right.collapsed .sidebar-controls {
    justify-content: space-between;
  }

  .chapter-pagination {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .hero-section,
  .content-section,
  .page-shell,
  .header-inner,
  .footer-inner {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .hero-copy h1,
  .chapter-hero h1 {
    letter-spacing: -0.03em;
  }

  .chapter-hero,
  .directory-part,
  .hero-panel {
    padding: 1.15rem;
  }

  .header-tools {
    gap: 0.5rem;
  }

  .toc-toggle span {
    display: none;
  }

  .toc-toggle::before {
    content: "TOC";
    font-size: 0.82rem;
    letter-spacing: 0.08em;
    font-weight: 700;
  }
}

@media print {
  .site-header,
  .sidebar,
  .toc-column,
  .theme-toggle,
  .nav-toggle,
  .chapter-pagination,
  .sidebar-backdrop,
  .progress-bar {
    display: none !important;
  }

  body {
    background: white;
    color: black;
  }

  .page-shell,
  .chapter-body {
    width: 100%;
    max-width: none;
    margin: 0;
    padding: 0;
    display: block;
  }

  .chapter-hero,
  .summary-pill,
  .info-card,
  .roadmap-card,
  .directory-part,
  .study-step {
    box-shadow: none;
    border: 1px solid #bbb;
  }
}
"""


SCRIPT = """
const root = document.documentElement;
const themeButtons = [...document.querySelectorAll('[data-theme-toggle]')];

function applyTheme(theme) {
  root.dataset.theme = theme;
  themeButtons.forEach((button) => {
    const label = button.querySelector('[data-theme-label]');
    if (label) {
      label.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    }
  });
}

const savedTheme = localStorage.getItem('sdm-theme');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
applyTheme(savedTheme || (prefersDark ? 'dark' : 'light'));

themeButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const nextTheme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('sdm-theme', nextTheme);
    applyTheme(nextTheme);
  });
});

const progressBar = document.querySelector('.progress-bar > span');
const article = document.querySelector('.article-body');

function updateReadingProgress() {
  if (!progressBar || !article) return;
  const rect = article.getBoundingClientRect();
  const articleTop = window.scrollY + rect.top;
  const articleHeight = article.offsetHeight;
  const viewportHeight = window.innerHeight;
  const scrollStart = articleTop - viewportHeight * 0.18;
  const scrollEnd = articleTop + articleHeight - viewportHeight * 0.72;
  const progress = Math.max(0, Math.min(1, (window.scrollY - scrollStart) / (scrollEnd - scrollStart || 1)));
  progressBar.style.width = `${progress * 100}%`;
}

window.addEventListener('scroll', updateReadingProgress, { passive: true });
window.addEventListener('resize', updateReadingProgress);
updateReadingProgress();

const pageShell = document.querySelector('.page-shell');
const leftSidebar = document.querySelector('.sidebar-left');
const rightSidebar = document.querySelector('.sidebar-right');
const leftSidebarButtons = [...document.querySelectorAll('[data-toggle-sidebar="left"]')];
const rightSidebarButtons = [...document.querySelectorAll('[data-toggle-sidebar="right"]')];
const navToggle = document.querySelector('[data-nav-toggle]');
const tocToggle = document.querySelector('[data-toc-toggle]');
const overlayCloseTargets = [...document.querySelectorAll('[data-overlay-close]')];
const leftSidebarKey = 'leftSidebarCollapsed';
const rightSidebarKey = 'rightSidebarCollapsed';
const legacyLeftSidebarKey = 'sdm-left-sidebar-collapsed';
const legacyRightSidebarKey = 'sdm-right-sidebar-collapsed';
const navOverlayMedia = window.matchMedia('(max-width: 900px)');
const tocOverlayMedia = window.matchMedia('(max-width: 1150px)');

function syncShellLayout() {
  if (!pageShell) return;
  const leftCollapsed = Boolean(leftSidebar?.classList.contains('collapsed'));
  const rightCollapsed = Boolean(rightSidebar?.classList.contains('collapsed'));
  pageShell.classList.toggle('content-expanded-left', leftCollapsed);
  pageShell.classList.toggle('content-expanded-right', rightCollapsed);
  pageShell.classList.toggle('content-expanded-both', leftCollapsed && rightCollapsed);
  document.body.classList.toggle('chapters-collapsed', leftCollapsed);
  document.body.classList.toggle('toc-collapsed', rightCollapsed);
}

function syncSidebarButtonState(side) {
  const sidebar = side === 'left' ? leftSidebar : rightSidebar;
  const buttons = side === 'left' ? leftSidebarButtons : rightSidebarButtons;
  if (!sidebar) return;

  const collapsed = sidebar.classList.contains('collapsed');
  buttons.forEach((button) => {
    button.setAttribute('aria-expanded', String(!collapsed));
    const icon = button.querySelector('.toggle-icon');
    if (icon) {
      icon.textContent = collapsed ? '»' : '«';
    }
  });
}

function setSidebarState(side, collapsed, persist = true) {
  const sidebar = side === 'left' ? leftSidebar : rightSidebar;
  if (!sidebar) return;

  sidebar.classList.toggle('collapsed', collapsed);
  syncSidebarButtonState(side);
  syncShellLayout();

  if (persist) {
    if (side === 'left') {
      localStorage.setItem(leftSidebarKey, collapsed ? 'true' : 'false');
      localStorage.removeItem(legacyLeftSidebarKey);
    } else {
      localStorage.setItem(rightSidebarKey, collapsed ? 'true' : 'false');
      localStorage.removeItem(legacyRightSidebarKey);
    }
  }
}

function toggleLeftSidebar() {
  if (!leftSidebar) return;
  setSidebarState('left', !leftSidebar.classList.contains('collapsed'));
}

function toggleRightSidebar() {
  if (!rightSidebar) return;
  setSidebarState('right', !rightSidebar.classList.contains('collapsed'));
}

function closeOverlayPanels() {
  document.body.classList.remove('nav-open', 'toc-open');
}

function openLeftOverlay() {
  closeOverlayPanels();
  document.body.classList.add('nav-open');
}

function openRightOverlay() {
  closeOverlayPanels();
  document.body.classList.add('toc-open');
}

function restoreSidebarState() {
  if (leftSidebar) {
    const savedLeftState = localStorage.getItem(leftSidebarKey) ?? localStorage.getItem(legacyLeftSidebarKey);
    setSidebarState('left', savedLeftState === 'true', false);
  }
  if (rightSidebar) {
    const savedRightState = localStorage.getItem(rightSidebarKey) ?? localStorage.getItem(legacyRightSidebarKey);
    setSidebarState('right', savedRightState === 'true', false);
  }
}

restoreSidebarState();

leftSidebarButtons.forEach((button) => {
  button.addEventListener('click', toggleLeftSidebar);
});

rightSidebarButtons.forEach((button) => {
  button.addEventListener('click', toggleRightSidebar);
});

if (navToggle) {
  navToggle.addEventListener('click', openLeftOverlay);
}

if (tocToggle) {
  tocToggle.addEventListener('click', openRightOverlay);
}

overlayCloseTargets.forEach((target) => {
  target.addEventListener('click', closeOverlayPanels);
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeOverlayPanels();
  }
});

function handleViewportChanges() {
  if (!navOverlayMedia.matches) {
    document.body.classList.remove('nav-open');
  }
  if (!tocOverlayMedia.matches) {
    document.body.classList.remove('toc-open');
  }
}

navOverlayMedia.addEventListener?.('change', handleViewportChanges);
tocOverlayMedia.addEventListener?.('change', handleViewportChanges);
window.addEventListener('resize', handleViewportChanges);
handleViewportChanges();

window.toggleLeftSidebar = toggleLeftSidebar;
window.toggleRightSidebar = toggleRightSidebar;

document.querySelectorAll('[data-filter-input]').forEach((input) => {
  const target = document.querySelector(input.dataset.filterTarget || '');
  if (!target) return;

  const items = [...target.querySelectorAll('[data-filter-item]')];
  const groups = [...target.querySelectorAll('[data-filter-group]')];

  input.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();

    items.forEach((item) => {
      const haystack = `${item.dataset.title || ''} ${item.dataset.part || ''}`.toLowerCase();
      item.hidden = Boolean(query) && !haystack.includes(query);
    });

    groups.forEach((group) => {
      const visibleItems = [...group.querySelectorAll('[data-filter-item]')].some((item) => !item.hidden);
      group.hidden = !visibleItems;
    });
  });
});

document.querySelectorAll('.article-body pre').forEach((pre) => {
  const code = pre.querySelector('code');
  if (!code || code.classList.contains('language-mermaid')) return;

  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy-button';
  button.textContent = 'Copy';
  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(code.innerText);
      button.textContent = 'Copied';
      window.setTimeout(() => {
        button.textContent = 'Copy';
      }, 1200);
    } catch (error) {
      button.textContent = 'Failed';
      window.setTimeout(() => {
        button.textContent = 'Copy';
      }, 1200);
    }
  });
  pre.appendChild(button);
});

document.querySelectorAll('.article-body h2[id], .article-body h3[id]').forEach((heading) => {
  const anchor = document.createElement('a');
  anchor.className = 'heading-anchor';
  anchor.href = `#${heading.id}`;
  anchor.setAttribute('aria-label', `Link to ${heading.textContent}`);
  anchor.textContent = '#';
  heading.appendChild(anchor);
});

const tocLinks = [...document.querySelectorAll('.toc-content a[href^="#"]')];
if (tocLinks.length) {
  const linkMap = new Map(tocLinks.map((link) => [decodeURIComponent(link.getAttribute('href').slice(1)), link]));
  const headings = [...document.querySelectorAll('.article-body h2[id], .article-body h3[id]')];
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (!visible.length) return;
      const currentId = visible[0].target.id;
      tocLinks.forEach((link) => link.classList.remove('is-active'));
      const activeLink = linkMap.get(currentId);
      if (activeLink) activeLink.classList.add('is-active');
    },
    { rootMargin: '-24% 0% -62% 0%', threshold: [0, 1] }
  );

  headings.forEach((heading) => observer.observe(heading));
}
"""


FAVICON = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="System Design Mastery">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#0f766e"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="18" fill="#f5f2eb"/>
  <rect x="6" y="6" width="52" height="52" rx="16" fill="url(#g)"/>
  <path d="M20 22h17c5.2 0 8 2.7 8 7 0 3.5-2 5.8-5.4 6.6L46 44h-7.7l-5.6-7.4H27V44h-7V22zm7 5.7v4h9.2c1.9 0 2.9-.8 2.9-2.2 0-1.4-1-2.2-2.9-2.2H27z" fill="#fffdf9"/>
  <circle cx="17" cy="49" r="3" fill="#fffdf9" opacity="0.9"/>
  <circle cx="28" cy="49" r="3" fill="#fffdf9" opacity="0.7"/>
  <circle cx="39" cy="49" r="3" fill="#fffdf9" opacity="0.5"/>
</svg>
"""


@dataclass
class Part:
    key: str
    order: int
    name: str
    short_name: str
    description: str
    theme_class: str
    chapters: list["Chapter"] = field(default_factory=list)


@dataclass
class Chapter:
    number: int
    title: str
    slug: str
    source_path: Path
    output_path: Path
    part: Part
    excerpt: str
    reading_minutes: int
    word_count: int
    content: str = ""
    toc: str = ""
    previous: "Chapter | None" = None
    next: "Chapter | None" = None


def build_parts() -> list[Part]:
    return [Part(**part) for part in PART_DEFINITIONS]


def clean_inline_markdown(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"^\s*[-*+]\s+", "", text)
    text = re.sub(r"^\s*\d+\.\s+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_section(markdown_text: str, heading: str) -> str:
    lines = markdown_text.splitlines()
    collecting = False
    captured: list[str] = []
    marker = f"## {heading}"
    for line in lines:
        if collecting and line.startswith("## "):
            break
        if collecting:
            captured.append(line)
        if line.strip() == marker:
            collecting = True
    return "\n".join(captured).strip()


def first_paragraph(markdown_block: str) -> str:
    paragraphs = [
        clean_inline_markdown(chunk)
        for chunk in re.split(r"\n\s*\n", markdown_block)
        if clean_inline_markdown(chunk)
    ]
    return paragraphs[0] if paragraphs else ""


def count_words(markdown_text: str) -> int:
    text = re.sub(r"```.*?```", " ", markdown_text, flags=re.S)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", text)
    text = re.sub(r"[#>*_`|]", " ", text)
    return len(re.findall(r"\b[\w'-]+\b", text))


def strip_first_heading(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).lstrip()
    return markdown_text


MERMAID_BLOCK_RE = re.compile(r"<pre><code class=\"language-mermaid\">(.*?)</code></pre>", re.S)


def rewrite_internal_markdown_links(content_html: str) -> str:
    def replace_href(match: re.Match[str]) -> str:
        href = match.group(1)
        if href.startswith(("http://", "https://", "#", "mailto:", "tel:")):
            return match.group(0)
        if ".md" not in href:
            return match.group(0)
        path_only, _, fragment = href.partition("#")
        stem = Path(path_only).stem
        if stem.lower() == "readme":
            replacement = "../index.html"
        else:
            replacement = f"{stem}.html"
        if fragment:
            replacement = f"{replacement}#{fragment}"
        return f'href="{replacement}"'

    content_html = re.sub(r'href="([^"]+)"', replace_href, content_html)
    content_html = re.sub(r"<table>", '<div class="table-wrap"><table>', content_html)
    content_html = re.sub(r"</table>", "</table></div>", content_html)
    return content_html


def render_mermaid_diagram(diagram_source: str, output_path: Path) -> None:
    if not shutil.which("npx"):
        raise RuntimeError("npx is required to render Mermaid diagrams for the static site build.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        input_path = temp_root / "diagram.mmd"
        input_path.write_text(diagram_source, encoding="utf-8")

        command = [
            "npx",
            "-y",
            "@mermaid-js/mermaid-cli",
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            "-b",
            "transparent",
            "-t",
            "neutral",
        ]
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            details = error.stderr.strip() or error.stdout.strip() or "Unknown Mermaid CLI error"
            import sys
            print(f"WARNING: Skipping broken Mermaid diagram {output_path.name}: {details[:200]}", file=sys.stderr)
            # Write a placeholder SVG so the page still renders
            output_path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="50"><text x="10" y="30" fill="#888" font-size="14">Diagram rendering skipped</text></svg>')


def replace_mermaid_blocks(content_html: str, chapter_slug: str, chapter_title: str) -> str:
    index = 0

    def replacer(match: re.Match[str]) -> str:
        nonlocal index
        index += 1
        diagram_source = html.unescape(match.group(1)).strip()
        file_name = f"{chapter_slug}-diagram-{index:02d}.svg"
        render_mermaid_diagram(diagram_source, DIAGRAMS_ROOT / file_name)
        alt_text = html.escape(f"Diagram {index} for {chapter_title}")
        return (
            f'<figure class="mermaid-static-diagram">'
            f'<img src="../assets/diagrams/{file_name}" alt="{alt_text}" loading="lazy">'
            f"</figure>"
        )

    return MERMAID_BLOCK_RE.sub(replacer, content_html)


def convert_markdown(markdown_text: str, chapter_slug: str, chapter_title: str) -> tuple[str, str]:
    md = Markdown(
        extensions=["extra", "toc", "sane_lists"],
        extension_configs={
            "toc": {
                "toc_depth": "2-3",
                "permalink": False,
            }
        },
        output_format="html5",
    )
    html = md.convert(strip_first_heading(markdown_text))
    html = rewrite_internal_markdown_links(html)
    html = replace_mermaid_blocks(html, chapter_slug, chapter_title)
    toc = md.toc or ""
    return html, toc


def collect_chapters(parts: list[Part]) -> list[Chapter]:
    parts_by_key = {part.key: part for part in parts}
    chapters: list[Chapter] = []

    for part in parts:
        for source_path in sorted((SOURCE_ROOT / part.key).glob("*.md")):
            raw = source_path.read_text(encoding="utf-8")
            match = re.search(r"^#\s*([A-Z]?\d+)\.\s*(.+)$", raw, flags=re.M)
            if not match:
                raise ValueError(f"Unable to parse chapter title in {source_path}")

            raw_number = match.group(1)
            number = int(raw_number.lstrip("F")) if raw_number[0].isalpha() else int(raw_number)
            title = clean_inline_markdown(match.group(2))
            slug = source_path.stem
            excerpt = first_paragraph(extract_section(raw, "Overview")) or first_paragraph(raw)
            word_count = count_words(raw)
            reading_minutes = max(5, math.ceil(word_count / 220))
            output_path = OUTPUT_ROOT / "chapters" / f"{slug}.html"

            chapter = Chapter(
                number=number,
                title=title,
                slug=slug,
                source_path=source_path,
                output_path=output_path,
                part=parts_by_key[part.key],
                excerpt=excerpt,
                reading_minutes=reading_minutes,
                word_count=word_count,
            )
            part.chapters.append(chapter)
            chapters.append(chapter)

    chapters.sort(key=lambda chapter: chapter.number)
    for index, chapter in enumerate(chapters):
        if index > 0:
            chapter.previous = chapters[index - 1]
        if index < len(chapters) - 1:
            chapter.next = chapters[index + 1]

        raw_markdown = chapter.source_path.read_text(encoding="utf-8")
        chapter.content, chapter.toc = convert_markdown(raw_markdown, chapter.slug, chapter.title)

    return chapters


def render_site(parts: list[Part], chapters: list[Chapter]) -> None:
    OUTPUT_ROOT.mkdir(exist_ok=True)
    chapters_dir = OUTPUT_ROOT / "chapters"
    chapters_dir.mkdir(exist_ok=True)
    (OUTPUT_ROOT / "assets" / "css").mkdir(parents=True, exist_ok=True)
    DIAGRAMS_ROOT.mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "assets" / "js").mkdir(parents=True, exist_ok=True)
    (OUTPUT_ROOT / "assets" / "icons").mkdir(parents=True, exist_ok=True)

    for old_html in chapters_dir.glob("*.html"):
        old_html.unlink()

    (OUTPUT_ROOT / "assets" / "css" / "styles.css").write_text(
        textwrap.dedent(STYLES).strip() + "\n",
        encoding="utf-8",
    )
    (OUTPUT_ROOT / "assets" / "js" / "app.js").write_text(
        textwrap.dedent(SCRIPT).strip() + "\n",
        encoding="utf-8",
    )
    (OUTPUT_ROOT / "assets" / "icons" / "favicon.svg").write_text(
        textwrap.dedent(FAVICON).strip() + "\n",
        encoding="utf-8",
    )

    env = Environment(
        loader=BaseLoader(),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    index_template = env.from_string(INDEX_TEMPLATE)
    chapter_template = env.from_string(CHAPTER_TEMPLATE)

    audience_cards = [
        {
            "title": "Software developers",
            "text": "Engineers who want to move beyond feature implementation into workload thinking, scale, and system behavior.",
        },
        {
            "title": "Backend engineers",
            "text": "Developers who want deeper intuition for data flow, reliability, consistency, and architecture trade-offs.",
        },
        {
            "title": "Frontend and full-stack engineers",
            "text": "Builders who need to understand the systems their products depend on, especially under growth and failure.",
        },
        {
            "title": "Interview preparation learners",
            "text": "Candidates preparing for structured system design interviews at product companies or platform teams.",
        },
        {
            "title": "Future architects",
            "text": "Engineers growing into technical leadership roles where system boundaries, trade-offs, and long-term design matter.",
        },
    ]

    value_points = [
        {
            "title": "Architectural thinking",
            "text": "Learn how to reason about systems as evolving business assets with real constraints, not isolated coding problems.",
        },
        {
            "title": "Interview relevance",
            "text": "Practice the chapter sequence that mirrors how strong interview answers move from requirements to bottlenecks and trade-offs.",
        },
        {
            "title": "Real-world scale",
            "text": "Connect theory to the components and patterns used in production systems: caches, queues, distributed workflows, and observability.",
        },
        {
            "title": "Trade-off clarity",
            "text": "See why system design is never only about speed or scale. It is about balancing correctness, cost, resilience, and team complexity.",
        },
    ]

    study_steps = [
        {
            "title": "Read the chapter actively",
            "text": "Move in order when possible so each topic inherits the vocabulary and trade-off language from earlier chapters.",
        },
        {
            "title": "Summarize in your own words",
            "text": "Reduce each chapter to a short explanation you could give to a teammate or interviewer without reading from notes.",
        },
        {
            "title": "Draw the architecture",
            "text": "Translate the chapter into boxes, flows, boundaries, and data paths. System design becomes durable when you can sketch it.",
        },
        {
            "title": "Review trade-offs",
            "text": "Ask what gets better, what gets worse, and what assumptions make the architecture correct for a given workload.",
        },
        {
            "title": "Revisit the case study",
            "text": "Use the case study and practice questions to pressure-test whether you can adapt the design under changed requirements.",
        },
    ]

    index_html = index_template.render(
        parts=parts,
        first_chapter=chapters[0],
        total_chapters=len(chapters),
        audience_cards=audience_cards,
        value_points=value_points,
        study_steps=study_steps,
    )
    (OUTPUT_ROOT / "index.html").write_text(index_html, encoding="utf-8")

    total_chapters = len(chapters)
    for chapter in chapters:
        chapter_html = chapter_template.render(
            chapter=chapter,
            parts=parts,
            total_chapters=total_chapters,
        )
        chapter.output_path.write_text(chapter_html, encoding="utf-8")


def main() -> None:
    if not SOURCE_ROOT.exists():
        raise SystemExit("Source folder 'system-design-mastery' was not found.")

    DIAGRAMS_ROOT.mkdir(parents=True, exist_ok=True)
    for old_diagram in DIAGRAMS_ROOT.glob("*.svg"):
        old_diagram.unlink()

    parts = build_parts()
    chapters = collect_chapters(parts)
    render_site(parts, chapters)
    print(f"Generated {len(chapters)} chapters in {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
