# Color Scheme Implementation Guide

This guide provides specific instructions for implementing the Asabaal Ventures color scheme throughout the website.

## Color Palette Reference

```css
/* Primary Colors */
--color-primary: #e27a9e; /* Pink/Magenta from Asabaal logo */
--color-secondary: #008f8c; /* Deep Teal from RESPECT background */
--color-tertiary: #6e3a80; /* Cosmic Purple from nebula background */

/* Secondary Colors */
--color-accent-1: #30d5f2; /* Electric Blue from holographic text */
--color-accent-2: #ff7d33; /* Sunset Orange from backgrounds */
--color-accent-3: #d9b642; /* Gold Accent from spiritual text */

/* Neutral Colors */
--color-dark: #0a0f1c; /* Deep Space Black for backgrounds */
--color-light: #f2e6c2; /* Parchment for light elements */

/* Gradients */
--gradient-primary: linear-gradient(90deg, var(--color-primary), var(--color-tertiary));
--gradient-accent: linear-gradient(90deg, var(--color-accent-1), var(--color-accent-2));
--gradient-cosmic: linear-gradient(135deg, var(--color-dark), var(--color-tertiary) 70%, var(--color-primary));
--gradient-futuristic: linear-gradient(90deg, var(--color-accent-1), var(--color-primary), var(--color-accent-1));
```

## 1. Background Colors

### Main Background

In `css/main.css`, add:

```css
body {
  background-color: var(--color-dark);
  color: var(--color-text);
}
```

### Hero Section Background

In `css/pages/home.css`, update:

```css
.hero__bg {
  background-image: url('/images/cosmic-bg.jpg');
  background-size: cover;
  background-position: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: var(--z-background);
}

.hero::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--gradient-cosmic);
  opacity: 0.6;
  z-index: var(--z-background);
}
```

### Section Backgrounds

Add these alternating section styles in `css/main.css`:

```css
.section--dark {
  background-color: var(--color-dark);
  color: var(--color-text);
}

.section--cosmic {
  background: var(--gradient-cosmic);
  color: var(--color-text);
  position: relative;
  overflow: hidden;
}

.section--light {
  background-color: rgba(10, 15, 28, 0.8);
  color: var(--color-text);
}

.section--accent {
  background: linear-gradient(135deg, var(--color-secondary), var(--color-tertiary));
  color: var(--color-text);
}
```

## 2. Text Colors

### Headings

In `css/typography.css`, update:

```css
h1, .h1 {
  color: var(--color-primary);
  /* existing styles */
}

h2, .h2 {
  color: var(--color-accent-1);
  /* existing styles */
}

h3, .h3 {
  color: var(--color-light);
  /* existing styles */
}

h4, .h4 {
  color: var(--color-accent-3);
  /* existing styles */
}
```

### Special Text

Add to `css/typography.css`:

```css
.spiritual-concept {
  color: var(--color-accent-3);
  text-shadow: 0 0 5px rgba(217, 182, 66, 0.3);
  /* existing styles */
}

.quote {
  color: var(--color-light);
  /* existing styles */
}

.quote::before {
  color: var(--color-primary);
  /* existing styles */
}
```

## 3. UI Elements

### Buttons

In `css/components/buttons.css`, update:

```css
.btn {
  background-color: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  /* other existing styles */
  transition: all var(--transition-normal);
}

.btn:hover {
  background-color: var(--color-primary);
  color: var(--color-dark);
}

.btn--primary {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-dark);
}

.btn--primary:hover {
  background-color: transparent;
  color: var(--color-primary);
}

.btn--secondary {
  background-color: var(--color-secondary);
  border-color: var(--color-secondary);
  color: var(--color-dark);
}

.btn--secondary:hover {
  background-color: transparent;
  color: var(--color-secondary);
}

.btn--accent {
  background-color: var(--color-accent-1);
  border-color: var(--color-accent-1);
  color: var(--color-dark);
}

.btn--accent:hover {
  background-color: transparent;
  color: var(--color-accent-1);
}

.btn--gradient {
  background: var(--gradient-primary);
  border: none;
  color: var(--color-text);
  position: relative;
  z-index: 1;
}

.btn--gradient::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--gradient-accent);
  opacity: 0;
  transition: opacity var(--transition-normal);
  z-index: -1;
  border-radius: inherit;
}

.btn--gradient:hover::before {
  opacity: 1;
}

.btn--outline {
  background-color: transparent;
  border: 2px solid var(--color-text);
  color: var(--color-text);
}

.btn--outline:hover {
  background-color: var(--color-text);
  color: var(--color-dark);
}
```

### Header and Navigation

In `css/components/header.css`, update:

