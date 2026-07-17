# .claude/agents/ — subagent definitions

A subagent is a `<name>.md` file: YAML frontmatter + a markdown system-prompt body. Subagents run in a
**fresh isolated context** (background by default; they return a summary), so they keep the main
session's context clean. Reach for one for fan-out research, an independent review/verify, or anything
read-heavy. See `kanban/playbook/03` for the keeper rule (subagent vs skill vs workflow).

## Frontmatter schema
```yaml
---
name: <kebab-name>          # optional; falls back to filename
description: "<when to invoke this agent — the auto-selection trigger; include 'Examples — ...'>"
tools: Read, Grep, Glob, Bash        # list or comma-string; omit to inherit all
model: sonnet                        # sonnet | opus | haiku | inherit — omit to inherit session model
---
```
Body = the agent's full instructions: role, do/don't, method, output shape.

## Conventions
- **One job per agent.** A researcher researches; a validator refutes; a decomposer decomposes. Don't
  build a do-everything agent.
- **Grant the least tools.** Read-only agents get `Read, Grep, Glob, Bash` (no Edit/Write) so they can't
  mutate. File-mutating parallel agents run with `isolation: 'worktree'` (set at call time).
- **Return data, not chat.** The final message IS the result; return a tight structured summary
  (file:line evidence, a verdict, a decomposition), not narration.
- **Adversarial by default for verification** — Generator ≠ Evaluator (`P-08`): the agent that wrote a
  change never grades it; a `validator` does, refute-by-default.

## Roster
| Agent | Job | Tools |
|---|---|---|
| codebase-researcher | Navigate the C++/Qt tree by symbol; answer "where/how is X" with file:line | Read, Grep, Glob, Bash |
| validator | Adversarially verify a change against its acceptance + house physics; run /code-review | Read, Grep, Glob, Bash |
| dossier-decomposer | Turn a problem into a dossier: PSes (EARS + acceptance) and execution waves | Read, Grep, Glob, Bash |
