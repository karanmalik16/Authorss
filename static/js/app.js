/**
 * Canon Ledger — Professional Editorial Workspace Client
 * Controls navigation, master-detail contradiction flags, living story bible,
 * 65-character manuscript reader with margin dots, and author decision recording.
 */

let state = {
  bible: null,
  activeTab: 'tabFlags',
  activeFlagFilter: 'pending',
  activeCategoryFilter: 'all',
  selectedFlagId: null,
  activeChapterId: null,
  activeBibleSubtab: 'bibleChars',
  showSentenceNumbers: true,
  pendingDecision: {
    flagId: null,
    status: null
  }
};

// ==========================================================================
// STRING & QUOTE CLEANING HELPERS
// ==========================================================================

/**
 * Strips duplicate leading/trailing quotes and wraps in clean typographic quotes.
 * Solves: Doubled quote marks in the matrix (""The Archduke... -> "The Archduke...)
 */
function cleanQuote(text) {
  if (!text) return '';
  let str = String(text).trim();
  // Strip outer quotes (standard, curly, unicode)
  str = str.replace(/^["'“\u201c\u2018\u00ab]+|["'”\u201d\u2019\u00bb]+$/g, '').trim();
  return `“${str}”`;
}

/**
 * Strips raw markdown heading syntax e.g. '# Chapter 1: ...' -> 'Chapter 1: ...'
 */
function cleanMarkdownHeading(text) {
  if (!text) return '';
  return String(text).replace(/^#{1,6}\s+/, '').trim();
}

/**
 * Extracts clean chapter title without 'Ch. X · ' or 'Chapter X: ' prefixes
 */
function getCleanChapterTitle(cid, rawTitle) {
  let clean = cleanMarkdownHeading(rawTitle || '').trim();
  clean = clean.replace(new RegExp(`^Ch\\.?\\s*${cid}\\s*[·:–—\\-]\\s*`, 'i'), '');
  clean = clean.replace(new RegExp(`^Chapter\\s*${cid}\\s*[·:–—\\-]\\s*`, 'i'), '');
  clean = clean.replace(/^Ch\\.?\\s*\d+\s*[·:–—\-]?\s*/i, '');
  clean = clean.replace(/^Chapter\s*\d+\s*[·:–—\-]?\s*/i, '');
  return clean.trim();
}

/**
 * Formats chapter references cleanly without redundant 'Ch 1: Chapter 1: ...'
 */
function formatChapterDisplay(cid, rawTitle) {
  const clean = getCleanChapterTitle(cid, rawTitle);
  if (clean) {
    return `Ch. ${cid} · ${clean}`;
  }
  return `Ch. ${cid}`;
}

/**
 * Emphasizes only conflicting words in quotes using bold or thin underline
 */
function highlightConflictingWord(quoteText, category) {
  if (!quoteText) return '';
  let text = escapeHtml(cleanQuote(quoteText));

  // Targeted conflicting word pairs
  const conflictPairs = [
    { regex: /(emerald-green|emerald green|emerald)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(piercing violet|violet)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(grueling three-day hard ride|three-day hard ride|three-day)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(returned that very afternoon|that very afternoon)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(right hand severed at the wrist|right hand severed|severed at the wrist)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(white-knuckled right fingers tightening|both hands|right fingers)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(dissolves into harmless vapor the instant it touches running water|dissolves into harmless vapor)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(waded across the torrent with blades drawn|waded across the torrent)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(sworn to absolute secrecy|No other soul in the realm knows)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(strangled with a crimson cord in his bed|crimson cord)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(icy stare, cold as winter stone|icy stare)/gi, replacement: '<span class="conflict-word">$1</span>' },
    { regex: /(suspicion burning in his dark eyes|burning in his dark eyes)/gi, replacement: '<span class="conflict-word">$1</span>' }
  ];

  for (const pair of conflictPairs) {
    if (pair.regex.test(text)) {
      text = text.replace(pair.regex, pair.replacement);
      break;
    }
  }

  return text;
}

// ==========================================================================
// INITIALIZATION
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
  setupSidebarNavigation();
  setupEventListeners();
  initSplitResizers();
  initGutterObserver();
  handleEmptyStateVisibility();
  loadBibleData();
  loadReferencesData();
});

function setupSidebarNavigation() {
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });

  // Story bible subtabs
  document.querySelectorAll('.tab-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const targetSub = btn.getAttribute('data-subtab');
      state.activeBibleSubtab = targetSub;

      ['bibleChars', 'bibleLocs', 'bibleRules'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = (id === targetSub) ? 'grid' : 'none';
      });
    });
  });
}

function switchTab(tabId) {
  state.activeTab = tabId;
  document.querySelectorAll('.sidebar-nav .nav-item').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });
  document.querySelectorAll('.tab-view').forEach(c => {
    c.classList.toggle('active', c.id === tabId);
  });

  // Hide onboarding empty state if switching to active tab with data
  const hasChapters = (state.bible?.chapters?.length || 0) > 0;
  const onboarding = document.getElementById('emptyStateContainer');
  if (onboarding) {
    onboarding.style.display = hasChapters ? 'none' : 'block';
  }
}

