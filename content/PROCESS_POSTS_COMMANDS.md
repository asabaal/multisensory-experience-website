# 📝 Blog Processing Commands - One at a Time

## Setup (Run Once)
```bash
export CLAUDE_CODE_OAUTH_TOKEN='your-token-here'
cd /home/asabaal/asabaal_ventures/repos/multisensory-experience-website/content
```

## Process Each Post (Run One at a Time)

### Posts with Real Content (Ready to Process!)

1. **Why: A Plea for Change**
```bash
python automated_claude_processor.py why.md --auto-update
```

2. **Collaborative Business Models & Ethical Advertising**
```bash
python automated_claude_processor.py collaborative-business-models-and-ethical-advertising.md --auto-update
```

3. **By My Hand: Discarding Hurt for Unity**
```bash
python automated_claude_processor.py by-my-hand.md --auto-update
```

4. **Charting the Course for a More Fulfilling Future**
```bash
python automated_claude_processor.py charting-the-course-for-a-more-fulfilling-future.md --auto-update
```

5. **Ethical Advocacy & The Future of Education**
```bash
python automated_claude_processor.py ethical-advocacy-and-the-future-of-education.md --auto-update
```

6. **Free As A Bird: A Spiritual Journey**
```bash
python automated_claude_processor.py free-as-a-bird.md --auto-update
```

7. **Keep It Simple - Simple Indeed**
```bash
python automated_claude_processor.py keep-it-simple.md --auto-update
```

8. **Logical Fallacies - Let's Start Thinking Together**
```bash
python automated_claude_processor.py logical-fallacies.md --auto-update
```

9. **Microaggression: Becoming Cognizant of Our Actions**
```bash
python automated_claude_processor.py microaggression.md --auto-update
```

10. **No - Fighting the Evil Inside of Yourself**
```bash
python automated_claude_processor.py no.md --auto-update
```

11. **Omniscient - What Does That Actually Mean?**
```bash
python automated_claude_processor.py omniscient.md --auto-update
```

12. **Power of Pain - You Already Feel It; Leverage It**
```bash
python automated_claude_processor.py power-of-pain.md --auto-update
```

13. **Probably Right: You're Probably Right, And So Am I**
```bash
python automated_claude_processor.py probably-right.md --auto-update
```

14. **Human Creativity with AI & Ethical Social Platforms**
```bash
python automated_claude_processor.py human-creativity-with-ai-and-ethical-social-platforms.md --auto-update
```

15. **Respect: The Fundamental Human Right**
```bash
python automated_claude_processor.py respect-the-fundamental-human-right.md --auto-update
```

16. **What Happens When A Queer Christian Remixes Anike's 'Send That'?**
```bash
python automated_claude_processor.py send-that.md --auto-update
```

17. **Why I Entered the AI Remix Competition**
```bash
python automated_claude_processor.py soundclash.md --auto-update
```

18. **Special: We are all special**
```bash
python automated_claude_processor.py special.md --auto-update
```

19. **Your Nature - Starting A Conversation**
```bash
python automated_claude_processor.py your-nature.md --auto-update
```

20. **The Future of Work and Personal Growth**
```bash
python automated_claude_processor.py the-future-of-work-and-personal-growth.md --auto-update
```

21. **The Unity of Truth: Global Peace Is Inevitable**
```bash
python automated_claude_processor.py the-unity-of-truth.md --auto-update
```

22. **Unveiling the Future of Asabaal Ventures**
```bash
python automated_claude_processor.py unveiling-the-future-of-asabaal-ventures.md --auto-update
```

23. **Asabaal Ventures: The Dawn of a New Era**
```bash
python automated_claude_processor.py asabaal-ventures.md --auto-update
```

24. **"More Than Me": How My Beliefs Evolved**
```bash
python automated_claude_processor.py more-than-me.md --auto-update
```

## 🔄 Refresh Blog Explorer (Cards Page)

If your blog explorer/cards page isn't showing all posts correctly:

### Option 1: Using main script
```bash
python automated_claude_processor.py --refresh-blog-explorer
```

### Option 2: Using standalone script
```bash
python refresh_blog_explorer.py
```

This will:
- Scan all published posts in `content/blog/published/`
- Rebuild the complete `blog-data.js` file
- Sort posts by date (newest first)
- Update all IDs sequentially

## 📊 Check Progress

After each post, you can check:
```bash
# See what's been generated
ls -la ../blog/post-*.html | wc -l

# Check blog data entries
grep -c '"id":' ../assets/js/blog-data.js

# Refresh blog explorer if needed
python refresh_blog_explorer.py
```

## 🎯 Tips

1. **Watch the output** - Each post will show:
   - Step 1: Extracting content
   - Step 2: Creating prompt
   - Step 3: Calling Claude (30-120 seconds)
   - Step 4: Extracting JSON
   - Step 5: Saving JSON
   - Step 6: Generating HTML
   - Step 7: Updating blog explorer

2. **If a post fails**, you can retry it:
   - Check the error message
   - Fix any issues
   - Run the same command again

3. **Take breaks** - Processing 24 posts will take 20-40 minutes total
   - Do a few at a time if you prefer
   - The `--auto-update` flag means it won't stop to ask questions

Happy processing! 🚀