/**
 * LexVision AI – Global Enterprise Application JS (app.js)
 */

document.addEventListener('DOMContentLoaded', function () {
  initGlobalSearch();
  initAutoDismissAlerts();
  initSidebarToggle();
  initTabsHandler();
});

/* Helper to get CSRF token from cookies */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/* Mobile Sidebar Drawer Toggle */
function initSidebarToggle() {
  const toggleBtn = document.getElementById('sidebarToggleBtn');
  const closeBtn = document.getElementById('sidebarCloseBtn');
  const sidebar = document.getElementById('appSidebar');
  const backdrop = document.getElementById('sidebarBackdrop');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('show');
    if (backdrop) backdrop.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('show');
    if (backdrop) backdrop.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (toggleBtn) toggleBtn.addEventListener('click', openSidebar);
  if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
  if (backdrop) backdrop.addEventListener('click', closeSidebar);
}

/* Global Search Dropdown Autocomplete */
function initGlobalSearch() {
  const searchInput = document.getElementById('globalSearchInput');
  const searchResultsBox = document.getElementById('globalSearchResults');

  if (!searchInput || !searchResultsBox) return;

  let debounceTimer;

  searchInput.addEventListener('input', function () {
    const query = this.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < 2) {
      searchResultsBox.style.display = 'none';
      searchResultsBox.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(() => {
      fetch(`/api/v1/search/?q=${encodeURIComponent(query)}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        }
      })
        .then(response => response.json())
        .then(data => {
          if (data.results && data.results.length > 0) {
            let html = '<div class="list-group list-group-flush shadow-lg border rounded-3 overflow-hidden" style="background:#fff;">';
            data.results.forEach(item => {
              const badgeClass = item.risk_level === 'CRITICAL' || item.risk_level === 'HIGH' ? 'badge-soft-danger' : (item.risk_level === 'MEDIUM' ? 'badge-soft-warning' : 'badge-soft-success');
              html += `
                <a href="/contracts/${item.id}/" class="list-group-item list-group-item-action p-3 d-flex justify-content-between align-items-center text-decoration-none">
                  <div>
                    <div class="fw-bold text-dark mb-1">${escapeHtml(item.title)}</div>
                    <small class="text-muted"><i class="bi bi-clock me-1"></i>${item.created_at} | Status: ${item.status}</small>
                  </div>
                  <span class="badge-custom ${badgeClass}">Risk ${item.risk_score}/100</span>
                </a>
              `;
            });
            html += '</div>';
            searchResultsBox.innerHTML = html;
            searchResultsBox.style.display = 'block';
          } else {
            searchResultsBox.innerHTML = '<div class="p-3 text-center text-muted bg-white border rounded shadow-sm">No matching contracts found</div>';
            searchResultsBox.style.display = 'block';
          }
        })
        .catch(err => console.error('Search error:', err));
    }, 250);
  });

  // Hide search box when clicking outside
  document.addEventListener('click', function (e) {
    if (!searchInput.contains(e.target) && !searchResultsBox.contains(e.target)) {
      searchResultsBox.style.display = 'none';
    }
  });
}

/* Auto Dismiss Flash Messages */
function initAutoDismissAlerts() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
        const bsAlert = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
        if (bsAlert) bsAlert.close();
      }
    }, 5000);
  });
}

/* Custom Workspace Tab Switching Handler */
function initTabsHandler() {
  const tabLinks = document.querySelectorAll('.nav-tab-item');
  if (!tabLinks.length) return;

  tabLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
      const targetTabId = this.getAttribute('data-tab');

      // Deactivate all tab links
      tabLinks.forEach(l => l.classList.remove('active'));
      // Activate clicked
      this.classList.add('active');

      // Hide all tab content panes
      const tabContents = document.querySelectorAll('.tab-content-pane');
      tabContents.forEach(pane => pane.style.display = 'none');

      // Show target tab pane
      const targetPane = document.getElementById(targetTabId);
      if (targetPane) {
        targetPane.style.display = 'block';
      }
    });
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}