function setupEventListeners() {
  // Sidebar toggle & collapse controls
  const appLayout = document.querySelector('.app-layout');
  const btnToggleSidebar = document.getElementById('btnToggleSidebar');

  function updateSidebarStateUI(isCollapsed) {
    if (btnToggleSidebar) {
      btnToggleSidebar.title = isCollapsed ? 'Show Sidebar (Ctrl+B)' : 'Hide Sidebar (Ctrl+B)';
      const toggleText = btnToggleSidebar.querySelector('.btn-sidebar-toggle-text');
      if (toggleText) {
        toggleText.textContent = isCollapsed ? 'Show Menu' : 'Menu';
      }
      btnToggleSidebar.classList.toggle('active', isCollapsed);
    }
  }

  function toggleSidebar() {
    if (!appLayout) return;
    appLayout.classList.toggle('sidebar-collapsed');
    const isCollapsed = appLayout.classList.contains('sidebar-collapsed');
    updateSidebarStateUI(isCollapsed);
    try {
      localStorage.setItem('canon_ledger_sidebar_collapsed', isCollapsed ? 'true' : 'false');
    } catch(e) {}
  }

  if (btnToggleSidebar) btnToggleSidebar.addEventListener('click', toggleSidebar);

  // Restore saved sidebar preference
  try {
    const isSavedCollapsed = localStorage.getItem('canon_ledger_sidebar_collapsed') === 'true';
    if (isSavedCollapsed && appLayout) {
      appLayout.classList.add('sidebar-collapsed');
      updateSidebarStateUI(true);
    }
  } catch(e) {}

  // Keyboard shortcut: Ctrl+B / Cmd+B to toggle sidebar
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
      e.preventDefault();
      toggleSidebar();
    }
  });

  // Demo story loader (header & onboarding)
  document.getElementById('btnLoadDemo').addEventListener('click', loadDemoStory);
  const onboardingDemo = document.getElementById('btnOnboardingDemo');
  if (onboardingDemo) onboardingDemo.addEventListener('click', loadDemoStory);

  // Demo script guide modal
  document.getElementById('btnDemoGuide').addEventListener('click', openDemoGuide);

  // Paper view toggle
  const togglePaperTheme = document.getElementById('togglePaperTheme');
  if (togglePaperTheme) {
    togglePaperTheme.addEventListener('change', (e) => {
      document.body.classList.toggle('reader-dark-mode', !e.target.checked);
    });
  }

  // Sentence number toggle
  const toggleSentenceNumbers = document.getElementById('toggleSentenceNumbers');
  if (toggleSentenceNumbers) {
    toggleSentenceNumbers.addEventListener('change', (e) => {
      state.showSentenceNumbers = e.target.checked;
      document.body.classList.toggle('hide-sentence-numbers', !state.showSentenceNumbers);
    });
  }

  // Reader Settings Menu Dropdown
  const btnReaderSettings = document.getElementById('btnReaderSettings');
  const readerSettingsMenu = document.getElementById('readerSettingsMenu');
  if (btnReaderSettings && readerSettingsMenu) {
    btnReaderSettings.addEventListener('click', (e) => {
      e.stopPropagation();
      readerSettingsMenu.classList.toggle('open');
      btnReaderSettings.setAttribute('aria-expanded', readerSettingsMenu.classList.contains('open'));
    });
    document.addEventListener('click', (e) => {
      if (!readerSettingsMenu.contains(e.target) && e.target !== btnReaderSettings) {
        readerSettingsMenu.classList.remove('open');
        btnReaderSettings.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Export dropdown
  const exportBtn = document.getElementById('btnExportMenu');
  const exportDropdown = document.getElementById('exportDropdown');
  exportBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    exportDropdown.parentElement.classList.toggle('open');
  });
  document.addEventListener('click', () => {
    exportDropdown.parentElement.classList.remove('open');
  });

  // Reset Project
  document.getElementById('btnReset').addEventListener('click', () => {
    if (confirm("Reset current story bible and start fresh? All chapters and lore will be cleared.")) {
      fetch('/api/reset', { method: 'POST' })
        .then(() => {
          showToast("Workspace reset. Ready for your manuscript.");
          loadBibleData();
        });
    }
  });

  // Flag status filters (chip clicks)
  document.querySelectorAll('.filter-strip .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.filter-strip .chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      state.activeFlagFilter = chip.getAttribute('data-filter');
      renderFlags();
    });
  });

  // Flag category filter
  document.getElementById('selectCategoryFilter').addEventListener('change', (e) => {
    state.activeCategoryFilter = e.target.value;
    renderFlags();
  });

  // Story bible search
  document.getElementById('bibleSearchInput').addEventListener('input', (e) => {
    const term = e.target.value.toLowerCase();
    filterBibleEntries(term);
  });

  // Upload modal triggers
  document.getElementById('btnOpenUploadModal').addEventListener('click', () => openModal('uploadModal'));
  const onboardingUpload = document.getElementById('btnOnboardingUpload');
  if (onboardingUpload) onboardingUpload.addEventListener('click', () => openModal('uploadModal'));

  // Dropzone file handling
  const dropzone = document.getElementById('fileDropzone');
  const fileInput = document.getElementById('fileInput');
  const uploadStatus = document.getElementById('fileUploadStatus');

  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      uploadStatus.textContent = `Selected: ${fileInput.files[0].name}`;
    }
  });
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      uploadStatus.textContent = `Selected: ${fileInput.files[0].name}`;
    }
  });

  // Submit Chapter
  document.getElementById('btnSubmitChapter').addEventListener('click', submitChapter);

  // Author Decision Confirm
  document.getElementById('btnConfirmDecision').addEventListener('click', confirmFlagDecision);

  // Edit Chapter Text
  document.getElementById('btnEditChapterText').addEventListener('click', openEditChapterModal);
  document.getElementById('btnSaveChapterEdit').addEventListener('click', saveChapterEdit);

  // Delete Chapter
  document.getElementById('btnDeleteChapter').addEventListener('click', deleteCurrentChapter);

  // Add lore entry modal
  document.getElementById('btnAddBibleEntry').addEventListener('click', () => openModal('addLoreModal'));
  document.getElementById('btnSaveLoreEntry').addEventListener('click', saveLoreEntry);

  // Modal close buttons
  document.querySelectorAll('[data-close]').forEach(btn => {
    btn.addEventListener('click', () => {
      const modalId = btn.getAttribute('data-close');
      closeModal(modalId);
    });
  });
}

// ==========================================================================
// SPLIT PANE RESIZERS
// ==========================================================================

function initSplitResizers() {
  setupSplitResizer({
    containerId: 'flagsMasterDetail',
    paneId: 'flagsListPane',
    resizerId: 'flagsSplitResizer',
    storageKey: 'canon_ledger_flags_list_width',
    defaultWidth: 430,
    minWidth: 280,
    maxWidth: 800
  });

  setupSplitResizer({
    containerId: 'manuscriptSplit',
    paneId: 'manuscriptSidebar',
    resizerId: 'manuscriptSplitResizer',
    storageKey: 'canon_ledger_manuscript_sidebar_width',
    defaultWidth: 290,
    minWidth: 220,
    maxWidth: 550
  });
}

