const toggle = document.getElementById('toggleSubscribes');
const mobileToggle = document.getElementById('subscribesCheckboxMobile');
const newsContainer = document.getElementById('cardsContainer');
const newsFilter = document.getElementById('newsFilter');
const allLabel = document.querySelector('.all-label');
const verifiedLabel = document.querySelector('.verified-label');


function syncToggles(state) {
  if (toggle) toggle.checked = state;
  if (mobileToggle) mobileToggle.checked = state;
}

function updateLabelHighlight() {
  if (toggle.checked) {
    verifiedLabel?.classList.add('active');
    allLabel?.classList.remove('active');
  } else {
    allLabel?.classList.add('active');
    verifiedLabel?.classList.remove('active');
  }
}

function toggleFilterVisibility() {
  const noNews = newsContainer.querySelector('.not-found-message') !== null;
  if (noNews && !toggle.checked) {
    newsFilter.classList.remove('d-lg-flex');
  } else {
    newsFilter.classList.add('d-lg-flex');
  }
}

async function loadNews(subscribesOnly) {
  const params = new URLSearchParams();
  if (subscribesOnly) params.set('subscribes', '1');
  const url = `/api/get_news_cards?${params.toString()}`;
  try {
    const response = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    if (!response.ok) throw new Error('Request error');

    const html = await response.text();
    newsContainer.innerHTML = html;
    toggleFilterVisibility();
  } catch (err) {
    console.error('Failed to load news:', err);
    if (newsFilter) {
      newsFilter.style.display = 'none';
    }
  }
}

function handleToggleChange(sourceToggle) {
  const isChecked = sourceToggle.checked;
  syncToggles(isChecked);
  updateLabelHighlight();
  loadNews(sourceToggle.checked);
}

if (toggle) {
  toggle.addEventListener('change', function() {
    handleToggleChange(toggle);
  });
}

if (mobileToggle) {
  mobileToggle.addEventListener('change', function() {
    handleToggleChange(mobileToggle);
  });
}

loadNews(mobileToggle.checked || toggle.checked)
