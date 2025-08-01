# Agentic PR Analysis System - Technical Walkthrough

*Visual guide to how the agent-calling-agents architecture works*

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    PR ANALYZER ORCHESTRATOR                     │
│                        (pr_analyzer.py)                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS PIPELINE                            │
│  1. Git Analysis    2. File Classification    3. Impact Scoring │
│  4. Agentic Quality Analysis    5. Report Generation            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 AGENTIC QUALITY ANALYZER                        │
│                (agentic_quality_analyzer.py)                    │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ DUPLICATE   │  │ MERGE       │  │ PATTERN     │             │
│  │ DETECTION   │  │ READINESS   │  │ ANALYSIS    │             │
│  │ AGENT       │  │ AGENT       │  │ AGENT       │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Communication Flow

### Phase 1: Context Preparation
```
PR Analyzer
    │
    ├── Extract file changes from git
    ├── Read file contents (up to 50KB each)
    ├── Classify files by category and importance
    └── Build analysis context JSON
         │
         ▼
┌─────────────────────────────────────────┐
│        ANALYSIS CONTEXT                 │
│                                         │
│ {                                       │
│   "pr_summary": {                       │
│     "total_files_changed": 257,         │
│     "total_lines_added": 48149,         │
│     "commit_messages": [...]            │
│   },                                    │
│   "files": [                            │
│     {                                   │
│       "path": "content/auto_blog.py",   │
│       "category": "CORE_BUSINESS",      │
│       "content_sample": "...",          │
│       "lines_added": 255                │
│     }                                   │
│   ],                                    │
│   "categories": {...}                   │
│ }                                       │
└─────────────────────────────────────────┘
```

### Phase 2: Agent Dispatch

```
AgenticQualityAnalyzer._launch_duplicate_detection_agent()
    │
    ├── Build specialized prompt with file content analysis
    ├── Call subprocess: claude -p "<PROMPT>"
    └── Parse agent response for duplicate issues
         │
         ▼
┌─────────────────────────────────────────┐
│     DUPLICATE DETECTION AGENT          │
│                                         │
│ PROMPT: "You are a senior software      │
│ architect analyzing 257 files for       │
│ functional duplicates. Here's the       │
│ actual file content:                    │
│                                         │
│ ### CORE_BUSINESS_LOGIC FILES           │
│ #### content/auto_blog_processor.py     │
│ - Content: def process_blog_posts()...  │
│ #### content/automated_blog.py          │  
│ - Content: def process_posts()...       │
│                                         │
│ DISCOVER files serving similar         │
│ purposes by analyzing functionality..." │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│        AGENT RESPONSE                   │
│                                         │
│ "CRITICAL: Found 8 blog processing     │
│ scripts with overlapping functionality: │
│                                         │
│ Files: auto_blog_processor.py,          │
│        automated_blog_processor.py,     │
│        batch_process_all_posts.py...    │
│                                         │
│ Evidence: All contain similar function  │
│ definitions for blog post processing... │
│                                         │
│ Recommendation: Consolidate into        │
│ single system..."                       │
└─────────────────────────────────────────┘
```

### Phase 3: Parallel Agent Execution

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ DUPLICATE AGENT │    │ READINESS AGENT │    │ PATTERN AGENT   │
│                 │    │                 │    │                 │
│ Analyzes:       │    │ Analyzes:       │    │ Analyzes:       │
│ • File content  │    │ • Completeness  │    │ • Code patterns │
│ • Functionality │    │ • Code quality  │    │ • Consistency   │
│ • Similar logic │    │ • Risk factors  │    │ • Architecture  │
│                 │    │                 │    │                 │
│ subprocess.run( │    │ subprocess.run( │    │ subprocess.run( │
│   ['claude',    │    │   ['claude',    │    │   ['claude',    │
│    '-p', prompt]│    │    '-p', prompt]│    │    '-p', prompt]│
│ )               │    │ )               │    │ )               │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┬─────────────────┬─────────────────┐
│    RESULTS      │    RESULTS      │    RESULTS      │
│                 │                 │                 │
│ • 3 CRITICAL    │ • Score: 72/100 │ • 2 MEDIUM      │
│ • 2 HIGH        │ • Status: REVIEW│ • Consistency   │
│ • Duplicates    │ • 4 blocking    │ • Architecture  │
│   found         │   issues        │   issues        │
└─────────────────┴─────────────────┴─────────────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ COMBINE RESULTS │
                 │                 │
                 │ • All issues    │
                 │ • Quality score │
                 │ • Readiness     │
                 │ • Recommendations│
                 └─────────────────┘