function setupSplitResizer(options) {
  const container = document.getElementById(options.containerId);
  const pane = document.getElementById(options.paneId);
  const resizer = document.getElementById(options.resizerId);
  if (!container || !pane || !resizer) return;

  // Restore saved width from localStorage
  let savedWidth = options.defaultWidth;
  try {
    const val = localStorage.getItem(options.storageKey);
    if (val) {
      const parsed = parseInt(val, 10);
      if (!isNaN(parsed) && parsed >= options.minWidth && parsed <= options.maxWidth) {
        savedWidth = parsed;
      }
    }
  } catch(e) {}

  pane.style.width = `${savedWidth}px`;

  let isDragging = false;
  let startX = 0;
  let startWidth = 0;

  function onMouseDown(e) {
    if (e.button !== 0) return; // Only primary click
    isDragging = true;
    startX = e.clientX;
    startWidth = pane.getBoundingClientRect().width;

    resizer.classList.add('is-resizing');
    document.body.classList.add('resizing-col');
    e.preventDefault();
  }

  function onMouseMove(e) {
    if (!isDragging) return;
    const deltaX = e.clientX - startX;
    let newWidth = startWidth + deltaX;

    const containerWidth = container.getBoundingClientRect().width;
    const effectiveMax = Math.min(options.maxWidth, containerWidth - 320);
    newWidth = Math.max(options.minWidth, Math.min(effectiveMax, newWidth));

    pane.style.width = `${newWidth}px`;
  }

  function onMouseUp() {
    if (!isDragging) return;
    isDragging = false;
    resizer.classList.remove('is-resizing');
    document.body.classList.remove('resizing-col');

    const finalWidth = Math.round(pane.getBoundingClientRect().width);
    try {
      localStorage.setItem(options.storageKey, finalWidth.toString());
    } catch(e) {}
  }

  // Double click resets to default
  resizer.addEventListener('dblclick', () => {
    pane.style.width = `${options.defaultWidth}px`;
    try {
      localStorage.setItem(options.storageKey, options.defaultWidth.toString());
    } catch(e) {}
  });

  resizer.addEventListener('mousedown', onMouseDown);
  document.addEventListener('mousemove', onMouseMove);
  document.addEventListener('mouseup', onMouseUp);

  // Touch device support
  resizer.addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) return;
    isDragging = true;
    startX = e.touches[0].clientX;
    startWidth = pane.getBoundingClientRect().width;
    resizer.classList.add('is-resizing');
    document.body.classList.add('resizing-col');
  }, { passive: true });

  document.addEventListener('touchmove', (e) => {
    if (!isDragging || e.touches.length !== 1) return;
    const deltaX = e.touches[0].clientX - startX;
    let newWidth = startWidth + deltaX;
    const containerWidth = container.getBoundingClientRect().width;
    const effectiveMax = Math.min(options.maxWidth, containerWidth - 320);
    newWidth = Math.max(options.minWidth, Math.min(effectiveMax, newWidth));
    pane.style.width = `${newWidth}px`;
  }, { passive: true });

  document.addEventListener('touchend', () => {
    if (!isDragging) return;
    isDragging = false;
    resizer.classList.remove('is-resizing');
    document.body.classList.remove('resizing-col');
    const finalWidth = Math.round(pane.getBoundingClientRect().width);
    try {
      localStorage.setItem(options.storageKey, finalWidth.toString());
    } catch(e) {}
  });
}

// ==========================================================================
// DATA LOADING
// ==========================================================================

function loadBibleData() {
  fetch('/api/bible')
    .then(res => res.json())
    .then(data => {
      state.bible = data;
      updateHeaderStats();
      handleEmptyStateVisibility();
      renderFlags();
      renderChapters();
      renderBibleGrid();
      renderKnowledgeMatrix();
      renderTimeline();

      if (state.activeChapterId) {
        selectChapter(state.activeChapterId);
      }
    })
    .catch(err => console.error("Error loading bible:", err));
}

function handleEmptyStateVisibility() {
  const hasChapters = (state.bible?.chapters?.length || 0) > 0;
  const onboarding = document.getElementById('emptyStateContainer');

  if (onboarding) {
    onboarding.style.display = hasChapters ? 'none' : 'block';
  }

  const seriesTag = document.querySelector('.series-tag');
  if (seriesTag) {
    seriesTag.style.display = hasChapters ? '' : 'none';
  }
}

function updateHeaderStats() {
  const b = state.bible;
  if (!b) return;

  const hasChapters = (b.chapters?.length || b.stats?.total_chapters || 0) > 0;
  const seriesTag = document.querySelector('.series-tag');
  if (seriesTag) {
    seriesTag.style.display = hasChapters ? '' : 'none';
  }

  document.getElementById('seriesTitleBadge').textContent = b.series_title || "My Novel";
  document.getElementById('summaryChapters').textContent = `${b.stats?.total_chapters || 0} Chapters`;
  document.getElementById('summaryWords').textContent = `${(b.stats?.total_words || 0).toLocaleString()} Words`;
  document.getElementById('summaryEntities').textContent = `${b.stats?.total_entities || 0} Lore Entities`;

  const pending = b.stats?.pending_flags || 0;
  document.getElementById('summaryPending').textContent = `${pending} Pending Flags`;
  document.getElementById('tabBadgeFlags').textContent = pending;

  // Filter counts
  const total = b.flags?.length || 0;
  const accepted = b.flags?.filter(f => f.status === 'accepted').length || 0;
  const dismissed = b.flags?.filter(f => f.status === 'dismissed').length || 0;
  const fixed = b.flags?.filter(f => f.status === 'fixed').length || 0;

  document.getElementById('countAllFlags').textContent = total;
  document.getElementById('countPendingFlags').textContent = pending;
  document.getElementById('countAcceptedFlags').textContent = accepted;
  document.getElementById('countDismissedFlags').textContent = dismissed;
  document.getElementById('countFixedFlags').textContent = fixed;

  // Bible counts
  const chars = b.entities?.filter(e => e.category === 'character').length || 0;
  const locs = b.entities?.filter(e => e.category === 'location').length || 0;
  const rules = b.world_rules?.length || 0;

  document.getElementById('bibleCharCount').textContent = chars;
  document.getElementById('bibleLocCount').textContent = locs;
  document.getElementById('bibleRuleCount').textContent = rules;
}

// ==========================================================================
// TAB 1: CONTINUITY SENTINEL (MASTER-DETAIL LAYOUT)
// ==========================================================================

