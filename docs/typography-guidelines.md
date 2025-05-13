# Asabaal Ventures Brand Guidelines

## Typography System

Our typography system is designed to convey both futuristic innovation and spiritual depth, reflecting our mission of "Monetizing Fulfillment, Peace, & Truth" in a post-labor economy.

### Font Families

We use a carefully selected combination of four complementary fonts:

#### 1. Primary Font: Inter
- **Usage**: Body text, paragraphs, general content, UI elements
- **Characteristics**: Clean, modern, highly readable
- **Weights Used**: 
  - Regular (400) for body text
  - Medium (500) for emphasis within paragraphs
  - Semi-bold (600) for subheadings and UI elements

![Inter Font Sample](https://assets.website-files.com/5f0801907ed7736e5de8cb15/5f27901a3c75e389b3d8b947_Inter.jpg)

#### 2. Display Font: Space Grotesk
- **Usage**: Headlines, page titles, large feature text
- **Characteristics**: Futuristic, distinctive, modern
- **Weights Used**:
  - Medium (500) for section headings
  - Bold (700) for main page headings
  - Light (300) for large display numbers

![Space Grotesk Font Sample](https://assets.website-files.com/611153e7af981472d8da199c/61b903ca405fde9f1b6e5ccf_space-grotesk-font.jpg)

#### 3. Accent Font: Cinzel
- **Usage**: Spiritual concepts, philosophical terms, important quotes
- **Characteristics**: Elegant, timeless, refined
- **Weights Used**:
  - Regular (400) for quotes and featured text
  - Medium (500) for highlighted spiritual concepts
  - Bold (700) for emphasis within spiritual content

![Cinzel Font Sample](https://cdn.myfonts.net/cdn-cgi/image/width=720%2Cheight=360%2Cfit=contain%2Cformat=auto/images/pim/10000/317536_0.png)

#### 4. Creative Font: Playfair Display
- **Usage**: Artistic elements, pull quotes, special sections
- **Characteristics**: Sophisticated, expressive, dynamic
- **Weights Used**:
  - Regular (400) for standard creative text
  - Italic (400i) for artistic expression
  - Bold (700) for emphasis

![Playfair Display Font Sample](https://assets.website-files.com/5f0801907ed7736e5de8cb15/5f27901a3c75e334a8d8b946_Playfair%20Display.jpg)

### Font Usage by Context

#### Website Sections

| Website Element | Font | Weight | Size | Notes |
|-----------------|------|--------|------|-------|
| Main Navigation | Space Grotesk | Medium (500) | 15px | Letter spacing: normal |
| Page Titles | Space Grotesk | Bold (700) | 48px | Letter spacing: tight |
| Section Headings | Space Grotesk | Bold (700) | 32px | Letter spacing: tight |
| Subheadings | Space Grotesk | Medium (500) | 24px | Letter spacing: normal |
| Body Text | Inter | Regular (400) | 16px | Line height: 1.5 |
| Buttons | Space Grotesk | Medium (500) | 14px | Uppercase with wide letter spacing |
| Links | Inter | Medium (500) | 16px | Same as body text with underline |
| Quotes | Cinzel | Regular (400) | 24px | Subtle indent and quotation marks |
| Spiritual Concepts | Cinzel | Medium (500) | Varies | Gold accent color |
| Pull Quotes | Playfair Display | Italic (400i) | 28px | Used sparingly for emphasis |
| Footer Links | Inter | Regular (400) | 14px | Slightly condensed spacing |
| Copyright Text | Inter | Light (300) | 12px | Lower emphasis |

#### Special Elements

1. **Tagline "Monetizing Fulfillment, Peace, & Truth"**
   - Font: Cinzel
   - Weight: Medium (500)
   - Style: All caps with wide letter spacing
   - Color: Gradient from Primary to Accent color

2. **"RESPECT" Concept**
   - Font: Space Grotesk
   - Weight: Bold (700)
   - Style: All caps with very wide letter spacing
   - Color: Variable depending on background

3. **Spiritual Quotations**
   - Font: Cinzel
   - Weight: Regular (400)
   - Style: Standard case with proper indentation
   - Special: Use golden highlight for key phrases

4. **Call-to-Action Buttons**
   - Font: Space Grotesk
   - Weight: Medium (500)
   - Style: All caps with wider letter spacing
   - Size: 14px (desktop), 16px (mobile)

### Implementation Details

1. **CSS Organization**
   - All typography styles are centralized in `css/typography.css`
   - Font imports occur at the top of this file
   - Base styles are applied to elements directly
   - Special styles are available via utility classes

2. **Utility Classes**
   - `.text-accent` for Cinzel font spiritual elements
   - `.text-creative` for Playfair Display creative elements
   - `.lead` for larger introductory paragraphs
   - `.quote` for stylized quotations
   - `.spiritual-concept` for highlighted concepts

3. **Responsive Considerations**
   - Font sizes scale down on mobile devices
   - Line heights remain consistent across breakpoints
   - Font weights may decrease slightly on smaller screens for better readability

### Accessibility Guidelines

- Maintain a minimum contrast ratio of 4.5:1 for body text
- Avoid using font sizes smaller than 14px (1.4rem)
- Do not rely solely on font styling to convey meaning
- Ensure heading hierarchy is preserved for screen readers
- Provide sufficient line height for improved readability

---

## Implementation Examples

### Headings

```html
<h1 class="hero__title">Reimagining Possible</h1>
<h2 class="section__title">Our Evolving Approach</h2>
<h3 class="feature__title">Multisensory Experiences</h3>
<h4 class="card__title">Neural Integration</h4>
```

### Spiritual Concepts

```html
<p>Through our approach to <span class="spiritual-concept">Collective Resonance</span>, we create experiences that transcend traditional boundaries.</p>
```

### Quotes

```html
<blockquote class="quote">
  The highest form of knowledge is empathy, for it requires us to suspend our egos and live in another's world.
  <cite class="quote-source">- Plato</cite>
</blockquote>
```

### Creative Elements

```html
<p class="text-creative">Explore the boundaries between perception and reality</p>
```

---

This typography system may evolve as our brand grows, but these guidelines provide a solid foundation for consistent visual communication across all Asabaal Ventures digital platforms.
