# Issue Creation Guide

## Step-by-Step Process

### 1. Determine Issue Location
Based on the status of your new issue, determine which file it should be added to:
- New issues generally go into `1_backlog.md`
- Prioritized and ready issues go into `2_todo.md`

### 2. Assign Issue ID
Check the most recent issue ID across all boards and increment by 1.

### 3. Copy the Template
Use the issue template from `//rupert/tracking/docs/issue_template.md`

### 4. Add Appropriate Emojis
Refer to `//rupert/tracking/docs/emoji_legend.md` for the correct emojis to use for:
- Priority level
- Status indicators
- Project type
- Acceptance criteria status

### 5. Fill in Issue Details
Complete all relevant fields in the template:
- Title and description
- Priority and status
- Dates and time estimates
- Acceptance criteria
- Any dependencies or relationships to other issues

### 6. Place the Issue in the File
Place new issues at the top of the file, maintaining the most recent issues at the top.

## Example

```markdown
### ISSUE-010: Implement API Authentication ud83cudd95
**Priority:** ud83dudd34 High
**Project:** ud83dudda5ufe0f IFM Project
**Created:** ud83dudcc5 2025-10-06
**Due:** u23f0 2025-10-20
**Estimated Hours:** u23f1ufe0f 8.0
**Status:** ud83cudd95 New

**Description:**
Implement OAuth 2.0 authentication for the API endpoints to ensure secure access.

**Acceptance Criteria:**
- u23f3 Authentication middleware created
- u23f3 Token validation implemented
- u23f3 User roles and permissions enforced
- u23f3 Integration tests written

**Dependencies:**
- ud83dudd17 ISSUE-006: Related to authentication debugging

**Comments:**
- [2025-10-06] @ethan: This is a high priority item for the next release.
```

## Moving Issues Between Boards

When an issue changes status:

1. Cut the entire issue entry from its current file
2. Update the status emoji and description
3. Update acceptance criteria status emojis as needed
4. Paste the updated issue into the appropriate destination file (at the top)

## Time Logging

Always include the date, hours spent, and a brief description of work done when logging time.

## Relationships Between Issues

Use the appropriate relationship indicators:
- ud83dudd17 Linked to another issue (general relationship)
- ud83dudd12 Blocked by another issue (dependency)
- ud83dudd11 Blocking another issue (inverse dependency)