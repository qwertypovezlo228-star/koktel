
document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('toggleVerified');
  const mobileToggle = document.getElementById('verifiedCheckboxMobile');
  const modelsContainer = document.getElementById('modelsContainer');
  const verificationFilter = document.getElementById('verificationFilter');
  const allLabel = document.querySelector('.all-label');
  const verifiedLabel = document.querySelector('.verified-label');
  const citiesContainer = document.getElementById('citiesContainer');
  const citySelectContainer = document.getElementById('citySelectContainer');

  const enableCities = window.location.pathname.includes('/category/2');

  let selectedCity = '';
  let currentPage = 1;

  if (!toggle || !modelsContainer || !verificationFilter) return;

  function toggleFilterVisibility() {
    const noModels = modelsContainer.querySelector('.not-found-message') !== null;
    if (noModels && !toggle.checked) {
      verificationFilter.classList.remove('d-lg-flex');
    } else {
      verificationFilter.classList.add('d-lg-flex');
    }
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

  async function loadModels(verifiedOnly, city = '', page = 1) {
    const params = new URLSearchParams();
    if (verifiedOnly) params.set('verified', '1');
    if (city) params.set('city', city);
    if (page > 1) params.set('page', page);

    const url = `${api_url}${params.toString()}`;

    try {
      const response = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (!response.ok) throw new Error('Request error');

      const html = await response.text();
      modelsContainer.innerHTML = html;
      currentPage = page;

      toggleFilterVisibility();
      
      // Scroll to top of models container
      modelsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } catch (err) {
      console.error('Failed to load models:', err);
      verificationFilter.style.display = 'none';
    }
  }
  
  // Global function for pagination buttons
  window.loadPage = function(page) {
    loadModels(toggle.checked, selectedCity, page);
  }

  async function loadCities(verifiedOnly) {
    if (!enableCities) return;

    const params = new URLSearchParams();
    if (verifiedOnly) params.set('verified', '1');

    const url = `/api/models_cities_button?${params.toString()}`;

    try {
      const response = await fetch(url, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (!response.ok) throw new Error('City fetch failed');

      const html = await response.text();
      citiesContainer.innerHTML = html;

      const cityButtons = citiesContainer.querySelectorAll('.city-button');

      if (cityButtons.length <= 1) {
        citiesContainer.classList.remove('d-lg-flex');
        citiesContainer.style.display = 'none';
      } else {
        citiesContainer.classList.add('d-lg-flex');
        citiesContainer.style.display = '';
      }

      highlightActiveCity();
      attachCityButtonListeners();
    } catch (err) {
      console.error('Failed to load cities:', err);
    }
  }

  async function loadCitySelectForMobile(verifiedOnly) {
    if (!enableCities || !citySelectContainer) return;

    const params = new URLSearchParams();
    if (verifiedOnly) params.set('verified', '1');
    params.set('dropdown', '1');

    try {
      const response = await fetch(`/api/models_cities_button?${params.toString()}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (!response.ok) throw new Error('City select fetch failed');

      const html = await response.text();
      citySelectContainer.innerHTML = html;

      const select = citySelectContainer.querySelector('#citySelect');
      if (select) {
        select.addEventListener('change', function() {
          selectedCity = this.value || '';
          currentPage = 1;
          loadModels(toggle.checked, selectedCity, 1);
          loadCities(toggle.checked);
        });
      }
    } catch (err) {
      console.error('Failed to load mobile city select:', err);
    }
  }

  function highlightActiveCity() {
    const cityButtons = document.querySelectorAll('.city-button');
    cityButtons.forEach(btn => {
      const city = btn.getAttribute('data-city') || '';
      if (city.toLowerCase() === (selectedCity || '').toLowerCase()) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  function attachCityButtonListeners() {
    const cityButtons = document.querySelectorAll('.city-button');
    cityButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        selectedCity = this.getAttribute('data-city') || '';
        currentPage = 1;

        loadModels(toggle.checked, selectedCity, 1);
        loadCities(toggle.checked);

        cityButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }

  function syncToggles(state) {
    if (toggle) toggle.checked = state;
    if (mobileToggle) mobileToggle.checked = state;
  }

  function handleToggleChange(sourceToggle) {
    const isChecked = sourceToggle.checked;
    syncToggles(isChecked);
    updateLabelHighlight();
    currentPage = 1;
    loadModels(isChecked, selectedCity, 1);
    if (enableCities) {
      loadCities(isChecked);
      loadCitySelectForMobile(isChecked);
    }
  }

  if (mobileToggle) {
    mobileToggle.checked = toggle?.checked || false;
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

  updateLabelHighlight();
  loadModels(toggle.checked, selectedCity);

  if (enableCities) {
    loadCities(toggle.checked);
    loadCitySelectForMobile(toggle.checked);
  }
});

