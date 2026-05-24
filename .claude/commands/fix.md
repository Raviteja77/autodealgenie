# /fix — Fix a Bug

Load: @.claude/skills/senior-dev.md
Load: @.claude/memory/GOTCHAS.md

Bug to fix: $ARGUMENTS

Steps:
1. Reproduce it — describe the exact steps to trigger this bug
2. Root cause — trace back to WHY, not just WHERE
3. Minimal fix — smallest correct change
4. Regression test — write the test that catches this
5. Sibling check — is the same mistake made elsewhere?

Output:
```
Root cause: [actual underlying problem]
Files changed: [list]
Test added: [path]
Siblings found: [any other instances]
```

After fixing, ask: "Should I add this to GOTCHAS.md so it doesn't happen again?"
