const amusementsData = {
  shows: [
    {
      id: 'demos',
      title: "Demos/Previews",
      subtitle: "Blog 2.0 Era",
      description: "Explore the journey of purpose-driven creation, unity consciousness, and the evolution of collaborative innovation. Each post is a piece of the larger vision coming to life.",
      link: "blog-listing.html",
      image: "assets/shows/amusements/banners/demos-preview.jpg",
      episodeCount: 26,
      status: "active",
      colorTheme: "#8b5cf6",
      gradient: "linear-gradient(45deg, #8b5cf6, #06b6d4)"
    },
    {
      id: 'vision-2054',
      title: "Vision 2054",
      subtitle: "The Great Reconciliation",
      description: "A blueprint for humanity's collective awakening to unity consciousness. Where division becomes connection, where separation becomes remembrance of our interconnectedness.",
      link: "vision_2054_page.html",
      image: "assets/shows/amusements/banners/vision-2054.jpg",
      status: "active",
      colorTheme: "#f59e0b",
      gradient: "linear-gradient(45deg, #f59e0b, #fbbf24)"
    },
    {
      id: 'life-is-your-word',
      title: "Life is your Word",
      subtitle: "A Reality Series",
      description: "Experience the journey of transformation, authenticity, and awakening through intimate conversations and real-life moments. Life is your Word explores what it means to truly live in alignment with your authentic self.",
      link: "life-is-your-word.html",
      logo: "assets/shows/life-is-your-word/logos/logo.png",
      banner: "assets/shows/life-is-your-word/banners/banner.jpg",
      status: "active",
      colorTheme: "#fbbf24",
      gradient: "linear-gradient(45deg, #fbbf24, #f472b6)",
      seasons: {
        season0: {
          title: "Season 0: Pilot",
          description: "The pilot concept exploring authenticity and transformation through 15 intimate episodes.",
          episodeCount: 15,
          status: "complete",
          releaseDate: "2024",
          episodes: [
            { number: 1, title: "The Beginning", description: "Where it all started - exploring the origins of authenticity", duration: "15 min" },
            { number: 2, title: "First Steps", description: "Taking the first brave steps toward living authentically", duration: "18 min" },
            { number: 3, title: "Breaking Through", description: "Breaking through barriers to find your true voice", duration: "20 min" },
            { number: 4, title: "Finding Courage", description: "Finding courage in the face of uncertainty", duration: "22 min" },
            { number: 5, title: "The Shift", description: "The pivotal moment when everything changes", duration: "19 min" },
            { number: 6, title: "Embracing Change", description: "Learning to embrace and welcome transformation", duration: "21 min" },
            { number: 7, title: "Authentic Connections", description: "Building genuine connections from authenticity", duration: "17 min" },
            { number: 8, title: "The Journey Within", description: "Deep exploration of inner transformation", duration: "24 min" },
            { number: 9, title: "Speaking Truth", description: "The power of speaking your truth", duration: "18 min" },
            { number: 10, title: "Finding Purpose", description: "Discovering your true purpose and calling", duration: "23 min" },
            { number: 11, title: "Living Aligned", description: "Making decisions aligned with authentic self", duration: "19 min" },
            { number: 12, title: "Breaking Patterns", description: "Identifying and breaking limiting patterns", duration: "21 min" },
            { number: 13, title: "The Awakening", description: "Profound moments of awakening and realization", duration: "20 min" },
            { number: 14, title: "Integration", description: "Integrating transformation into daily life", duration: "22 min" },
            { number: 15, title: "New Beginnings", description: "Celebrating transformation and embracing new chapters", duration: "25 min" }
          ]
        },
        season1: {
          title: "Season 1",
          description: "The inaugural season launching in 2025. More intimate conversations, deeper transformations, and authentic moments of awakening.",
          episodeCount: 0,
          status: "coming-soon",
          releaseDate: "Q2 2025",
          teaser: "Get ready for Season 1 - coming in early 2025 with even more powerful stories of transformation and authenticity."
        }
      }
    },
    {
      id: 'musical-poetry',
      title: "Musical Poetry with Asabaal",
      subtitle: "Poetic Awakening",
      description: "Experience the fusion of spoken word, music, and visual poetry in this transformative audio-visual journey. Each episode weaves together poetry, melody, and imagery to create a multisensory meditation experience.",
      link: "musical-poetry.html",
      logo: "assets/shows/musical-poetry/logos/logo.png",
      banner: "assets/shows/musical-poetry/banners/banner.jpg",
      status: "active",
      colorTheme: "#06b6d4",
      gradient: "linear-gradient(45deg, #06b6d4, #10b981)",
      seasons: {
        season1: {
          title: "Season 1",
          description: "The inaugural season of musical poetry experiences - a journey through consciousness, emotion, and spiritual awakening.",
          episodeCount: 1,
          status: "active",
          releaseDate: "2025",
          episodes: [
            {
              number: 1,
              title: "First Light",
              description: "The first poem in the series - exploring the dawn of consciousness and the awakening of awareness.",
              duration: "8 min",
              poemLines: [
                "In the darkness before dawn,",
                "A spark begins to form,",
                "The first light of awareness,",
                "Transforming into warmth.",
                "",
                "Each breath a revelation,",
                "Each moment a discovery,",
                "The universe awakens within,",
                "And we remember our truth."
              ]
            }
          ]
        }
      }
    }
  ]
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = amusementsData;
}
