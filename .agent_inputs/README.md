# Agent Inputs Directory

This directory contains structured input files for agent interactions, enabling reproducible and traceable AI agent workflows.

## Directory Structure

```
.agent_inputs/
├── README.md                    # This file
├── stage10_feedback/           # Stage 10 feedback inputs
│   ├── pending/               # Feedback waiting to be processed
│   ├── processed/             # Feedback that has been applied
│   └── templates/             # Reusable feedback templates
└── future_stages/             # Placeholder for other agent stages
```

## Usage

### Stage 10 Feedback Workflow

1. **Create feedback file** in `pending/`:
   ```bash
   # Example: .agent_inputs/stage10_feedback/pending/raw_input_corrections.md
   ```

2. **Process feedback**:
   ```bash
   python /path/to/stage10_feedback_updates.py "$(cat .agent_inputs/stage10_feedback/pending/raw_input_corrections.md)"
   ```

3. **Move to processed** after successful application:
   ```bash
   mv .agent_inputs/stage10_feedback/pending/raw_input_corrections.md \
      .agent_inputs/stage10_feedback/processed/raw_input_corrections_$(date +%Y%m%d_%H%M%S).md
   ```

### File Naming Convention

- **Pending files**: `{descriptive_name}.md`
- **Processed files**: `{descriptive_name}_{YYYYMMDD_HHMMSS}.md`
- **Templates**: `{template_type}_template.md`

## Benefits

- ✅ **Reproducible**: Same input produces same agent behavior
- ✅ **Traceable**: Complete audit trail of feedback provided
- ✅ **Version Control**: Can track feedback changes over time
- ✅ **Collaboration**: Team members can review and share feedback
- ✅ **Batch Processing**: Can queue multiple feedback files
- ✅ **Templates**: Reusable feedback patterns

## Integration with Agent Workflow

The agent system automatically:
1. Reads input files from `pending/` directory
2. Processes feedback using OpenRouter API
3. Updates analysis outputs
4. Moves processed files to `processed/` with timestamp

This ensures a clean, reproducible workflow for human-AI collaboration.