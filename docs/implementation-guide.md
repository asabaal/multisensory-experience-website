# Brand Implementation Guide

This guide provides specific code snippets for implementing the Asabaal Ventures brand elements on the website. Each section includes targeted changes to make to specific files.

## 1. Image Updates

### Replace Logo References

In `index.html` and all other pages with logo references, change:

```html
<img src="/images/logo.svg" alt="Multisensory Experiences Logo" class="header__logo-img">
```

To:
```html
<img src="/images/asabaal-logo.svg" alt="Asabaal Ventures Logo" class="header__logo-img">
```

And in the footer:
```html
<img src="/images/logo-white.svg" alt="Multisensory Experiences Logo" class="footer__logo-img">
```

To:
```html
<img src="/images/asabaal-logo-white.svg" alt="Asabaal Ventures Logo" class="footer__logo-img">
```

### Hero Background

In `css/pages/home.css`, find:

```css
.hero__bg {
  background-image: url('/images/hero-bg.jpg');
  /* other properties */
}
```

Change to:
```css
.hero__bg {
  background-image: url('/images/cosmic-bg.jpg'); /* Your nebula background */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
```

## 2. Content & Text Updates

### Update Tagline

In `index.html` (and other relevant files), find:

```html
<div class="footer__tagline">Reimagining Possible in a Post-Labor Economy</div>
```

Change to:
```html
<div class="footer__tagline text-accent">Monetizing Fulfillment, Peace, & Truth</div>
```

Also update the main headline in the hero section:

```html
<h1 class="hero__title text-gradient">Reimagining Possible in a Post-Labor Economy</h1>
```

Change to:
```html
<h1 class="hero__title text-gradient">Monetizing Fulfillment, Peace, & Truth</h1>
<p class="hero__subtitle text-cosmic">Reimagining Possible in a Post-Labor Economy</p>
```

### Update RESPECT Content

Add this to the "Our Evolving Approach" page (`approach.html`):

```html
<section class="section respect-section">
  <div class="container">
    <div class="respect-container">
      <h2 class="respect-title text-futuristic">RESPECT</h2>
      <p class="respect-subtitle">THE FUNDAMENTAL HUMAN RIGHT</p>
      <div class="respect-content">
        <p>At the core of our philosophy is the profound recognition that respect is not merely a courtesy, but a fundamental human right essential to personal growth and societal betterment.</p>
        <p>Through our multisensory experiences, we aim to cultivate deeper levels of respect—for ourselves, for others, and for the collective journey we share in this post-labor economy.</p>
      </div>
    </div>
  </div>
</section>
```

## 3. Typography Implementation

### Update HTML Header in All Pages

In the `<head>` section of each HTML file, ensure the favicon is updated:

```html
<!-- Favicon -->
<link rel="icon" href="/images/favicon.ico">
<link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
```

### Add Spiritual Concepts

Throughout content, highlight spiritual concepts using:

```html
<span class="spiritual-concept">Collective Resonance</span>
```

### Create Meaningful Quotes

For spiritual quotations or philosophical statements:

```html
<blockquote class="quote">
  The highest form of knowledge is empathy, for it requires us to suspend our egos and live in another's world.
  <cite class="quote-source">- Plato</cite>
</blockquote>
```

## 4. CSS Class Implementation

### Cosmic Elements

For elements that should have the cosmic/nebula aesthetic:

```html
<div class="feature-card cosmic-overlay">
  <!-- card content -->
</div>
```

### Text Styling

Apply the various text styling classes as needed:

- `text-gradient` - For gradient text effects
- `text-futuristic` - For futuristic, glowing text
- `text-cosmic` - For purple space-themed text
- `text-gold` - For gold-colored accent text
- `text-accent` - For Cinzel font spiritual elements
- `text-creative` - For Playfair Display creative elements
- `lead` - For larger introductory paragraphs
- `spiritual-concept` - For highlighted concepts

## 5. Testing Implementation

After making these changes:

1. Check all pages in different browsers
2. Verify responsive behavior on mobile devices
3. Ensure contrast is sufficient for accessibility
4. Test all interactive elements with the new styling
5. Check font loading performance

## Helpful Git Commands

```bash
# Pull the latest changes from the brand-integration branch
git checkout brand-integration
git pull

# After making changes, commit and push
git add .
git commit -m "Implement brand typography and styling"
git push origin brand-integration

# When ready to merge to main
git checkout main
git merge brand-integration
git push origin main
```

Remember that this is just a starting point. You'll likely want to make additional refinements as you implement the brand and see how it looks in practice.
