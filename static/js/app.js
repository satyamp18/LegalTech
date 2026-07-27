/**
 * LexVision AI – Global Application JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  initGlobalSearch();
  initAutoDismissAlerts();
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
            let html = '<div class="list-group list-group-flush shadow-lg border rounded-3 overflow-hidden">';
            data.results.forEach(item => {
              const badgeClass = item.risk_level === 'CRITICAL' || item.risk_level === 'HIGH' ? 'bg-danger' : (item.risk_level === 'MEDIUM' ? 'bg-warning text-dark' : 'bg-success');
              html += `
                <a href="/contracts/${item.id}/" class="list-group-item list-group-item-action p-3 d-flex justify-content-between align-items-center">
                  <div>
                    <div class="fw-bold text-dark mb-1">${escapeHtml(item.title)}</div>
                    <small class="text-muted"><i class="bi bi-clock me-1"></i>${item.created_at} | Status: ${item.status}</small>
                  </div>
                  <span class="badge ${badgeClass} rounded-pill">Risk ${item.risk_score}/100</span>
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

function initAutoDismissAlerts() {
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}
