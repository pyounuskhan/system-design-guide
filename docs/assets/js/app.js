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