function renderFlags() {
  const listEl = document.getElementById('flagsMasterList');
  const detailEl = document.getElementById('flagsDetailContainer');
  if (!listEl || !detailEl) return;

  const flags = state.bible?.flags || [];
  if (flags.length === 0) {
    listEl.innerHTML = `
      <div style="padding: 2rem 1rem; text-align: center; color: var(--text-muted); font-size: 0.84rem;">
        No continuity flags detected.
      </div>
    `;
    detailEl.innerHTML = `
      <div class="empty-detail-state">
        <p>No continuity flags to inspect.</p>
      </div>
    `;
    return;
  }

  // Filter flags
  const filtered = flags.filter(f => {
    const matchStatus = (state.activeFlagFilter === 'all') || (f.status === state.activeFlagFilter);
    const matchCategory = (state.activeCategoryFilter === 'all') || (f.category === state.activeCategoryFilter);
    return matchStatus && matchCategory;
  });

  if (filtered.length === 0) {
    listEl.innerHTML = `
      <div style="padding: 2rem 1rem; text-align: center; color: var(--text-muted); font-size: 0.84rem;">
        No flags matching filter "${state.activeFlagFilter}".
      </div>
    `;
    detailEl.innerHTML = `
      <div class="empty-detail-state">
        <p>Select another filter to view flags.</p>
      </div>
    `;
    return;
  }

  // Default selection to first flag if current selection not in filtered list
  if (!filtered.some(f => f.id === state.selectedFlagId)) {
    state.selectedFlagId = filtered[0].id;
  }

  // Render List on Left
  listEl.innerHTML = filtered.map(flag => {
    const isSelected = flag.id === state.selectedFlagId;
    const dotClass = `status-${flag.status}-dot`;
    const earlierTitle = getCleanChapterTitle(flag.earlier_chapter_id, flag.earlier_chapter_title) || `Chapter ${flag.earlier_chapter_id}`;
    const newTitle = getCleanChapterTitle(flag.new_chapter_id, flag.new_chapter_title) || `Chapter ${flag.new_chapter_id}`;

    return `
      <div class="flag-list-item ${isSelected ? 'selected' : ''}" onclick="selectFlag('${flag.id}')">
        <div class="flag-list-meta">
          <span class="flag-category-tag">${escapeHtml(flag.category.replace(/_/g, ' '))}</span>
          <span class="flag-status-dot ${dotClass}" title="Status: ${flag.status}"></span>
        </div>
        <div class="flag-list-title">${escapeHtml(flag.title)}</div>
        <div class="flag-list-locations">
          <div class="flag-loc-row">
            <span class="flag-loc-label baseline">Baseline:</span>
            <span class="flag-loc-val" title="Ch. ${flag.earlier_chapter_id} · ${escapeHtml(earlierTitle)}">Ch. ${flag.earlier_chapter_id} · ${escapeHtml(earlierTitle)}</span>
          </div>
          <div class="flag-loc-row">
            <span class="flag-loc-label conflict">Conflict:</span>
            <span class="flag-loc-val" title="Ch. ${flag.new_chapter_id} · ${escapeHtml(newTitle)}">Ch. ${flag.new_chapter_id} · ${escapeHtml(newTitle)}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Render Detail on Right
  renderFlagDetail();
}

function selectFlag(flagId) {
  state.selectedFlagId = flagId;
  document.querySelectorAll('.flag-list-item').forEach(el => el.classList.remove('selected'));
  renderFlags();
}

function renderFlagDetail() {
  const detailEl = document.getElementById('flagsDetailContainer');
  const flag = (state.bible?.flags || []).find(f => f.id === state.selectedFlagId);
  if (!flag) {
    detailEl.innerHTML = `
      <div class="empty-detail-state">
        <p>Select a continuity flag to view side-by-side evidence.</p>
      </div>
    `;
    return;
  }

  const earlierTitle = getCleanChapterTitle(flag.earlier_chapter_id, flag.earlier_chapter_title) || `Chapter ${flag.earlier_chapter_id}`;
  const newTitle = getCleanChapterTitle(flag.new_chapter_id, flag.new_chapter_title) || `Chapter ${flag.new_chapter_id}`;

  // Emphasize ONLY conflicting words with bold / thin underline
  const earlierHighlighted = highlightConflictingWord(flag.earlier_quote, flag.category);
  const currentHighlighted = highlightConflictingWord(flag.new_quote, flag.category);

  detailEl.innerHTML = `
    <div class="detail-card">
      <div class="detail-top-bar">
        <div class="detail-title-group">
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <span class="tag-badge ${flag.severity === 'high' ? 'high' : ''}">${flag.severity}</span>
            <span class="tag-badge">${escapeHtml(flag.category.replace(/_/g, ' '))}</span>
          </div>
          <h3>${escapeHtml(flag.title)}</h3>
        </div>
        <span class="tag-badge font-mono">${flag.status.toUpperCase()}</span>
      </div>

      <div class="detail-explanation">
        ${escapeHtml(flag.explanation)}
      </div>

      <!-- Side-by-Side Verifiable Evidence -->
      <div class="detail-evidence-grid">
        <!-- Earlier Baseline -->
        <div class="evidence-panel">
          <div class="evidence-header">
            <span class="evidence-role baseline">Earlier Baseline</span>
            <span class="evidence-ref">Ch. ${flag.earlier_chapter_id} · ${escapeHtml(earlierTitle)} · Sent ${flag.earlier_sentence_num}</span>
          </div>
          <div class="evidence-text font-serif">
            ${earlierHighlighted}
          </div>
        </div>

        <!-- Conflicting Passage -->
        <div class="evidence-panel">
          <div class="evidence-header">
            <span class="evidence-role conflict">Conflicting Passage</span>
            <span class="evidence-ref">Ch. ${flag.new_chapter_id} · ${escapeHtml(newTitle)} · Sent ${flag.new_sentence_num}</span>
          </div>
          <div class="evidence-text font-serif">
            ${currentHighlighted}
          </div>
        </div>
      </div>

      <div class="detail-fix-hint">
        <strong>Author Fix Hint:</strong> ${escapeHtml(flag.suggested_fix)}
      </div>

      ${flag.author_note ? `
        <div class="detail-author-note">
          <strong>Author Resolution Note:</strong> "${escapeHtml(flag.author_note)}"
        </div>
      ` : ''}

      <div class="detail-actions-bar">
        <div class="actions-left">
          ${flag.status === 'pending' ? `
            <button class="btn btn-gold" onclick="promptFlagDecision('${flag.id}', 'accepted')">
              Accept Flag
            </button>
            <button class="btn btn-secondary" onclick="promptFlagDecision('${flag.id}', 'dismissed')">
              Dismiss
            </button>
            <button class="btn-text-link" onclick="promptFlagDecision('${flag.id}', 'fixed')">
              Mark as Fixed
            </button>
          ` : `
            <button class="btn btn-sm btn-secondary" onclick="promptFlagDecision('${flag.id}', 'pending')">
              Reopen Flag
            </button>
          `}
        </div>

        <button class="btn-text-link" onclick="jumpToSentenceInManuscript(${flag.new_chapter_id}, ${flag.new_sentence_num})">
          View in Manuscript →
        </button>
      </div>
    </div>
  `;
}

function promptFlagDecision(flagId, status) {
  state.pendingDecision = { flagId, status };
  const title = document.getElementById('decisionModalTitle');
  const promptText = document.getElementById('decisionModalPrompt');
  const noteInput = document.getElementById('inputDecisionNote');
  noteInput.value = '';

  if (status === 'accepted') {
    title.textContent = "Accept Continuity Flag";
    promptText.textContent = "Confirm this continuity error for your revision list. You can add an optional note for your draft revision.";
    noteInput.placeholder = "e.g., Will revise in Chapter 2...";
  } else if (status === 'dismissed') {
    title.textContent = "Dismiss (False Alarm)";
    promptText.textContent = "Canon Ledger permanently hashes and remembers this dismissal fingerprint so this false alarm will never reappear.";
    noteInput.placeholder = "e.g., Poetic metaphor / intentional disguise...";
  } else if (status === 'fixed') {
    title.textContent = "Mark as Fixed";
    promptText.textContent = "Confirm that this contradiction has been resolved in your manuscript.";
    noteInput.placeholder = "e.g., Fixed in draft text...";
  } else {
    // Reopen
    state.activeFlagFilter = 'pending';
    document.querySelectorAll('.filter-strip .chip').forEach(c => c.classList.remove('active'));
    const pendingChip = document.querySelector('.filter-strip .chip[data-filter="pending"]');
    if (pendingChip) pendingChip.classList.add('active');
    state.selectedFlagId = flagId;
    saveFlagStatus(flagId, 'pending', '');
    return;
  }

  openModal('decisionModal');
}

function confirmFlagDecision() {
  const { flagId, status } = state.pendingDecision;
  const note = document.getElementById('inputDecisionNote').value.trim();
  closeModal('decisionModal');
  saveFlagStatus(flagId, status, note);
}

function saveFlagStatus(flagId, status, note) {
  fetch(`/api/flags/${flagId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, author_note: note })
  })
    .then(res => res.json().catch(() => ({ success: false, error: 'Invalid response from server' })))
    .then(res => {
      if (res && res.success) {
        showToast(`Flag updated: ${status}`);
        loadBibleData();
      } else {
        const errorMsg = res && res.error ? res.error : 'Failed to update flag';
        showToast(`Error: ${errorMsg}`);
      }
    })
    .catch(err => {
      console.error("Error saving flag status:", err);
      showToast(`Error: ${err.message || 'Request failed'}`);
    });
}