```

---

## Technical Implementation Details

### 1. Agent Communication Protocol

```python
def _call_claude_agent(self, prompt):
    """Call Claude CLI using subprocess"""
    try:
        # Clean prompt for safety
        clean_prompt = prompt.replace('\x00', '').replace('\r\n', '\n')
        
        # Subprocess call to Claude CLI
        cmd = ['claude', '-p', clean_prompt]
        result = subprocess.run(
            cmd, 
            env={**os.environ, 'CLAUDE_CODE_OAUTH_TOKEN': self.oauth_token},
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            raise RuntimeError(f"Agent failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("Agent timeout after 120 seconds")
    except FileNotFoundError:
        raise RuntimeError("Claude CLI not found")
```

### 2. Agent Specialization Architecture

```
DUPLICATE DETECTION AGENT
├── Purpose: Find functionally similar files
├── Input: File content + functional analysis
├── Method: Content comparison + semantic analysis
├── Output: QualityIssue objects with evidence
└── Reasoning: "Files have similar content hashes indicating duplication"

MERGE READINESS AGENT  
├── Purpose: Assess deployment safety
├── Input: PR overview + file categories + commit messages
├── Method: Completeness + quality + risk assessment
├── Output: JSON with score, status, blocking issues
└── Reasoning: "Large PR with mixed concerns needs review"

PATTERN ANALYSIS AGENT
├── Purpose: Code consistency and architecture review
├── Input: Code patterns + project structure
├── Method: Pattern matching + convention analysis  
├── Output: Architecture and consistency issues
└── Reasoning: "Inconsistent naming conventions detected"
```

### 3. Error Handling & Fallbacks

```
┌─────────────────────────────────────────┐
│           AGENT CALL FLOW               │
│                                         │
│ 1. Prepare context & prompts            │
│ 2. Launch agent via subprocess          │
│ 3. Parse structured response            │
│ 4. Handle failures gracefully           │
└─────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│         ERROR SCENARIOS                 │
│                                         │
│ • Claude CLI not found                  │
│   └── RuntimeError: "Install Claude"   │
│                                         │
│ • OAuth token missing                   │
│   └── RuntimeError: "Set OAUTH token"  │
│                                         │  
│ • Agent timeout (120s)                  │
│   └── RuntimeError: "Agent timeout"    │
│                                         │
│ • JSON parsing fails                    │
│   └── Fall back to text parsing        │
│                                         │
│ • Network/API errors                    │
│   └── RuntimeError: "Agent call failed"│
└─────────────────────────────────────────┘
```

### 4. Response Processing Pipeline

```
Agent Response → Parse JSON → Extract Issues → Filter Exceptions → Combine Results

Example Flow:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Raw Agent Text  │    │ JSON Extraction │    │ Issue Objects   │
│                 │    │                 │    │                 │
│ "```json        │    │ {               │    │ QualityIssue(   │
│ {               │───▶│   "issues": [   │───▶│   severity="HIGH"│
│   "issues": [   │    │     {           │    │   category="DUP"│
│     {           │    │       "severity"│    │   title="..."   │
│       "severity"│    │       "title"   │    │   files=[...]   │
│ ...             │    │ ...             │    │ )               │
│ ```"            │    │ }               │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │ Filter by       │
                                              │ Exceptions      │
                                              │                 │
                                              │ Skip suppressed │
                                              │ patterns        │
                                              └─────────────────┘
```

---

## Why Agents Are Failing

### Current Failure Points

1. **Claude CLI Dependency**
   ```bash
   # System tries to call:
   claude -p "You are a senior software architect..."
   
   # Likely failures:
   # - CLI not installed globally
   # - PATH issues in subprocess environment
   # - OAuth token not properly passed
   # - CLI version incompatibility
   ```

2. **Subprocess Environment**
   ```python
   # Environment variables may not transfer properly
   env={**os.environ, 'CLAUDE_CODE_OAUTH_TOKEN': self.oauth_token}
   
   # Issues:
   # - OAuth token format/validity
   # - Environment isolation in subprocess
   # - Shell configuration differences
   ```

3. **Response Parsing Brittleness**
   ```python
   # Expecting structured JSON, but getting:
   # - Free-form text responses
   # - Malformed JSON
   # - Timeout errors
   # - Rate limiting responses
   ```

### Recommended Fixes

1. **Replace subprocess with direct API calls**
2. **Add comprehensive error handling and logging**
3. **Implement graceful fallbacks for each agent**
4. **Modularize prompts and response parsing**

---

## System Performance Profile

### Current Manual Process
- **Time:** 45-60 minutes per PR
- **Accuracy:** High (human insight)
- **Consistency:** Low (varies by reviewer)
- **Scalability:** Poor (doesn't scale)

### Target Automated System  
- **Time:** 2-3 minutes per PR
- **Accuracy:** Very High (AI + structured analysis)
- **Consistency:** Excellent (standardized process)
- **Scalability:** Excellent (handles any PR size)

### Bottlenecks Identified
1. **File content reading** - Limited to 50KB per file
2. **Agent communication** - Subprocess overhead
3. **Response parsing** - Fragile JSON extraction
4. **Context preparation** - Large prompt assembly

---

*This walkthrough shows exactly how your agentic system should work when properly implemented. The architecture is sound, but the execution needs to be fixed.*