# /implement — Implement a Feature (Dev Mode)

Load memory: @.claude/memory/PROGRESS.md @.claude/memory/GOTCHAS.md

Feature to implement: $ARGUMENTS

Steps:
1. Look for `docs/SPEC-*.md` for this feature. If found, read it. If not found:
   ask "No spec found. Run `/plan [feature]` first, or describe what to build."
2. Based on the spec, load the right skills:
   - If backend work → @.claude/skills/fastapi-python.md
   - If frontend work → @.claude/skills/nextjs-frontend.md
   - If both → load both
3. List sub-tasks in order before starting. Ask "Any questions before I start?"
4. Build step by step. After each logical chunk, pause and say what was done.
5. When complete: list all files changed/created, run the QA checklist.
6. Ask: "Should I update PROGRESS.md with what we built?"