function jumpToSentenceInManuscript(chapterId, sentenceNum) {
  switchTab('tabManuscript');
  selectChapter(chapterId, sentenceNum);
}

// ==========================================================================
// TAB 2: MANUSCRIPT & CHAPTERS (65-CHAR COLUMN & MARGIN DOTS)
// ==========================================================================

let readerResizeObserver = null;

function refreshGutter() {
  const gutterEl = document.getElementById('manuscriptGutter');
  if (!gutterEl) return;
  gutterEl.innerHTML = '';

  if (!state.activeChapterId) return;

  const chapFlags = (state.bible?.flags || []).filter(
    f => f.new_chapter_id === state.activeChapterId && f.status === 'pending'
  );
  const flaggedSentNums = new Set(chapFlags.map(f => f.new_sentence_num));

  flaggedSentNums.forEach(sentNum => {
    const sentEl = document.getElementById(`sent_${state.activeChapterId}_${sentNum}`);
    if (sentEl) {
      const dot = document.createElement('div');
      dot.className = 'gutter-flag-dot';
      dot.style.top = `${sentEl.offsetTop + 6}px`;
      dot.title = `Continuity flag in sentence #${sentNum}. Click to inspect sentence.`;
      dot.addEventListener('click', () => {
        sentEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
      gutterEl.appendChild(dot);
    }
  });
}

function initGutterObserver() {
  const readerBody = document.getElementById('readerBody');
  if (readerBody && window.ResizeObserver) {
    if (readerResizeObserver) {
      readerResizeObserver.disconnect();
    }
    readerResizeObserver = new ResizeObserver(() => {
      refreshGutter();
    });
    readerResizeObserver.observe(readerBody);
  }
}

function clearReader() {
  state.activeChapterId = null;
  const titleEl = document.getElementById('readerTitle');
  if (titleEl) titleEl.textContent = 'Select a chapter';
  const metaEl = document.getElementById('readerMeta');
  if (metaEl) metaEl.textContent = '';
  const actionsEl = document.getElementById('readerActions');
  if (actionsEl) actionsEl.style.display = 'none';
  const contentArea = document.getElementById('manuscriptContentArea') || document.getElementById('readerBody');
  if (contentArea) {
    contentArea.innerHTML = '<p class="reader-placeholder">Select a chapter from the left to read.</p>';
  }
  const gutterEl = document.getElementById('manuscriptGutter');
  if (gutterEl) gutterEl.innerHTML = '';
  document.querySelectorAll('.chapter-nav-card').forEach(el => el.classList.remove('active'));
}

function renderChapters() {
  const list = document.getElementById('chapterNavList');
  const chapters = state.bible?.chapters || [];
  if (!list) return;

  if (chapters.length === 0) {
    list.innerHTML = `<p style="font-size:0.78rem; color:var(--text-muted); padding:0.5rem;">No chapters loaded.</p>`;
    clearReader();
    return;
  }

  list.innerHTML = chapters.map(c => `
    <div class="chapter-nav-card ${state.activeChapterId === c.id ? 'active' : ''}" data-chapter-id="${c.id}" onclick="selectChapter(${c.id})">
      <div class="chapter-nav-title font-serif">${escapeHtml(cleanMarkdownHeading(c.title))}</div>
      <div class="chapter-nav-meta">
        <span>${c.word_count} words</span>
        <span>${c.sentences?.length || 0} sents</span>
      </div>
    </div>
  `).join('');

  if (!state.activeChapterId && chapters.length > 0) {
    selectChapter(chapters[0].id);
  }
}

function selectChapter(chapterId, highlightSentenceNum = null) {
  state.activeChapterId = chapterId;
  const chap = (state.bible?.chapters || []).find(c => c.id === chapterId);
  if (!chap) {
    clearReader();
    return;
  }

  document.querySelectorAll('.chapter-nav-card').forEach(el => el.classList.remove('active'));
  const activeCard = document.querySelector(`.chapter-nav-card[data-chapter-id="${chap.id}"]`);
  if (activeCard) activeCard.classList.add('active');

  // Clean title without raw #
  const cleanTitle = cleanMarkdownHeading(chap.title);
  document.getElementById('readerTitle').textContent = cleanTitle;
  document.getElementById('readerMeta').textContent = `Chapter #${chap.id} · ${chap.word_count} words · ${chap.sentences?.length || 0} sentences`;
  document.getElementById('readerActions').style.display = 'flex';

  // Find sentences flagged in this chapter
  const chapFlags = (state.bible?.flags || []).filter(f => f.new_chapter_id === chapterId && f.status === 'pending');
  const flaggedSentNums = new Set(chapFlags.map(f => f.new_sentence_num));

  const contentArea = document.getElementById('manuscriptContentArea') || document.getElementById('readerBody');

  // Group sentences by paragraph_num to preserve natural novel formatting
  const parasMap = new Map();
  (chap.sentences || []).forEach(s => {
    const pNum = s.paragraph_num || 1;
    if (!parasMap.has(pNum)) parasMap.set(pNum, []);
    parasMap.get(pNum).push(s);
  });

  let parasHtml = '';
  parasMap.forEach(sents => {
    const sentsHtml = sents.map(s => {
      const isFlagged = flaggedSentNums.has(s.sentence_num);
      const isTarget = highlightSentenceNum === s.sentence_num;
      const cleanSentenceText = cleanMarkdownHeading(s.text);

      return `<span class="reading-sentence ${isFlagged ? 'has-flag' : ''} ${isTarget ? 'target-jump' : ''}" id="sent_${chap.id}_${s.sentence_num}"><span class="sentence-index">[${s.sentence_num}]</span>${escapeHtml(cleanSentenceText)} </span>`;
    }).join('');
    parasHtml += `<p class="manuscript-para">${sentsHtml}</p>`;
  });

  contentArea.innerHTML = parasHtml;

  // Refresh margin gutter dots driven by ResizeObserver and called after rendering
  refreshGutter();

  if (highlightSentenceNum) {
    setTimeout(() => {
      const el = document.getElementById(`sent_${chap.id}_${highlightSentenceNum}`);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 150);
  }
}

function submitChapter() {
  const title = document.getElementById('inputChapterTitle').value.trim();
  const fileInput = document.getElementById('fileInput');
  const pastedText = document.getElementById('inputPastedText').value.trim();

  const formData = new FormData();
  if (title) formData.append('title', cleanMarkdownHeading(title));

  if (fileInput.files.length > 0) {
    formData.append('file', fileInput.files[0]);
  } else if (pastedText) {
    formData.append('text', pastedText);
  } else {
    alert("Please upload a manuscript file (.docx, .md, .txt) or paste prose text.");
    return;
  }

  closeModal('uploadModal');
  showToast("Ingesting chapter & auditing canon...");

  fetch('/api/chapters/upload', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        // Clear file input, pasted text, title, and status text
        const titleInput = document.getElementById('inputChapterTitle');
        if (titleInput) titleInput.value = '';
        const fileInputEl = document.getElementById('fileInput');
        if (fileInputEl) fileInputEl.value = '';
        const pastedTextEl = document.getElementById('inputPastedText');
        if (pastedTextEl) pastedTextEl.value = '';
        const statusEl = document.getElementById('fileUploadStatus');
        if (statusEl) statusEl.textContent = '';
        const dropzoneEl = document.getElementById('fileDropzone');
        if (dropzoneEl) dropzoneEl.classList.remove('dragover');

        showToast(`Chapter ingested! Found ${res.new_flags?.length || 0} continuity flags.`);
        loadBibleData();
        if (res.new_flags && res.new_flags.length > 0) {
          switchTab('tabFlags');
        } else {
          switchTab('tabManuscript');
        }
      } else {
        alert(res.error || "Failed to ingest chapter.");
      }
    });
}

function openEditChapterModal() {
  const chap = (state.bible?.chapters || []).find(c => c.id === state.activeChapterId);
  if (!chap) return;

  state.initialEditText = chap.raw_text;
  document.getElementById('editModalTitle').textContent = "Edit Chapter";
  document.getElementById('editModalTextarea').value = chap.raw_text;
  openModal('editChapterModal');
}

function saveChapterEdit() {
  const textarea = document.getElementById('editModalTextarea');
  const rawValue = textarea ? textarea.value : '';
  const newText = rawValue.trim();
  if (!newText) {
    alert("Chapter text cannot be empty.");
    return;
  }

  state.initialEditText = rawValue; // Set initialEditText to the textarea value, not the trimmed text
  closeModal('editChapterModal');
  showToast("Saving and re-checking continuity sentinel...");

  fetch(`/api/chapters/${state.activeChapterId}/fix`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: newText })
  })
    .then(res => res.json())
    .then(res => {
      if (res.success) {
        showToast("Chapter saved and re-checked!");
        if (res.chapter && state.bible && Array.isArray(state.bible.chapters)) {
          const idx = state.bible.chapters.findIndex(c => c.id === res.chapter.id);
          if (idx !== -1) {
            state.bible.chapters[idx] = res.chapter;
          } else {
            state.bible.chapters.push(res.chapter);
          }
          selectChapter(res.chapter.id);
        }
        loadBibleData();
      } else {
        alert(res.error || "Failed to update chapter.");
      }
    })
    .catch(err => {
      console.error("Save error:", err);
      alert("Network error saving chapter.");
    });
}

