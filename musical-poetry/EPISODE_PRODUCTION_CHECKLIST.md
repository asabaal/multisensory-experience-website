# Musical Poetry Episode Production Checklist

Use this checklist for each episode of Musical Poetry with Asabaal.

## Content Preparation

### Audio
- [ ] Export mastered audio file for the episode
- [ ] Upload audio file to hosting location
- [ ] Update `amusements-data.js` with correct `audioFile` path

### Lyrics
- [ ] Select key lyrics excerpts (not full lyrics)
- [ ] Format lyrics for readability
- [ ] Update episode HTML with lyrics excerpt

### Reflection & Commentary
- [ ] Write **Opening Reflection** (Author Commentary Zone 1)
  - What question birthed this piece?
  - What emotional state were you in?
  - What tension should the listener hold while listening?
  - Why does this episode come at this point in the series?
  
- [ ] Write **Commentary** (Author Commentary Zone 2)
  - Philosophical question of identity
  - Social perception vs self perception
  - Repentance and growth language
  - Human mutuality framework
  - Theological anthropology
  
- [ ] Write **Closing Reflection** (Author Commentary Zone 3)
  - End with contemplative resonance
  - Leave readers with something to ponder

## Page Assembly

Using the template file (`musical-poetry-template.html`):

1. [ ] Duplicate the template file
   ```bash
   cp musical-poetry-template.html season-1/episode-X.html
   ```

2. [ ] Update episode-specific details:
   - [ ] Page title in `<head>`
   - [ ] Episode number in breadcrumb
   - [ ] Episode title in header
   - [ ] Episode number in JavaScript call

3. [ ] Insert content:
   - [ ] Opening reflection text
   - [ ] Audio file path
   - [ ] Audio info (title, project, format)
   - [ ] Lyrics excerpt
   - [ ] Commentary text
   - [ ] Series arc context
   - [ ] Album breadcrumb
   - [ ] Closing reflection

4. [ ] Update navigation links:
   - [ ] Previous episode link (or hide if first)
   - [ ] Next episode link (or hide if last)

5. [ ] Test the page in browser:
   - [ ] Audio player loads correctly
   - [ ] All sections display properly
   - [ ] Navigation works
   - [ ] Responsive design looks good on mobile

## Data Updates

Update `assets/js/amusements-data.js`:

```javascript
{
  number: X,
  title: "Episode Title",
  description: "Short description for episode card",
  duration: "X min",
  audioFile: "assets/shows/musical-poetry/season1/episodeX-audio.mp3",
  openingReflection: "[Your opening reflection text]",
  lyricsExcerpt: ["Line 1", "Line 2", ...],
  commentary: "[Your commentary text]",
  seriesArcContext: "[Series arc context]",
  albumBreadcrumb: "[Album breadcrumb]",
  closingReflection: "[Your closing reflection]"
}
```

## Publication

### Pre-Publish
- [ ] Add cover art if desired
- [ ] Tag by themes (faith, identity, liberation, etc.)
- [ ] Verify all links work
- [ ] Test audio player functionality

### Publish
- [ ] Commit changes to git
- [ ] Push to production
- [ ] Verify page loads on live site
- [ ] Test audio playback on live site

### Post-Publish
- [ ] Share link on social media
- [ ] Add to blog index if applicable
- [ ] Update analytics tracking
- [ ] Gather listener feedback

## Episode Order Reference

Season 1 episodes in narrative order:

1. **Who Do You Think I Am** - Identity questioned
2. **CHILD OF GOD (WHO YOU BE)** - Identity claimed
3. **Ask Seek Knock** - Faith practiced
4. **NOT YOUR SLAVE** - Bondage rejected
5. **How Do I Praise You?** - Worship wrestled
6. **Take This Cup** - Calling accepted
7. **Sacrifice Season** - Sacrifice embraced
8. **Love Them Harder** - Love chosen

## Template Workflow

For each new episode:

1. Copy template: `cp musical-poetry-template.html season-1/episode-[N].html`
2. Read the file: Use Edit tool to make changes
3. Replace placeholders:
   - `[Episode Title Here]`
   - `[Opening reflection goes here]`
   - `[INSERT-AUDIO-FILE.mp3]`
   - `[Lyrics excerpt goes here]`
   - `[Commentary analysis goes here]`
   - `[Series arc context goes here]`
   - `[Album breadcrumb goes here]`
   - `[Closing reflection goes here]`
4. Update navigation links for prev/next episodes
5. Update episode number in JavaScript call
6. Test and publish

## Quick Reference: File Paths

- **Template**: `/musical-poetry/musical-poetry-template.html`
- **Season 1 Episodes**: `/musical-poetry/season-1/episode-[1-8].html`
- **Data File**: `/assets/js/amusements-data.js`
- **Navigation Script**: `/assets/js/amusements-navigation.js`
- **Audio Files**: `/assets/shows/musical-poetry/season1/episode-[N]-audio.mp3`

## Notes

- Always test audio playback on multiple browsers
- Keep lyrics excerpts brief for blog readability
- Use serif font for lyrics, sans-serif for commentary
- Album breadcrumbs should be subtle, not promotional
- Each episode builds on the previous narrative arc
- Navigation links should be hidden for first/last episodes

## Support

If you encounter issues:
- Check console for JavaScript errors
- Verify file paths are correct
- Ensure audio files exist and are accessible
- Test responsive design on mobile devices
