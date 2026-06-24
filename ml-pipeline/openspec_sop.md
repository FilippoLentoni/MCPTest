# OpenSpec SOP — Spec-Driven Development with a Coding Agent

This document explains how to use the OpenSpec workflow to plan, review, and implement features collaboratively with a coding agent (Claude Code).

---

## What Is OpenSpec?

OpenSpec is a spec-driven development approach where every feature starts as a set of structured documents — a proposal, a design, capability specs, and a task checklist — before a single line of code is written. The spec files live inside the repo alongside the code, making them version-controlled, reviewable in PRs, and consumable by a coding agent.

The key idea: **the agent builds from the spec, not from improvisation.** Your colleagues review the spec before implementation begins. The spec is the shared contract.

---

## Folder Structure

Every feature gets its own subdirectory under `openspec/changes/`:

```
openspec/
└── changes/
    └── <feature-slug>/              ← one folder per feature
        ├── .openspec.yaml           ← metadata (schema version, creation date)
        ├── proposal.md              ← why & what (non-technical, shareable)
        ├── design.md                ← technical decisions & trade-offs
        ├── tasks.md                 ← implementation checklist (agent works from this)
        └── specs/
            └── <capability-name>/
                └── spec.md          ← requirements + Given/When/Then scenarios
```

Multiple capabilities can live under `specs/` — one subfolder each.

---

## File Purposes

| File | Who writes it | Who reads it | Purpose |
|---|---|---|---|
| `proposal.md` | You | Colleagues, agent | Justifies the feature; defines capabilities added/modified |
| `design.md` | You (or agent assisted) | Agent, reviewers | Technical decisions, trade-offs, non-goals — agent MUST not override these |
| `specs/<cap>/spec.md` | You (or agent assisted) | Agent, reviewers | Precise requirements + scenarios — the acceptance criteria |
| `tasks.md` | You (or agent assisted) | Agent | Ordered checklist — agent checks items off as it implements |
| `.openspec.yaml` | Auto | Agent | Metadata marker so tooling can discover the change |

---

## The Workflow

### Phase 1 — Propose (you → agent)

Start a conversation with your coding agent:

```
I want to add <feature>. Help me write a proposal.
```

The agent will ask clarifying questions and produce `proposal.md`. Review it. Adjust the capabilities list — this is the scope contract.

### Phase 2 — Design (agent → you review)

Tell the agent:

```
Now write the design for this change. Use the proposal and explore the existing codebase.
```

The agent reads your repo, understands the context, and drafts `design.md` with decisions and trade-offs. **You review and edit** — especially the Decisions section. Once merged/approved, these decisions are locked for implementation.

### Phase 3 — Spec (agent → you review)

```
Write the specs for each capability listed in the proposal.
```

The agent produces `specs/<capability>/spec.md` with formal requirements and Given/When/Then scenarios. These become the acceptance criteria. If a requirement is wrong here, implementation will be wrong too — review carefully.

### Phase 4 — Tasks (agent → you review)

```
Break the design and specs into a task checklist.
```

The agent produces `tasks.md` — a numbered, ordered checklist that a fresh agent can execute top-to-bottom without needing to ask questions. Review for completeness: missing a setup step here causes the agent to make assumptions later.

### Phase 5 — PR for review (you)

Commit all four files (no code yet) and open a PR. This is the **spec PR**:

```bash
git checkout -b <feature-slug>
git add openspec/changes/<feature-slug>/
git commit -m "spec: add OpenSpec for <feature-slug>"
git push -u origin <feature-slug>
gh pr create --title "spec: <feature-slug>" --body "..."
```

Colleagues review `proposal.md` (scope), `design.md` (approach), and `specs/` (requirements). They can comment, push alternative decisions, or pick up the implementation themselves by pulling the branch.

### Phase 6 — Implement (agent works from tasks.md)

Once the PR is approved (or you are ready to start):

```
Implement the tasks in openspec/changes/<feature-slug>/tasks.md.
Work through them in order. Check each item off as you complete it.
Do not deviate from the decisions in design.md.
```

The agent reads `design.md` first (locked decisions), then `specs/` (acceptance criteria), then executes `tasks.md` top-to-bottom, marking items `[x]` as it goes. When the last task is checked, the feature is done.

### Phase 7 — Verify & archive

Run tests and verify the spec scenarios manually. Then archive the change:

```
Archive the weather-lambda-tool change now that implementation is complete.
```

The agent marks the change as archived (moves it to `openspec/archive/` or similar) so the `changes/` folder only shows in-flight work.

---

## Collaboration Patterns

### Colleague picks up implementation

A colleague can pull the spec branch and say to their own coding agent:

```
Implement the tasks in openspec/changes/weather-lambda-tool/tasks.md.
The design decisions are locked in design.md — follow them.
```

They never need to re-derive the decisions or ask "why did we choose X."

### Splitting work

If two capabilities can be built in parallel, create two separate change folders. Each gets its own PR, its own task checklist, and can be implemented by different people simultaneously.

### Changing direction mid-implementation

If implementation reveals a design decision was wrong, stop and update `design.md` first (in a new commit), then continue. The spec files are the source of truth — the code follows them, not the other way around.

---

## Example: This Project

This repo uses OpenSpec for the **AgentCore MCP Gateway** project:

| Change folder | Feature | Status |
|---|---|---|
| `openspec/changes/weather-lambda-tool/` | Weather Lambda + AgentCore registration | In spec review |
| `openspec/changes/stock-lambda-tool/` | Google Stock Lambda + AgentCore registration | Planned |
| `openspec/changes/agentcore-gateway/` | AgentCore Gateway configuration + MCP endpoint | Planned |

The goal is a Claude Code agent that connects to the AgentCore Gateway via MCP and can invoke both tools from a conversation.

---

## Quick Reference

```
# Start a new change
/opsx propose               ← generates proposal.md
/opsx explore               ← agent reads repo context for design
/opsx sync                  ← syncs specs from design decisions

# Implement
/opsx apply                 ← agent works through tasks.md

# Finish
/opsx archive               ← moves completed change to archive
```

---

## Tips

- **Keep `design.md` decisions short.** One decision = one heading. Alternatives considered go under it. Reviewers skim — walls of text get rubber-stamped.
- **Write specs in user-facing language.** "The system SHALL return HTTP 200" is better than "the Lambda handler must return 200." The agent translates requirements to code; you translate intent to requirements.
- **Tasks.md is for the agent, not for humans.** It can be verbose and mechanical. If the agent needs a command to run, put the exact command in the task.
- **One task = one verifiable unit.** If you can't check it off with a single test or observation, split it.
- **Never skip the spec PR.** Reviewing a 200-line spec takes 10 minutes. Reviewing a 2000-line implementation PR takes 2 hours — and the design mistakes are already baked in.