function deleteCurrentChapter() {
  if (!state.activeChapterId) return;
  const chap = (state.bible?.chapters || []).find(c => c.id === state.activeChapterId);
  const chapName = chap ? cleanMarkdownHeading(chap.title) : `Chapter #${state.activeChapterId}`;
  if (confirm(`Are you sure you want to delete ${chapName}? This will remove all its text and associated continuity flags.`)) {
    fetch(`/api/chapters/${state.activeChapterId}`, { method: 'DELETE' })
      .then(res => res.json())
      .then(res => {
        if (res.success) {
          clearReader();
          showToast("Chapter removed.");
          loadBibleData();
        } else {
          alert(res.error || "Failed to delete chapter.");
        }
      })
      .catch(err => {
        console.error("Delete error:", err);
        alert("Network error deleting chapter.");
      });
  }
}

// ==========================================================================
// TAB 3: LIVING STORY BIBLE
// ==========================================================================

function renderBibleGrid() {
  const b = state.bible;
  if (!b) return;

  // Characters
  const charGrid = document.getElementById('bibleChars');
  const characters = (b.entities || []).filter(e => e.category === 'character');
  charGrid.innerHTML = characters.map(c => `
    <div class="lore-card">
      <div class="lore-card-header">
        <h4 class="lore-card-name">${escapeHtml(c.name)}</h4>
        <span class="tag-badge">Character</span>
      </div>
      <div class="lore-card-meta">
        <div class="meta-row">
          <span class="meta-key">First Appeared:</span>
          <span class="meta-val">Chapter ${c.first_chapter_id}</span>
        </div>
        ${Object.entries(c.attributes || {}).map(([k, v]) => `
          <div class="meta-row">
            <span class="meta-key">${escapeHtml(k.replace('_', ' '))}:</span>
            <span class="meta-val">${escapeHtml(v)}</span>
          </div>
        `).join('')}
      </div>
      ${(c.citations || []).slice(0, 2).map(cit => `
        <div class="lore-citation-item">
          ${cleanQuote(cit.quote)} <span class="font-mono" style="font-size:0.7rem; color:var(--text-muted);">(Ch. ${cit.chapter_id} · Sent #${cit.sentence_num})</span>
        </div>
      `).join('')}
    </div>
  `).join('');

  // Locations
  const locGrid = document.getElementById('bibleLocs');
  const locations = (b.entities || []).filter(e => e.category === 'location');
  locGrid.innerHTML = locations.map(l => `
    <div class="lore-card">
      <div class="lore-card-header">
        <h4 class="lore-card-name">${escapeHtml(l.name)}</h4>
        <span class="tag-badge">Location</span>
      </div>
      <div class="lore-card-meta">
        ${Object.entries(l.attributes || {}).map(([k, v]) => `
          <div class="meta-row">
            <span class="meta-key">${escapeHtml(k.replace('_', ' '))}:</span>
            <span class="meta-val">${escapeHtml(v)}</span>
          </div>
        `).join('')}
      </div>
      ${(l.citations || []).slice(0, 1).map(cit => `
        <div class="lore-citation-item">
          ${cleanQuote(cit.quote)} <span class="font-mono" style="font-size:0.7rem; color:var(--text-muted);">(Ch. ${cit.chapter_id})</span>
        </div>
      `).join('')}
    </div>
  `).join('');

  // World Rules
  const ruleGrid = document.getElementById('bibleRules');
  ruleGrid.innerHTML = (b.world_rules || []).map(r => `
    <div class="lore-card">
      <div class="lore-card-header">
        <h4 class="lore-card-name">${escapeHtml(r.name)}</h4>
        <span class="tag-badge">${r.domain}</span>
      </div>
      <p style="font-family: var(--font-serif); font-size: 0.95rem; margin-bottom: 0.65rem; color: #D3DBE8; line-height: 1.5;">
        ${cleanQuote(r.statement)}
      </p>
      ${(r.citations || []).slice(0, 1).map(cit => `
        <div class="lore-citation-item">
          ${cleanQuote(cit.quote)} <span class="font-mono" style="font-size:0.7rem; color:var(--text-muted);">(Ch. ${cit.chapter_id})</span>
        </div>
      `).join('')}
    </div>
  `).join('');
}

function filterBibleEntries(term) {
  document.querySelectorAll('.lore-card').forEach(card => {
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(term) ? 'block' : 'none';
  });
}

function saveLoreEntry() {
  const cat = document.getElementById('loreCategory').value;
  const name = document.getElementById('loreName').value.trim();
  const stmt = document.getElementById('loreStatement').value.trim();
  if (!name || !stmt) return;

  closeModal('addLoreModal');

  if (cat === 'world_rule') {
    fetch('/api/bible/rules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, statement: stmt })
    }).then(() => loadBibleData());
  } else {
    fetch('/api/bible/entities', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, category: cat, notes: stmt })
    }).then(() => loadBibleData());
  }
}