```css
.header {
  background-color: rgba(10, 15, 28, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(226, 122, 158, 0.2);
  /* existing styles */
}

.header--scrolled {
  background-color: rgba(10, 15, 28, 0.95);
  box-shadow: 0 4px 30px rgba(110, 58, 128, 0.3);
  /* existing styles */
}

.nav__link {
  color: var(--color-text);
  /* existing styles */
}

.nav__link:hover {
  color: var(--color-primary);
}

.nav__link--active {
  color: var(--color-primary);
  /* existing styles */
}

.nav-toggle__line {
  background-color: var(--color-text);
  /* existing styles */
}
```

### Footer

In `css/components/footer.css`, update:

```css
.footer {
  background-color: rgba(10, 15, 28, 0.95);
  border-top: 1px solid rgba(226, 122, 158, 0.2);
  /* existing styles */
}

.footer__logo-img {
  filter: drop-shadow(0 0 8px rgba(226, 122, 158, 0.5));
}

.footer__tagline {
  color: var(--color-accent-3);
  /* existing styles */
}

.footer__links-title {
  color: var(--color-accent-1);
  /* existing styles */
}

.footer__link {
  color: var(--color-text-muted);
  transition: color var(--transition-normal);
  /* existing styles */
}

.footer__link:hover {
  color: var(--color-primary);
}

.footer__social-link {
  color: var(--color-text);
  /* existing styles */
}

.footer__social-link:hover {
  color: var(--color-primary);
  /* existing styles */
}

.footer__bottom {
  border-top: 1px solid rgba(226, 122, 158, 0.1);
  /* existing styles */
}
```

## 4. Cards and Content Elements

Update card styles in `css/components/cards.css`:

```css
.feature-card {
  background-color: rgba(10, 15, 28, 0.6);
  border: 1px solid rgba(226, 122, 158, 0.2);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  transition: all var(--transition-normal);
  /* existing styles */
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(110, 58, 128, 0.3);
  border-color: rgba(226, 122, 158, 0.4);
}

.feature-card__icon {
  color: var(--color-primary);
  /* existing styles */
}

.feature-card__title {
  color: var(--color-accent-1);
  /* existing styles */
}

.blog-card {
  background-color: rgba(10, 15, 28, 0.7);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  transition: all var(--transition-normal);
  /* existing styles */
}

.blog-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(110, 58, 128, 0.3);
}

.blog-card__category {
  color: var(--color-accent-3);
  /* existing styles */
}

.blog-card__title {
  color: var(--color-accent-1);
  /* existing styles */
}

.card__link {
  color: var(--color-primary);
  /* existing styles */
}

.card__link:hover {
  color: var(--color-accent-1);
  /* existing styles */
}
```

## 5. Forms and Input Elements

In `css/components/forms.css`, update:

```css
input, textarea, select {
  background-color: rgba(10, 15, 28, 0.6);
  border: 1px solid rgba(226, 122, 158, 0.3);
  color: var(--color-text);
  /* existing styles */
}

input:focus, textarea:focus, select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(226, 122, 158, 0.2);
  /* existing styles */
}

.form__label {
  color: var(--color-text-muted);
  /* existing styles */
}

.form__message--error {
  color: var(--color-accent-2);
  /* existing styles */
}

.form__message--success {
  color: var(--color-secondary);
  /* existing styles */
}

.newsletter-form__input {
  background-color: rgba(10, 15, 28, 0.4);
  border: 1px solid rgba(226, 122, 158, 0.2);
  /* existing styles */
}

.newsletter-form__button {
  background-color: var(--color-primary);
  color: var(--color-dark);
  /* existing styles */
}

.newsletter-form__button:hover {
  background-color: var(--color-accent-1);
  /* existing styles */
}
```

## Testing Your Changes

After implementing these color changes:

1. Check text contrast against backgrounds to ensure readability
2. Verify that interactive elements (buttons, links) provide clear visual feedback
3. Test all pages in both light and dark system themes
4. Check how the colors appear on different devices and screen sizes

Remember that colors may appear slightly different across devices, so aim for a balanced approach that works well across various screens.

## Alternative Dark/Light Mode

If you'd like to implement a dark/light mode toggle in the future, we can add a CSS class to the body and use it to define alternative color schemes:

```css
body.light-mode {
  --color-dark: #f2f2f2;
  --color-light: #121212;
  --color-text: #18181b;
  --color-text-muted: rgba(24, 24, 27, 0.7);
  --gradient-cosmic: linear-gradient(135deg, var(--color-light), var(--color-tertiary) 70%, var(--color-primary));
  /* other variable overrides */
}
```

But for now, the focus is on implementing the cosmic/nebula dark theme as the primary aesthetic.
