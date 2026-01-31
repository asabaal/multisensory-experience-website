const AmusementsNavigation = {
  data: amusementsData,

  init() {
    this.renderHubCards();
    this.setupEventListeners();
  },

  renderHubCards() {
    const showsGrid = document.getElementById('shows-grid');
    
    if (!showsGrid) return;

    showsGrid.innerHTML = this.data.shows.map(show => {
      return `
      <div class="show-card" data-show-id="${show.id}" onclick="window.location.href='${show.link}'">
        <div class="show-image" style="background: ${show.gradient || show.colorTheme}">
          ${show.logo ? `<img src="${show.logo}" alt="${show.title} Logo">` : ''}
          <div class="show-overlay">
            <span class="show-status ${show.status}">${show.status === 'active' ? 'Now Streaming' : 'Coming Soon'}</span>
          </div>
        </div>
        <div class="show-content">
          <h2 class="show-title">${show.title}</h2>
          <p class="show-subtitle" style="color: ${show.colorTheme}">${show.subtitle}</p>
          <p class="show-description">${show.description}</p>
          ${show.episodeCount ? `<div class="show-stats">
            <span class="episode-count">${show.episodeCount} episodes</span>
          </div>` : ''}
          <div class="show-explore">
            <span class="explore-text">Explore</span>
            <span class="explore-arrow">→</span>
          </div>
        </div>
      </div>
      </div>
    `;
    }).join('');
    
    showsGrid.innerHTML = cardsHTML;
  },

  setupEventListeners() {
  }
};

document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM Content Loaded');
  console.log('AmusementsNavigation object:', typeof AmusementsNavigation);
  console.log('AmusementsNavigation.init:', typeof AmusementsNavigation.init);
  AmusementsNavigation.init();
});

function togglePlay() {
  const playButton = document.querySelector('.play-button');
  if (playButton) {
    if (playButton.textContent === '▶') {
      playButton.textContent = '❚❚';
    } else {
      playButton.textContent = '▶';
    }
  }
}

function togglePoem() {
  const poemContainer = document.querySelector('.poem-text');
  const toggleButton = document.querySelector('.poem-toggle');

  if (poemContainer && toggleButton) {
    poemContainer.classList.toggle('collapsed');
    toggleButton.textContent = poemContainer.classList.contains('collapsed')
      ? '▼ Show Poem'
      : '▲ Hide Poem';
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = AmusementsNavigation;
}