// ==========================================================================
// TAB 4: "WHO KNOWS THIS?" MATRIX (NO DUPLICATE QUOTES, DEDUPLICATED ROWS)
// ==========================================================================

function renderKnowledgeMatrix() {
  const tbody = document.getElementById('knowledgeMatrixBody');
  if (!tbody) return;

  const rawItems = state.bible?.knowledge_items || [];
  if (rawItems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:2rem; color:var(--text-muted);">No confidential lore catalogued yet.</td></tr>`;
    return;
  }

  // Deduplicate items by fact_summary or ID
  const seen = new Set();
  const uniqueItems = [];
  for (const item of rawItems) {
    const key = item.id || item.fact_summary;
    if (!seen.has(key)) {
      seen.add(key);
      uniqueItems.push(item);
    }
  }

  tbody.innerHTML = uniqueItems.map(k => `
    <tr>
      <td>
        <strong style="color:var(--text-primary); font-size:0.9rem;">${escapeHtml(k.fact_summary)}</strong>
        <div class="lore-citation-item" style="margin-top:0.35rem;">
          ${cleanQuote(k.source_quote)}
        </div>
      </td>
      <td class="font-mono" style="font-size:0.78rem;">Chapter ${k.first_chapter_id}</td>
      <td>
        ${(k.known_by || []).map(c => `
          <span class="pill-status known">
            <svg class="inline-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            ${escapeHtml(c)}
          </span>
        `).join('')}
      </td>
      <td>
        ${(k.unknown_to || []).map(c => `
          <span class="pill-status unknown">
            <svg class="inline-status-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="16" height="11" x="4" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            ${escapeHtml(c)}
          </span>
        `).join('')}
      </td>
      <td>
        <span class="tag-badge ${k.is_secret ? 'high' : ''}">
          ${k.is_secret ? 'Secret' : 'Public'}
        </span>
      </td>
    </tr>
  `).join('');
}

// ==========================================================================
// TAB 5: TIMELINE
// ==========================================================================

