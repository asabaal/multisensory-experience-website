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
          ${show.image ? `<img src="${show.image}" alt="${show.title} Card">` : ''}
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
    `;
    }).join('');
  },

  renderShowOverview(showId) {
    const show = this.data.shows.find(s => s.id === showId);
    if (!show) {
      console.error('Show not found:', showId);
      return;
    }

    document.title = `${show.title} | Asabaal's Amusements`;
    this.renderShowHeader(show);
    this.renderSeasons(show);
  },

  renderShowHeader(show) {
    const showHeader = document.querySelector('.show-header');
    if (!showHeader) return;

    showHeader.innerHTML = `
      <div class="show-banner" style="background: ${show.gradient || show.colorTheme}">
        <div style="font-size: 6rem; color: white; text-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);">${show.id === 'life-is-your-word' ? '🎬' : show.id === 'musical-poetry' ? '🎵' : show.id === 'vision-2054' ? '🌟' : '🎭'}</div>
      </div>
      <div class="show-info">
        <h1 class="show-title-large">${show.title}</h1>
        <p class="show-subtitle-large" style="color: ${show.colorTheme}">${show.subtitle}</p>
        <p class="show-description-large">${show.description}</p>
      </div>
    `;
  },

  renderSeasons(show) {
    const seasonsContainer = document.querySelector('.seasons-grid');
    if (!seasonsContainer || !show.seasons) return;

    const seasonEntries = Object.entries(show.seasons);
    seasonsContainer.innerHTML = seasonEntries.map(([seasonId, season]) => {
      const statusClass = season.status;
      const statusText = season.status === 'complete' ? 'Complete' : season.status === 'active' ? 'Now Streaming' : 'Coming Soon';
      const statusGradient = season.status === 'complete' ? 'linear-gradient(45deg, #10b981, #059669)' : season.status === 'active' ? 'linear-gradient(45deg, #10b981, #059669)' : 'linear-gradient(45deg, #f59e0b, #d97706)';
      const seasonEmoji = season.status === 'complete' ? '✓' : season.status === 'active' ? '▶' : '📅';
      
      return `
        <div class="season-card" onclick="window.location.href='${show.id}/${seasonId}.html'">
          <div class="season-image" style="background: ${statusGradient || show.gradient || show.colorTheme}">
            <div class="season-emoji">${seasonEmoji}</div>
            <div class="season-overlay">
              <span class="season-badge ${statusClass}">${statusText}</span>
            </div>
          </div>
          <div class="season-content">
            <h3 class="season-title">${season.title}</h3>
            <p class="season-description">${season.description}</p>
            ${season.episodeCount > 0 ? `<p class="season-stats">${season.episodeCount} episodes</p>` : ''}
            ${season.status === 'coming-soon' ? `<p class="season-release" style="color: ${show.colorTheme}">Launching ${season.releaseDate}</p>` : ''}
            ${season.teaser ? `<p class="season-teaser">${season.teaser}</p>` : ''}
          </div>
          <div class="season-explore">
            <span class="explore-text">${season.status === 'coming-soon' ? 'Get Notified' : 'Explore Now'}</span>
            <span class="explore-arrow">→</span>
          </div>
        </div>
      `;
    }).join('');
  },

  renderSeason(showId, seasonId) {
    const show = this.data.shows.find(s => s.id === showId);
    if (!show || !show.seasons) return;

    const season = show.seasons[seasonId];
    if (!season || !season.episodes || season.episodes.length === 0) return;

    document.title = `${season.title} | ${show.title} | Asabaal's Amusements`;
    this.renderSeasonHeader(show, season);
    this.renderEpisodes(show, season);
  },

  renderSeasonHeader(show, season) {
    const seasonHeader = document.querySelector('.season-header');
    if (!seasonHeader) return;

    seasonHeader.innerHTML = `
      <div class="season-banner" style="background: ${show.gradient || show.colorTheme}">
        <div class="season-banner-content">
          <h1 class="season-title-large">${season.title}</h1>
          <p class="season-subtitle">${show.title}</p>
        </div>
      </div>
      <div class="season-info">
        <p class="season-description-large">${season.description}</p>
      </div>
    `;
  },

  renderEpisodes(show, season) {
    const episodesContainer = document.querySelector('.episodes-grid');
    if (!episodesContainer) return;

    episodesContainer.innerHTML = season.episodes.map((episode, index) => {
      const prevEpisode = index > 0 ? season.episodes[index - 1] : null;
      const nextEpisode = index < season.episodes.length - 1 ? season.episodes[index + 1] : null;

      return `
        <div class="episode-card" onclick="window.location.href='${show.id}/${season.id}/episode-${episode.number}.html'">
          <div class="episode-thumbnail" style="background: ${show.gradient || show.colorTheme}">
            <div class="episode-number">${episode.number}</div>
          </div>
          <div class="episode-content">
            <h3 class="episode-title">${episode.title}</h3>
            <p class="episode-description">${episode.description}</p>
            <div class="episode-meta">
              <span class="episode-duration" style="color: ${show.colorTheme}">${episode.duration}</span>
              <span class="episode-explore">Watch →</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    this.setupEpisodeNavigation(prevEpisode, nextEpisode, show, season);
  },

  setupEpisodeNavigation(prevEpisode, nextEpisode, show, season) {
    const prevButton = document.querySelector('.episode-nav-prev');
    const nextButton = document.querySelector('.episode-nav-next');

    if (prevButton) {
      if (prevEpisode) {
        prevButton.href = `${show.id}/${season.id}/episode-${prevEpisode.number}.html`;
        prevButton.innerHTML = `← Previous: ${prevEpisode.title}`;
        prevButton.style.display = 'inline-block';
      } else {
        prevButton.style.display = 'none';
      }
    }

    if (nextButton) {
      if (nextEpisode) {
        nextButton.href = `${show.id}/${season.id}/episode-${nextEpisode.number}.html`;
        nextButton.innerHTML = `Next: ${nextEpisode.title} →`;
        nextButton.style.display = 'inline-block';
      } else {
        nextButton.style.style.display = 'none';
      }
    }
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
