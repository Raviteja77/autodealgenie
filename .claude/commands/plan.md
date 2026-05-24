# /plan — Plan a Feature (Architect Mode)

Load: @.claude/skills/architect.md
Load memory: @.claude/memory/PROGRESS.md @.claude/memory/DECISIONS.md

You are now in **Architect Mode** for AutoDealGenie.
Feature to plan: $ARGUMENTS

Steps:
1. Check PROGRESS.md — is this feature already in progress or decided?
2. Check DECISIONS.md — are there existing decisions that constrain this?
3. Interview the user with clarifying questions before proposing anything.
4. Write the spec to `docs/SPEC-[feature-kebab-name].md`
5. Close with: "Ready. Start a **fresh session** and run `/implement [feature name]`"

Do NOT write any implementation code in this session.
