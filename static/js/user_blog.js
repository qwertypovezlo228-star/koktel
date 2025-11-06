
const newsContainer = document.getElementById('cardsContainer');

async function loadNews(user_id) {
  const params = new URLSearchParams();
  params.set('user_id', user_id);
  const url = `/api/get_news_cards?${params.toString()}`;
  try {
    const response = await fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    if (!response.ok) throw new Error('Request error');

    const html = await response.text();
    newsContainer.innerHTML = html;
  } catch (err) {
    console.error('Failed to load news:', err);
    news.style.display = 'none';
  }
}

loadNews(user_id)