function renderTimeline() {
  const stream = document.getElementById('timelineStream');
  const events = state.bible?.timeline_events || [];
  if (!stream) return;

  if (events.length === 0) {
    stream.innerHTML = `<p style="color:var(--text-muted); font-size:0.84rem;">No timeline milestones catalogued yet.</p>`;
    return;
  }

  stream.innerHTML = events.map(e => {
    const quoteText = (e.quote || '').trim();
    const descText = (e.event_description || '').trim();
    const isDuplicate = !quoteText || 
      quoteText.toLowerCase() === descText.toLowerCase() ||
      cleanQuote(quoteText).toLowerCase() === cleanQuote(descText).toLowerCase();

    return `
      <div class="timeline-card">
        <div class="timeline-meta-bar">
          <strong style="color:var(--accent-gold); font-size:0.8rem;">[Ch. ${e.chapter_id} · ${escapeHtml(e.timestamp_desc)}]</strong>
          <span style="color:var(--text-muted); font-size:0.72rem;">${escapeHtml(formatChapterDisplay(e.chapter_id, e.chapter_title))}</span>
        </div>
        <p style="font-size:0.88rem; color:#E2E8F0; line-height:1.5; margin-bottom:0.3rem;">
          ${escapeHtml(e.event_description)}
        </p>
        ${!isDuplicate ? `<div class="lore-citation-item">${cleanQuote(e.quote)}</div>` : ''}
      </div>
    `;
  }).join('');
}

// ==========================================================================
// TAB 6: MARKET BENCHMARK (NO LOCALHOST LINK, DATE STAMP, ACCURATE TOOLS)
// ==========================================================================

function loadReferencesData() {
  fetch('/api/references')
    .then(res => res.json())
    .then(data => {
      renderCompetitorTable(data.competitors || []);
      renderDemandCards(data.demand_evidence || []);
    })
    .catch(err => console.error("Error loading references:", err));
}

function renderCompetitorTable(competitors) {
  const tbody = document.getElementById('competitorTableBody');
  if (!tbody) return;

  tbody.innerHTML = competitors.map(c => {
    const isCanonLedger = c.name === 'Canon Ledger';
    const rowStyle = isCanonLedger ? 'style="background: rgba(201, 162, 39, 0.08);"' : '';

    return `
      <tr ${rowStyle}>
        <td>
          <strong style="${isCanonLedger ? 'color: var(--accent-gold); font-size: 0.95rem;' : 'color: var(--text-primary);'}">
            ${escapeHtml(c.display_name || c.name)}
          </strong>
          ${c.url ? `
            <div style="font-size: 0.72rem; margin-top: 0.2rem;">
              <a href="${c.url}" target="_blank" style="color: var(--text-muted); text-decoration: underline;">
                ${c.url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]} ↗
              </a>
            </div>
          ` : ''}
          <div style="margin-top: 0.35rem;">
            <span class="tag-badge">${escapeHtml(c.category)}</span>
          </div>
        </td>
        <td>${escapeHtml(c.story_bible)}</td>
        <td style="font-size: 0.82rem;">${escapeHtml(c.auto_extraction)}</td>
        <td style="font-size: 0.82rem; ${isCanonLedger ? 'color: var(--status-red); font-weight: 600;' : ''}">
          ${escapeHtml(c.contradiction_check)}
        </td>
        <td>
          <strong style="${isCanonLedger ? 'color: var(--status-green);' : 'color: var(--text-muted);'}">
            ${escapeHtml(c.author_control)}
          </strong>
        </td>
        <td style="font-size: 0.8rem; color: #9BA5B7;">
          ${escapeHtml(c.edge_note)}
        </td>
      </tr>
    `;
  }).join('');
}

function renderDemandCards(demands) {
  const container = document.getElementById('demandCards');
  if (!container) return;

  container.innerHTML = demands.map(d => {
    let quoteHtml = '';
    const srcName = d.source_name || d.source;
    if (d.is_paraphrase) {
      // Remove quotation marks and show as a paraphrase labelled "Paraphrase of [source name]"
      const unquoted = String(d.quote || '').replace(/^["'“\u201c\u2018\u00ab]+|["'”\u201d\u2019\u00bb]+$/g, '').trim();
      quoteHtml = `Paraphrase of ${escapeHtml(srcName)}: ${escapeHtml(unquoted)}`;
    } else {
      // Exact copy of source text in quotation marks
      quoteHtml = cleanQuote(d.quote);
    }

    return `
      <div class="demand-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.3rem;">
          <div class="demand-title">${escapeHtml(d.title)}</div>
          <a href="${d.url}" target="_blank" style="font-size: 0.7rem; color: var(--accent-gold); text-decoration: underline;">
            Source ↗
          </a>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.4rem;">
          ${escapeHtml(d.source)}
        </div>
        <div class="demand-quote font-serif">
          ${quoteHtml}
        </div>
        <div style="font-size: 0.76rem; color: var(--text-secondary); margin-top: 0.4rem;">
          <strong>Market Implication:</strong> ${escapeHtml(d.significance)}
        </div>
      </div>
    `;
  }).join('');
}

// ==========================================================================
// DEMO GUIDE & PRECEDENTS
// ==========================================================================

function loadDemoStory() {
  showToast("Loading 3-chapter manuscript with 5 planted errors...");
  fetch('/api/demo/load', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
      showToast("Demo story loaded!");
      loadBibleData();
      switchTab('tabFlags');
    });
}

function openDemoGuide() {
  fetch('/api/demo/guide')
    .then(res => res.json())
    .then(data => {
      const precedentEl = document.getElementById('precedentCards');
      if (precedentEl) {
        precedentEl.innerHTML = data.real_world_examples.map(ex => `
          <div class="precedent-item">
            <h5>${escapeHtml(ex.author)} — <em>${escapeHtml(ex.book)}</em></h5>
            <p style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.2rem;">
              <strong>Error:</strong> ${escapeHtml(ex.details)}
            </p>
            <p style="font-size:0.74rem; color:var(--accent-gold);">
              <strong>Reader Impact:</strong> ${escapeHtml(ex.reader_impact)}
            </p>
          </div>
        `).join('');
      }

      const timelineEl = document.getElementById('scriptTimeline');
      if (timelineEl) {
        timelineEl.innerHTML = data.steps.map(s => `
          <div class="script-card">
            <div class="script-time-tag">Step ${s.step} (${s.time}) · ${escapeHtml(s.title)}</div>
            <p style="font-size:0.84rem; color:#E2E8F0; margin-top:0.3rem; line-height:1.5;">${escapeHtml(s.script)}</p>
          </div>
        `).join('');
      }

      openModal('demoGuideModal');
    });
}

// ==========================================================================
// MODALS & UTILITIES
// ==========================================================================

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  if (id === 'editChapterModal') {
    const textarea = document.getElementById('editModalTextarea');
    if (textarea && state.initialEditText !== undefined && textarea.value !== state.initialEditText) {
      if (!confirm("You have unsaved edits. Discard changes?")) {
        return false;
      }
    }
  }
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
  return true;
}

function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.style.display = 'block';
  setTimeout(() => {
    toast.style.display = 'none';
  }, 3500);
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
