# Issue Tracking System

This is a kanban-style issue tracking system for managing consulting projects and tasks. The system is organized into different stages of work represented by separate markdown files.

## Board Structure

- **1_backlog.md** - Incoming issues/tasks not yet prioritized
- **2_todo.md** - Prioritized items ready to be worked on
- **3_in_progress.md** - Items currently being worked on
- **4_review.md** - Items awaiting review/feedback
- **5_completed.md** - Finished items

## Documentation

This directory contains the following reference documents:

- **emoji_legend.md** - Complete reference for all emoji indicators used in the system
- **issue_template.md** - Template to copy when creating new issues
- **issue_creation_guide.md** - Step-by-step guide for creating and moving issues
- **kanban_visualization.md** - Overview of the kanban workflow

## Quick Start

1. To create a new issue, follow the instructions in `issue_creation_guide.md`
2. Use the template in `issue_template.md` as your starting point
3. Refer to `emoji_legend.md` for the appropriate status indicators and emojis

## Issue Format

Each issue follows this structure:

```markdown
### ISSUE-ID: Issue Title [Status Emoji]
**Priority:** [Priority Emoji] [High/Medium/Low]
**Project:** [Project Emoji] [Project Name]
**Created:** ud83dudcc5 YYYY-MM-DD
**Due:** u23f0 YYYY-MM-DD (if applicable)
**Estimated Hours:** u23f1ufe0f X.X

**Description:**
Detailed description of the issue or task.

**Acceptance Criteria:**
- [Status Emoji] Criterion 1
- [Status Emoji] Criterion 2

**Dependencies:**
- [Relationship Emoji] ISSUE-XXX: Description

**Comments:**
- [YYYY-MM-DD] @user: Comment text
```

## Usage

To move an issue between stages, cut the entire issue section from one file and paste it into the appropriate destination file. Update the status indicators accordingly. Maintain chronological order with newest items at the top.

## Time Tracking

As you work on issues, log time directly in the issue with comments:

```markdown
**Time Logged:**
- [YYYY-MM-DD] X.X hrs - Brief description of work done
```