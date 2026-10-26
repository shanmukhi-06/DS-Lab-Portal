/**
 * Data Science Laboratory Digital Library & Record
 * Complete Interactive Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global State
  let currentStudent = null;
  let allExperiments = [];
  let allModules = [];
  let allTools = [];
  let allResources = [];
  let pendingDelete = null; // { type: 'experiment'|'module'|'tool'|'resource', id: number, label: string }

  // DOM Elements - Student ID Card & Nav
  const idPhoto = document.getElementById('idPhoto');
  const idName = document.getElementById('idName');
  const idRoll = document.getElementById('idRoll');
  const idDept = document.getElementById('idDept');
  const idSec = document.getElementById('idSec');
  const idSub = document.getElementById('idSub');
  const idFaculty = document.getElementById('idFaculty');
  const idWebLink = document.getElementById('idWebLink');
  const idGhLink = document.getElementById('idGhLink');
  const editProfileBtn = document.getElementById('editProfileBtn');
  const navAvatarImg = document.getElementById('navAvatarImg');
  const navStudentName = document.getElementById('navStudentName');
  const navProfileTrigger = document.getElementById('navProfileTrigger');

  // DOM Elements - Overview Counts
  const countModules = document.getElementById('countModules');
  const countExperiments = document.getElementById('countExperiments');
  const countTools = document.getElementById('countTools');
  const countResources = document.getElementById('countResources');

  // DOM Elements - Nav & Tabs
  const navLinks = document.querySelectorAll('.nav-link');
  const contentSections = {
    modules: document.getElementById('section-modules'),
    labexp: document.getElementById('section-labexp'),
    tools: document.getElementById('section-tools'),
    resources: document.getElementById('section-resources')
  };

  // DOM Elements - Experiments
  const experimentGrid = document.getElementById('experimentGrid');
  const emptyState = document.getElementById('emptyState');
  const searchInput = document.getElementById('searchInput');
  const experimentCountBadge = document.getElementById('experimentCountBadge');
  const openAddExpModalBtn = document.getElementById('openAddExpModalBtn');
  const quickAddExpBtn = document.getElementById('quickAddExpBtn');

  // DOM Elements - Modules
  const modulesGrid = document.getElementById('modulesGrid');
  const openAddModuleModalBtn = document.getElementById('openAddModuleModalBtn');
  const quickAddModuleBtn = document.getElementById('quickAddModuleBtn');
  const addModuleModal = document.getElementById('addModuleModal');
  const addModuleForm = document.getElementById('addModuleForm');
  const submitModBtn = document.getElementById('submitModBtn');

  // DOM Elements - Tools
  const toolsGrid = document.getElementById('toolsGrid');
  const openAddToolModalBtn = document.getElementById('openAddToolModalBtn');
  const quickAddToolBtn = document.getElementById('quickAddToolBtn');
  const addToolModal = document.getElementById('addToolModal');
  const addToolForm = document.getElementById('addToolForm');
  const submitToolBtn = document.getElementById('submitToolBtn');

  // DOM Elements - Resources
  const resourcesGrid = document.getElementById('resourcesGrid');
  const openAddResourceModalBtn = document.getElementById('openAddResourceModalBtn');
  const quickAddResBtn = document.getElementById('quickAddResBtn');
  const addResourceModal = document.getElementById('addResourceModal');
  const addResourceForm = document.getElementById('addResourceForm');
  const submitResBtn = document.getElementById('submitResBtn');

  // DOM Elements - Add Experiment Modal
  const addExperimentModal = document.getElementById('addExperimentModal');
  const addExperimentForm = document.getElementById('addExperimentForm');
  const coverDropzone = document.getElementById('coverDropzone');
  const coverImageInput = document.getElementById('coverImageInput');
  const coverPreviewContainer = document.getElementById('coverPreviewContainer');
  const coverPreviewImg = document.getElementById('coverPreviewImg');
  const coverPrompt = document.getElementById('coverPrompt');
  const removeCoverBtn = document.getElementById('removeCoverBtn');
  const chooseVideoBtn = document.getElementById('chooseVideoBtn');
  const videoInput = document.getElementById('videoInput');
  const videoFileName = document.getElementById('videoFileName');
  const removeVideoBtn = document.getElementById('removeVideoBtn');
  const submitExpBtn = document.getElementById('submitExpBtn');

  // DOM Elements - Details Modal
  const mbuPhysicalIdCard = document.getElementById('mbuPhysicalIdCard');
  const openIdCardModalBtn = document.getElementById('openIdCardModalBtn');
  const idCardModal = document.getElementById('idCardModal');
  const detailsModal = document.getElementById('detailsModal');
  const detailExpNo = document.getElementById('detailExpNo');
  const detailTitle = document.getElementById('detailTitle');
  const detailDesc = document.getElementById('detailDesc');
  const detailCoverImg = document.getElementById('detailCoverImg');
  const detailVideoWrapper = document.getElementById('detailVideoWrapper');
  const detailVideoPlayer = document.getElementById('detailVideoPlayer');
  const detailGithubLink = document.getElementById('detailGithubLink');
  const detailD2Heading = document.getElementById('detailD2Heading');
  const detailLongContent = document.getElementById('detailLongContent');

  // DOM Elements - Edit ID Card Modal
  const editProfileModal = document.getElementById('editProfileModal');
  const editProfileForm = document.getElementById('editProfileForm');
  const profilePhotoInput = document.getElementById('profilePhotoInput');
  const editPhotoPreview = document.getElementById('editPhotoPreview');
  const profNameInput = document.getElementById('profNameInput');
  const profRollInput = document.getElementById('profRollInput');
  const profDeptInput = document.getElementById('profDeptInput');
  const profSectionInput = document.getElementById('profSectionInput');
  const profSubInput = document.getElementById('profSubInput');
  const profFacultyInput = document.getElementById('profFacultyInput');
  const profGithubInput = document.getElementById('profGithubInput');
  const profWebsiteInput = document.getElementById('profWebsiteInput');
  const saveProfileBtn = document.getElementById('saveProfileBtn');

  // DOM Elements - Delete Confirmation Modal
  const deleteConfirmModal = document.getElementById('deleteConfirmModal');
  const deleteExperimentTargetTitle = document.getElementById('deleteExperimentTargetTitle');
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

  // Toast
  const toast = document.getElementById('toast');
  let toastTimer = null;

  // -------------------------------------------------------------
  // INITIALIZATION
  // -------------------------------------------------------------
  async function init() {
    await Promise.all([
      fetchStudent(),
      fetchCounts(),
      fetchExperiments(),
      fetchModules(),
      fetchTools(),
      fetchResources()
    ]);
    attachEventListeners();
  }

  // -------------------------------------------------------------
  // API FETCH CALLS
  // -------------------------------------------------------------
  async function fetchCounts() {
    try {
      const res = await fetch('/api/counts');
      const data = await res.json();
      if (data.success && data.data) {
        countModules.textContent = `${data.data.modules} Modules`;
        countExperiments.textContent = `${data.data.experiments} Exp`;
        countTools.textContent = `${data.data.tools} Tools`;
        countResources.textContent = `${data.data.resources} Resources`;
      }
    } catch (err) {
      console.error('Failed to load counts:', err);
    }
  }

  async function fetchStudent() {
    try {
      const res = await fetch('/api/student');
      const data = await res.json();
      if (data.success && data.data) {
        currentStudent = data.data;
        renderStudent(currentStudent);
      }
    } catch (err) {
      console.error('Failed to load student details:', err);
      showToast('Could not load student profile', 'error');
    }
  }

  async function fetchExperiments(searchQuery = '') {
    try {
      const url = searchQuery ? `/api/experiments?q=${encodeURIComponent(searchQuery)}` : '/api/experiments';
      const res = await fetch(url);
      const data = await res.json();
      if (data.success) {
        allExperiments = data.data || [];
        renderExperiments(allExperiments);
      }
    } catch (err) {
      console.error('Failed to load experiments:', err);
      showToast('Could not load experiments', 'error');
    }
  }

  async function fetchModules() {
    try {
      const res = await fetch('/api/modules');
      const data = await res.json();
      if (data.success) {
        allModules = data.data || [];
        renderModules(allModules);
      }
    } catch (err) {
      console.error('Failed to load modules:', err);
    }
  }

  async function fetchTools() {
    try {
      const res = await fetch('/api/tools');
      const data = await res.json();
      if (data.success) {
        allTools = data.data || [];
        renderTools(allTools);
      }
    } catch (err) {
      console.error('Failed to load tools:', err);
    }
  }

  async function fetchResources() {
    try {
      const res = await fetch('/api/resources');
      const data = await res.json();
      if (data.success) {
        allResources = data.data || [];
        renderResources(allResources);
      }
    } catch (err) {
      console.error('Failed to load resources:', err);
    }
  }

  // -------------------------------------------------------------
  // RENDERING
  // -------------------------------------------------------------
  function renderStudent(student) {
    if (!student) return;
    idName.textContent = student.name || 'Shanmukhi';
    idRoll.textContent = student.roll_no || '24102A030132';
    idDept.textContent = student.branch || student.department || 'Data Science';
    idSec.textContent = student.section || 'DS-3';
    idSub.textContent = student.subject || 'Data Science';
    idFaculty.textContent = student.faculty || 'Faculty In-Charge';

    const photoSrc = student.photo_url || '/static/images/shanmukhi-profile.png';
    if (idPhoto) idPhoto.src = photoSrc;
    if (navAvatarImg) navAvatarImg.src = photoSrc;
    if (navStudentName) navStudentName.textContent = student.name || 'Shanmukhi';

    // Social Links
    if (student.github_url && student.github_url.trim() !== '') {
      idGhLink.href = student.github_url;
      idGhLink.hidden = false;
    } else {
      idGhLink.hidden = true;
    }

    if (student.website_url && student.website_url.trim() !== '') {
      idWebLink.href = student.website_url;
      idWebLink.hidden = false;
    } else {
      idWebLink.href = '#';
    }
  }

  function renderExperiments(experiments) {
    experimentGrid.innerHTML = '';
    const count = experiments.length;
    experimentCountBadge.textContent = `${count} ${count === 1 ? 'Experiment' : 'Experiments'}`;

    if (count === 0) {
      emptyState.hidden = false;
      return;
    }

    emptyState.hidden = true;

    experiments.forEach((exp) => {
      const card = document.createElement('article');
      card.className = 'exp-card';
      card.dataset.id = exp.id;

      const coverSrc = exp.cover_image || '/static/images/default-cover.svg';
      const githubBtnHtml = exp.github_url && exp.github_url.trim() !== ''
        ? `<a href="${escapeHtml(exp.github_url)}" target="_blank" rel="noopener noreferrer" class="btn-card-gh" title="View Repository">
             <svg viewBox="0 0 16 16" width="13" height="13" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.6 7.6 0 0 1 4 0c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>
             GitHub
           </a>`
        : '';

      card.innerHTML = `
        <div class="exp-card__cover">
          <img src="${escapeHtml(coverSrc)}" alt="Cover for Experiment ${escapeHtml(exp.experiment_no)}" loading="lazy">
          <span class="exp-card__badge">EXP ${escapeHtml(exp.experiment_no)}</span>
        </div>
        <div class="exp-card__content">
          <div class="exp-card__header">
            <span class="exp-card__num-tag">Experiment ${escapeHtml(exp.experiment_no)}</span>
            <h3 class="exp-card__title">${escapeHtml(exp.title)}</h3>
            <p class="exp-card__desc">${escapeHtml(exp.short_description)}</p>
          </div>
          <div class="exp-card__footer">
            <div class="exp-card__actions-left">
              <button type="button" class="btn btn--primary btn-card-read" data-action="read" data-id="${exp.id}">Read More</button>
              ${githubBtnHtml}
            </div>
            <button type="button" class="btn-card-delete" data-action="delete-exp" data-id="${exp.id}" title="Delete experiment">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
            </button>
          </div>
        </div>
      `;

      experimentGrid.appendChild(card);
    });
  }

  function renderModules(modules) {
    modulesGrid.innerHTML = '';
    if (!modules || modules.length === 0) {
      modulesGrid.innerHTML = `<p class="empty-note" style="color:var(--muted);font-style:italic;">No modules added yet. Click + Add Module to create one.</p>`;
      return;
    }

    modules.forEach((mod) => {
      const card = document.createElement('div');
      card.className = 'module-card';
      card.setAttribute('data-module-id', mod.id);

      const pages = Array.isArray(mod.pages_json) ? mod.pages_json : [];
      const videos = Array.isArray(mod.youtube_links) ? mod.youtube_links : [];
      const pageCount = pages.length || 7;
      const videoCount = videos.length || 5;
      const pdfUrl = mod.pdf_url || `/static/docs/Module-${mod.module_no}-Data-Science-Foundations.pdf`;

      const topicList = (mod.topics || '').split(',').map(t => t.trim()).filter(Boolean);
      const topicPillsHtml = topicList.slice(0, 5).map(t => `<span class="topic-pill">${escapeHtml(t)}</span>`).join('');

      card.innerHTML = `
        <div class="module-header">
          <span class="module-badge">UNIT ${escapeHtml(mod.module_no)}</span>
          <div style="display:flex;align-items:center;gap:8px;">
            <span class="module-pages-badge">${pageCount} Pages &bull; ${videoCount} Lectures</span>
            <button type="button" class="btn-text-danger" data-action="delete-mod" data-id="${mod.id}" title="Delete module">&times;</button>
          </div>
        </div>
        <h3 class="module-title" style="cursor:pointer;" title="Click to open module">${escapeHtml(mod.title)}</h3>
        <p class="module-desc">${escapeHtml(mod.description)}</p>
        ${topicPillsHtml ? `
          <div class="module-topics-box">
            <div class="module-topics-title">Key Core Syllabus:</div>
            <div class="module-topics-pills">${topicPillsHtml}</div>
          </div>
        ` : ''}
        <div class="module-actions-bar">
          <a href="${pdfUrl}" target="_blank" rel="noopener noreferrer" class="btn btn--primary btn--sm open-pdf-direct-btn" data-id="${mod.id}" title="Read Module PDF Document">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v4zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zm5 2h1v-3h-1v3zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6z"/>
            </svg>
            <span>Read Module (PDF)</span>
          </a>
          <button type="button" class="btn btn--youtube btn--sm open-videos-btn" data-id="${mod.id}">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
            </svg>
            <span>Video Lectures (${videoCount})</span>
          </button>
        </div>
      `;
      modulesGrid.appendChild(card);
    });
  }

  function renderTools(tools) {
    toolsGrid.innerHTML = '';
    if (!tools || tools.length === 0) {
      toolsGrid.innerHTML = `<p class="empty-note" style="color:var(--muted);font-style:italic;">No tools added yet. Click + Add Tool to create one.</p>`;
      return;
    }

    tools.forEach((tool) => {
      const card = document.createElement('div');
      card.className = 'tool-card';
      const linkHtml = tool.tool_url && tool.tool_url.trim() !== ''
        ? `<a href="${escapeHtml(tool.tool_url)}" target="_blank" rel="noopener noreferrer" class="btn btn--sm btn--secondary tool-link-btn">Open Tool &rarr;</a>`
        : '';

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span class="tool-category-badge">${escapeHtml(tool.category || 'General')}</span>
          <button type="button" class="btn-text-danger" data-action="delete-tool" data-id="${tool.id}" title="Delete tool">&times;</button>
        </div>
        <h4 class="tool-name">${escapeHtml(tool.name)}</h4>
        <p class="tool-desc">${escapeHtml(tool.description)}</p>
        ${linkHtml}
      `;
      toolsGrid.appendChild(card);
    });
  }

  function renderResources(resources) {
    resourcesGrid.innerHTML = '';
    if (!resources || resources.length === 0) {
      resourcesGrid.innerHTML = `<p class="empty-note" style="color:var(--muted);font-style:italic;">No resources added yet. Click + Add Resource to create one.</p>`;
      return;
    }

    resources.forEach((res) => {
      const card = document.createElement('div');
      card.className = 'resource-card';
      const linkHtml = res.link_url && res.link_url.trim() !== '#' && res.link_url.trim() !== ''
        ? `<a href="${escapeHtml(res.link_url)}" target="_blank" rel="noopener noreferrer" class="btn btn--sm btn--primary resource-link-btn">Access Resource &rarr;</a>`
        : `<span style="font-size:0.78rem;color:var(--muted);margin-top:auto;">Internal Library Archive</span>`;

      card.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span class="resource-cat-badge">${escapeHtml(res.category || 'Reference')}</span>
          <button type="button" class="btn-text-danger" data-action="delete-res" data-id="${res.id}" title="Delete resource">&times;</button>
        </div>
        <h4 class="resource-title">${escapeHtml(res.title)}</h4>
        <p class="resource-desc">${escapeHtml(res.description)}</p>
        ${linkHtml}
      `;
      resourcesGrid.appendChild(card);
    });
  }

  // -------------------------------------------------------------
  // EVENT LISTENERS & NAVIGATION
  // -------------------------------------------------------------
  function attachEventListeners() {
    // Navigation link clicks (Home, Modules, Lab Exp, Tools, Resources)
    navLinks.forEach((btn) => {
      btn.addEventListener('click', () => {
        navLinks.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');

        const tab = btn.dataset.tab;
        if (tab === 'all') {
          // Show all sections
          Object.values(contentSections).forEach((sec) => (sec.hidden = false));
          window.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
          // Show all or scroll to specific section
          Object.values(contentSections).forEach((sec) => (sec.hidden = false));
          const targetSection = contentSections[tab];
          if (targetSection) {
            targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }
      });
    });

    // Overview cards "View more" buttons
    document.querySelectorAll('[data-nav-target]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.navTarget;
        const navBtn = document.querySelector(`.nav-link[data-tab="${target}"]`);
        if (navBtn) navBtn.click();
      });
    });

    // Quick Add buttons on overview cards
    quickAddExpBtn.addEventListener('click', () => {
      openModal(addExperimentModal);
      resetAddExperimentForm();
    });
    openAddExpModalBtn.addEventListener('click', () => {
      openModal(addExperimentModal);
      resetAddExperimentForm();
    });

    quickAddModuleBtn.addEventListener('click', () => openModal(addModuleModal));
    openAddModuleModalBtn.addEventListener('click', () => openModal(addModuleModal));

    quickAddToolBtn.addEventListener('click', () => openModal(addToolModal));
    openAddToolModalBtn.addEventListener('click', () => openModal(addToolModal));

    quickAddResBtn.addEventListener('click', () => openModal(addResourceModal));
    openAddResourceModalBtn.addEventListener('click', () => openModal(addResourceModal));

    // Nav avatar click opens edit profile modal (if present)
    if (navProfileTrigger) navProfileTrigger.addEventListener('click', openProfileEditModal);
    if (editProfileBtn) editProfileBtn.addEventListener('click', openProfileEditModal);

    // Search input live filter for experiments
    searchInput.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase().trim();
      if (!query) {
        renderExperiments(allExperiments);
        return;
      }
      const filtered = allExperiments.filter((exp) => {
        const num = (exp.experiment_no || '').toLowerCase();
        const title = (exp.title || '').toLowerCase();
        const desc = (exp.short_description || '').toLowerCase();
        return num.includes(query) || title.includes(query) || desc.includes(query);
      });
      renderExperiments(filtered);
    });

    // Card Actions Delegation
    experimentGrid.addEventListener('click', (e) => {
      const readBtn = e.target.closest('[data-action="read"]');
      if (readBtn) {
        const expId = parseInt(readBtn.dataset.id, 10);
        openDetailsModal(expId);
        return;
      }

      const delBtn = e.target.closest('[data-action="delete-exp"]');
      if (delBtn) {
        const expId = parseInt(delBtn.dataset.id, 10);
        const exp = allExperiments.find((i) => i.id === expId);
        openDeleteModal('experiment', expId, `Experiment ${exp ? exp.experiment_no : ''}: "${exp ? exp.title : ''}"`);
        return;
      }
    });

    // Module card buttons (Flip Book & Videos)
    modulesGrid.addEventListener('click', (e) => {
      const openBookBtn = e.target.closest('.open-book-btn');
      if (openBookBtn) {
        const modId = parseInt(openBookBtn.getAttribute('data-id'), 10);
        openModuleBook(modId, 1);
        return;
      }
      const titleClick = e.target.closest('.module-title');
      if (titleClick) {
        const card = titleClick.closest('.module-card');
        const modId = parseInt(card.getAttribute('data-module-id'), 10);
        openModuleBook(modId, 1);
        return;
      }
      const openVideosBtn = e.target.closest('.open-videos-btn');
      if (openVideosBtn) {
        const modId = parseInt(openVideosBtn.getAttribute('data-id'), 10);
        openModuleVideosModal(modId);
        return;
      }
    });

    // Flipbook controls
    if (bookPrevBtn) bookPrevBtn.addEventListener('click', flipPrevSpread);
    if (bookNextBtn) bookNextBtn.addEventListener('click', flipNextSpread);
    if (leftPageSheet) leftPageSheet.addEventListener('click', (e) => {
      if (e.target.closest('a, button, input, select, textarea, .video-ref-link, .video-ref-card')) return;
      flipPrevSpread();
    });
    if (rightPageSheet) rightPageSheet.addEventListener('click', (e) => {
      if (e.target.closest('a, button, input, select, textarea, .video-ref-link, .video-ref-card')) return;
      flipNextSpread();
    });
    if (bookTocToggleBtn) bookTocToggleBtn.addEventListener('click', toggleTocDrawer);
    if (closeTocDrawerBtn) closeTocDrawerBtn.addEventListener('click', toggleTocDrawer);
    if (bookVideosToggleBtn) bookVideosToggleBtn.addEventListener('click', toggleVideosDrawer);
    if (closeVideosDrawerBtn) closeVideosDrawerBtn.addEventListener('click', toggleVideosDrawer);
    if (bookPageSlider) {
      bookPageSlider.addEventListener('input', (e) => {
        jumpToPage(parseInt(e.target.value, 10));
      });
    }

    // Keyboard navigation for flipbook
    document.addEventListener('keydown', (e) => {
      if (moduleBookModal && !moduleBookModal.hidden) {
        if (e.key === 'ArrowRight') {
          e.preventDefault();
          flipNextSpread();
        } else if (e.key === 'ArrowLeft') {
          e.preventDefault();
          flipPrevSpread();
        }
      }
    });

        modulesGrid.addEventListener('click', (e) => {
      const delBtn = e.target.closest('[data-action="delete-mod"]');
      if (delBtn) {
        const modId = parseInt(delBtn.dataset.id, 10);
        const mod = allModules.find((i) => i.id === modId);
        openDeleteModal('module', modId, `Module ${mod ? mod.module_no : ''}: "${mod ? mod.title : ''}"`);
      }
    });

    toolsGrid.addEventListener('click', (e) => {
      const delBtn = e.target.closest('[data-action="delete-tool"]');
      if (delBtn) {
        const toolId = parseInt(delBtn.dataset.id, 10);
        const tool = allTools.find((i) => i.id === toolId);
        openDeleteModal('tool', toolId, `Tool: "${tool ? tool.name : ''}"`);
      }
    });

    resourcesGrid.addEventListener('click', (e) => {
      const delBtn = e.target.closest('[data-action="delete-res"]');
      if (delBtn) {
        const resId = parseInt(delBtn.dataset.id, 10);
        const r = allResources.find((i) => i.id === resId);
        openDeleteModal('resource', resId, `Resource: "${r ? r.title : ''}"`);
      }
    });

    // Physical ID Card Modal
    if (mbuPhysicalIdCard && idCardModal) {
      mbuPhysicalIdCard.addEventListener('click', () => {
        openModal(idCardModal);
      });
      mbuPhysicalIdCard.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          openModal(idCardModal);
        }
      });
    }
    if (openIdCardModalBtn && idCardModal) {
      openIdCardModalBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openModal(idCardModal);
      });
    }

    // Modal close controls
    document.querySelectorAll('[data-close-modal]').forEach((el) => {
      el.addEventListener('click', (e) => {
        const modal = e.target.closest('.modal');
        if (modal) closeModal(modal);
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal:not([hidden])').forEach((m) => closeModal(m));
      }
    });

    // Cover image file drag/drop / change
    coverDropzone.addEventListener('click', (e) => {
      if (e.target !== removeCoverBtn && !removeCoverBtn.contains(e.target)) {
        coverImageInput.click();
      }
    });
    coverImageInput.addEventListener('change', handleCoverFileSelect);
    removeCoverBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      coverImageInput.value = '';
      coverPreviewImg.src = '';
      coverPreviewContainer.hidden = true;
      coverPrompt.hidden = false;
    });

    // Video select
    chooseVideoBtn.addEventListener('click', () => videoInput.click());
    videoInput.addEventListener('change', () => {
      if (videoInput.files && videoInput.files[0]) {
        videoFileName.textContent = videoInput.files[0].name;
        removeVideoBtn.hidden = false;
      } else {
        videoFileName.textContent = 'No video selected (MP4, WebM, MOV)';
        removeVideoBtn.hidden = true;
      }
    });
    removeVideoBtn.addEventListener('click', () => {
      videoInput.value = '';
      videoFileName.textContent = 'No video selected (MP4, WebM, MOV)';
      removeVideoBtn.hidden = true;
    });

    // Profile photo preview
    profilePhotoInput.addEventListener('change', () => {
      if (profilePhotoInput.files && profilePhotoInput.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
          editPhotoPreview.src = e.target.result;
        };
        reader.readAsDataURL(profilePhotoInput.files[0]);
      }
    });

    // Form Submissions
    addExperimentForm.addEventListener('submit', handleAddExperimentSubmit);
    addModuleForm.addEventListener('submit', handleAddModuleSubmit);
    addToolForm.addEventListener('submit', handleAddToolSubmit);
    addResourceForm.addEventListener('submit', handleAddResourceSubmit);
    editProfileForm.addEventListener('submit', handleEditProfileSubmit);
    confirmDeleteBtn.addEventListener('click', handleConfirmDelete);
  }

  // -------------------------------------------------------------
  // EXPERIMENT HANDLERS
  // -------------------------------------------------------------
  function resetAddExperimentForm() {
    addExperimentForm.reset();
    coverImageInput.value = '';
    coverPreviewImg.src = '';
    coverPreviewContainer.hidden = true;
    coverPrompt.hidden = false;
    videoInput.value = '';
    videoFileName.textContent = 'No video selected (MP4, WebM, MOV)';
    removeVideoBtn.hidden = true;
    clearFieldErrors();
  }

  function handleCoverFileSelect() {
    if (coverImageInput.files && coverImageInput.files[0]) {
      const file = coverImageInput.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        coverPreviewImg.src = e.target.result;
        coverPreviewContainer.hidden = false;
        coverPrompt.hidden = true;
      };
      reader.readAsDataURL(file);
    }
  }

  async function handleAddExperimentSubmit(e) {
    e.preventDefault();
    clearFieldErrors();

    const expNum = document.getElementById('expNumberInput').value.trim();
    const expTitle = document.getElementById('expTitleInput').value.trim();
    const expDesc = document.getElementById('expShortDescInput').value.trim();
    const expD2Head = document.getElementById('expD2HeadingInput').value.trim();
    const expLongContent = document.getElementById('expLongContentInput').value.trim();
    const expGithub = document.getElementById('expGithubInput').value.trim();

    let hasError = false;
    if (!expNum) {
      setFieldError('err-exp-num', 'Experiment number is required');
      hasError = true;
    }
    if (!expTitle) {
      setFieldError('err-exp-title', 'Experiment name is required');
      hasError = true;
    }
    if (!expDesc) {
      setFieldError('err-exp-desc', 'Short description is required');
      hasError = true;
    }
    if (!expLongContent) {
      setFieldError('err-exp-content', 'Complete experiment content is required');
      hasError = true;
    }

    if (hasError) return;

    const formData = new FormData();
    formData.append('experiment_no', expNum);
    formData.append('title', expTitle);
    formData.append('short_description', expDesc);
    formData.append('d2_heading', expD2Head || 'Long Description');
    formData.append('long_content', expLongContent);
    formData.append('github_url', expGithub);

    if (coverImageInput.files && coverImageInput.files[0]) {
      formData.append('cover_image', coverImageInput.files[0]);
    }
    if (videoInput.files && videoInput.files[0]) {
      formData.append('video', videoInput.files[0]);
    }

    submitExpBtn.disabled = true;
    submitExpBtn.textContent = 'Adding Experiment...';

    try {
      const res = await fetch('/api/experiments', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        closeModal(addExperimentModal);
        resetAddExperimentForm();
        await fetchExperiments(searchInput.value.trim());
        await fetchCounts();
        showToast('Experiment added successfully!', 'success');
      } else {
        showToast(data.message || 'Failed to add experiment', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Server error while saving experiment', 'error');
    } finally {
      submitExpBtn.disabled = false;
      submitExpBtn.textContent = 'Add Experiment';
    }
  }

  function openDetailsModal(expId) {
    const exp = allExperiments.find((i) => i.id === expId);
    if (!exp) return;

    detailExpNo.textContent = `Experiment ${exp.experiment_no}`;
    detailTitle.textContent = exp.title;
    detailDesc.textContent = exp.short_description;
    detailD2Heading.textContent = exp.d2_heading || 'Long Description';
    detailLongContent.textContent = exp.long_content;
    detailCoverImg.src = exp.cover_image || '/static/images/default-cover.svg';

    if (exp.video && exp.video.trim() !== '') {
      detailVideoPlayer.src = exp.video;
      detailVideoWrapper.hidden = false;
    } else {
      detailVideoPlayer.pause();
      detailVideoPlayer.src = '';
      detailVideoWrapper.hidden = true;
    }

    if (exp.github_url && exp.github_url.trim() !== '') {
      detailGithubLink.href = exp.github_url;
      detailGithubLink.hidden = false;
    } else {
      detailGithubLink.hidden = true;
    }

    openModal(detailsModal);
  }

  // -------------------------------------------------------------
  // MODULES, TOOLS, RESOURCES HANDLERS
  // -------------------------------------------------------------
  async function handleAddModuleSubmit(e) {
    e.preventDefault();
    const formData = new FormData(addModuleForm);
    submitModBtn.disabled = true;
    submitModBtn.textContent = 'Saving...';
    try {
      const res = await fetch('/api/modules', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        closeModal(addModuleModal);
        addModuleForm.reset();
        await fetchModules();
        await fetchCounts();
        showToast('Module added successfully!', 'success');
      } else {
        showToast(data.message || 'Error adding module', 'error');
      }
    } catch (err) {
      showToast('Server error', 'error');
    } finally {
      submitModBtn.disabled = false;
      submitModBtn.textContent = 'Add Module';
    }
  }

  async function handleAddToolSubmit(e) {
    e.preventDefault();
    const formData = new FormData(addToolForm);
    submitToolBtn.disabled = true;
    submitToolBtn.textContent = 'Saving...';
    try {
      const res = await fetch('/api/tools', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        closeModal(addToolModal);
        addToolForm.reset();
        await fetchTools();
        await fetchCounts();
        showToast('Tool added successfully!', 'success');
      } else {
        showToast(data.message || 'Error adding tool', 'error');
      }
    } catch (err) {
      showToast('Server error', 'error');
    } finally {
      submitToolBtn.disabled = false;
      submitToolBtn.textContent = 'Add Tool';
    }
  }

  async function handleAddResourceSubmit(e) {
    e.preventDefault();
    const formData = new FormData(addResourceForm);
    submitResBtn.disabled = true;
    submitResBtn.textContent = 'Saving...';
    try {
      const res = await fetch('/api/resources', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        closeModal(addResourceModal);
        addResourceForm.reset();
        await fetchResources();
        await fetchCounts();
        showToast('Resource added successfully!', 'success');
      } else {
        showToast(data.message || 'Error adding resource', 'error');
      }
    } catch (err) {
      showToast('Server error', 'error');
    } finally {
      submitResBtn.disabled = false;
      submitResBtn.textContent = 'Add Resource';
    }
  }

  // -------------------------------------------------------------
  // PROFILE EDIT
  // -------------------------------------------------------------
  function openProfileEditModal() {
    if (currentStudent) {
      profNameInput.value = currentStudent.name || '';
      profRollInput.value = currentStudent.roll_no || '';
      profDeptInput.value = currentStudent.branch || currentStudent.department || 'Data Science';
      profSectionInput.value = currentStudent.section || 'DS-3';
      profSubInput.value = currentStudent.subject || 'Data Science';
      profFacultyInput.value = currentStudent.faculty || 'Faculty In-Charge';
      profGithubInput.value = currentStudent.github_url || '';
      profWebsiteInput.value = currentStudent.website_url || '';
      editPhotoPreview.src = currentStudent.photo_url || '/static/images/shanmukhi-profile.png';
    }
    profilePhotoInput.value = '';
    openModal(editProfileModal);
  }

  async function handleEditProfileSubmit(e) {
    e.preventDefault();
    const name = profNameInput.value.trim();
    const rollNo = profRollInput.value.trim();

    if (!name || !rollNo) {
      showToast('Name and Roll Number are required', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('roll_no', rollNo);
    formData.append('branch', profDeptInput.value.trim());
    formData.append('section', profSectionInput.value.trim());
    formData.append('subject', profSubInput.value.trim() || 'Data Science');
    formData.append('faculty', profFacultyInput.value.trim() || 'Faculty In-Charge');
    formData.append('github_url', profGithubInput.value.trim());
    formData.append('website_url', profWebsiteInput.value.trim());

    if (profilePhotoInput.files && profilePhotoInput.files[0]) {
      formData.append('photo', profilePhotoInput.files[0]);
    }

    saveProfileBtn.disabled = true;
    saveProfileBtn.textContent = 'Saving...';

    try {
      const res = await fetch('/api/student', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success && data.data) {
        currentStudent = data.data;
        renderStudent(currentStudent);
        closeModal(editProfileModal);
        showToast('Student ID Card updated successfully!', 'success');
      } else {
        showToast(data.message || 'Failed to update profile', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Server error while updating profile', 'error');
    } finally {
      saveProfileBtn.disabled = false;
      saveProfileBtn.textContent = 'Save Changes';
    }
  }

  // -------------------------------------------------------------
  // DELETE LOGIC
  // -------------------------------------------------------------
  function openDeleteModal(type, id, label) {
    pendingDelete = { type, id, label };
    deleteExperimentTargetTitle.textContent = `${label} will be permanently removed.`;
    openModal(deleteConfirmModal);
  }

  async function handleConfirmDelete() {
    if (!pendingDelete) return;
    const { type, id } = pendingDelete;
    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.textContent = 'Deleting...';

    let endpoint = '';
    if (type === 'experiment') endpoint = `/api/experiments/${id}`;
    else if (type === 'module') endpoint = `/api/modules/${id}`;
    else if (type === 'tool') endpoint = `/api/tools/${id}`;
    else if (type === 'resource') endpoint = `/api/resources/${id}`;

    try {
      const res = await fetch(endpoint, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        closeModal(deleteConfirmModal);
        pendingDelete = null;
        if (type === 'experiment') await fetchExperiments(searchInput.value.trim());
        else if (type === 'module') await fetchModules();
        else if (type === 'tool') await fetchTools();
        else if (type === 'resource') await fetchResources();
        await fetchCounts();
        showToast('Record deleted successfully', 'success');
      } else {
        showToast(data.message || 'Could not delete record', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Server error during deletion', 'error');
    } finally {
      confirmDeleteBtn.disabled = false;
      confirmDeleteBtn.textContent = 'Delete';
    }
  }

  // -------------------------------------------------------------
  // MODAL UTILITIES & TOAST
  // -------------------------------------------------------------
  function openModal(modal) {
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function closeModal(modal) {
    modal.hidden = true;
    const anyOpen = document.querySelector('.modal:not([hidden])');
    if (!anyOpen) document.body.style.overflow = '';
    if (modal === detailsModal && detailVideoPlayer) {
      detailVideoPlayer.pause();
      detailVideoPlayer.currentTime = 0;
    }
  }

  function setFieldError(fieldId, message) {
    const el = document.getElementById(fieldId);
    if (el) el.textContent = message;
  }

  function clearFieldErrors() {
    document.querySelectorAll('.field-error').forEach((el) => {
      el.textContent = '';
    });
  }

  function showToast(message, type = 'success') {
    if (toastTimer) clearTimeout(toastTimer);
    toast.textContent = message;
    toast.className = `toast toast--${type}`;
    toast.hidden = false;
    toastTimer = setTimeout(() => {
      toast.hidden = true;
    }, 3500);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Launch
  init();
});

  // Mode toggle: Flip Book vs Embedded PDF View
  const bookFlipViewBtn = document.getElementById('bookFlipViewBtn');
  const bookPdfViewBtn = document.getElementById('bookPdfViewBtn');
  const openBookEl = document.getElementById('openBook');
  const bookPdfContainer = document.getElementById('bookPdfContainer');
  const bookPdfIframe = document.getElementById('bookPdfIframe');
  const bookDirectPdfLink = document.getElementById('bookDirectPdfLink');
  const pdfExternalLinkBtn = document.getElementById('pdfExternalLinkBtn');
  const pdfDownloadBtn = document.getElementById('pdfDownloadBtn');
  const pdfViewerTitle = document.getElementById('pdfViewerTitle');
  const flipbookBottombar = document.getElementById('flipbookBottombar');

  const moduleVideosModal = document.getElementById('moduleVideosModal');
  const modVideosModalBadge = document.getElementById('modVideosModalBadge');
  const modVideosModalTitle = document.getElementById('modVideosModalTitle');
  const moduleVideosModalBody = document.getElementById('moduleVideosModalBody');

  function setBookViewMode(mode) {
    if (mode === 'pdf') {
      if (openBookEl) openBookEl.hidden = true;
      if (bookPdfContainer) bookPdfContainer.hidden = false;
      if (bookFlipViewBtn) bookFlipViewBtn.classList.remove('active');
      if (bookPdfViewBtn) bookPdfViewBtn.classList.add('active');
      if (flipbookBottombar) flipbookBottombar.style.opacity = '0.3';
      if (currentBookModule && bookPdfIframe) {
        const pdfUrl = currentBookModule.pdf_url || `/static/docs/Module-${currentBookModule.module_no}-Data-Science-Foundations.pdf`;
        bookPdfIframe.src = pdfUrl;
      }
    } else {
      if (openBookEl) openBookEl.hidden = false;
      if (bookPdfContainer) bookPdfContainer.hidden = true;
      if (bookFlipViewBtn) bookFlipViewBtn.classList.add('active');
      if (bookPdfViewBtn) bookPdfViewBtn.classList.remove('active');
      if (flipbookBottombar) flipbookBottombar.style.opacity = '1';
    }
  }

  if (bookFlipViewBtn) bookFlipViewBtn.addEventListener('click', () => setBookViewMode('book'));
  if (bookPdfViewBtn) bookPdfViewBtn.addEventListener('click', () => setBookViewMode('pdf'));

  function openModuleVideosModal(moduleId) {
    const mod = allModules.find((m) => m.id === moduleId);
    if (!mod) {
      showToast('Module not found', 'error');
      return;
    }

    const videos = Array.isArray(mod.youtube_links) ? mod.youtube_links : [];
    modVideosModalBadge.textContent = `UNIT ${mod.module_no}`;
    modVideosModalTitle.textContent = `${mod.title} • Video Lectures`;

    if (videos.length === 0) {
      moduleVideosModalBody.innerHTML = `<p style="color:var(--muted);font-style:italic;">No video lectures linked for this module.</p>`;
    } else {
      moduleVideosModalBody.innerHTML = videos.map((v) => `
        <div class="video-item-row">
          <div class="video-item-left">
            <div class="video-yt-badge">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
                <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
              </svg>
            </div>
            <div class="video-item-details">
              <h4>${escapeHtml(v.title)}</h4>
              <div class="video-item-meta">${escapeHtml(v.channel || 'YouTube')} &bull; ${escapeHtml(v.duration || '')}</div>
              <p class="video-item-desc">${escapeHtml(v.desc || '')}</p>
            </div>
          </div>
          <div class="video-item-actions">
            <a href="${escapeHtml(v.url)}" target="_blank" rel="noopener noreferrer" class="btn btn--primary btn--sm" style="display:inline-flex;align-items:center;gap:4px;">
              <span>Watch on YouTube</span>
              <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>
              </svg>
            </a>
            <button type="button" class="btn btn--secondary btn--sm play-in-portal-btn" data-yt-id="${escapeHtml(v.id || '')}" data-yt-url="${escapeHtml(v.url || '')}" data-title="${escapeHtml(v.title)}" data-channel="${escapeHtml(v.channel || '')}" data-desc="${escapeHtml(v.desc || '')}">
              Play in Portal
            </button>
          </div>
        </div>
      `).join('');

      moduleVideosModalBody.querySelectorAll('.play-in-portal-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
          openYoutubePlayerModal({
            id: btn.getAttribute('data-yt-id'),
            url: btn.getAttribute('data-yt-url'),
            title: btn.getAttribute('data-title'),
            channel: btn.getAttribute('data-channel'),
            desc: btn.getAttribute('data-desc')
          });
        });
      });
    }

    openModal(moduleVideosModal);
  }
