# SOP: OpenSpec Workflow with Claude Code CLI

Use this SOP when working from a terminal. Claude Code CLI gives you a persistent session with slash commands, including the `/opsx` OpenSpec commands.

---

## Prerequisites

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify
claude --version

# Authenticate (first time)
claude login
```

---

## Starting a new change

### 1. Open a session in your project root

```bash
cd /path/to/project
claude
```

You are now in an interactive Claude Code session. The agent can see your entire repo.

---

### 2. Propose the change — `/opsx propose`

Type in the session:

```
/opsx propose
```

Claude will ask what you want to build. Describe it in plain English — no need to know the right file names or structure yet:

```
I want to create an AWS AgentCore Gateway in the columbia account (169976659173)
that will act as an MCP endpoint for Claude Code.
```

The command creates:
```
openspec/changes/<slug>/
├── .openspec.yaml
└── proposal.md
```

Read `proposal.md` and push back on anything wrong:

```
Change the gateway name to "mcp-tools-gateway".
Remove the Lambda registration — that is a separate change.
```

Claude edits the file. Iterate until the scope is right.

---

### 3. Explore context — `/opsx explore`

```
/opsx explore
```

Claude reads the existing codebase (other spec files, config, existing code) to understand context before writing the design. This prevents the design from contradicting decisions already made in other changes.

---

### 4. Write the design

```
Write design.md for this change using the proposal and what you found in the codebase.
```

Claude creates `design.md` with a Decisions section. **Review each decision.** These are locked during implementation — the agent will not deviate from them.

To override a decision:

```
Change D1: use CDK instead of the Console for gateway creation.
Add a decision about which CDK construct to use.
```

---

### 5. Sync specs — `/opsx sync`

```
/opsx sync
```

Claude generates `specs/<capability>/spec.md` from the design decisions. Each spec contains formal requirements (SHALL statements) and Given/When/Then scenarios that become the acceptance criteria.

Review the scenarios — if a scenario is wrong, the implementation will be wrong too.

---

### 6. Generate tasks

```
Write tasks.md from the design and specs.
Make each task small enough to check off with a single observation or test.
```

Claude creates `tasks.md`. This is the agent's work order — it will execute these tasks top-to-bottom during implementation.

---

### 7. Open a spec PR

Still inside the Claude session:

```
Commit the spec files and open a PR on GitHub for team review.
No implementation yet — spec only.
```

Claude will:
1. Stage the `openspec/changes/<slug>/` files
2. Create a branch `spec/<slug>`
3. Push and open a PR via `gh pr create`

Your colleagues review `proposal.md` (scope), `design.md` (decisions), and `specs/` (requirements) before any code is written.

---

### 8. Implement — `/opsx apply`

Once the PR is approved (or you are ready to start):

```
/opsx apply
```

Or explicitly:

```
Implement the tasks in openspec/changes/<slug>/tasks.md in order.
Check each task off as you complete it.
Do not deviate from the decisions in design.md.
```

The agent reads `design.md` (locked decisions), `specs/` (acceptance criteria), and then executes `tasks.md` top-to-bottom. Watch the checkboxes fill in — each `[x]` means one verified unit of work is done.

---

### 9. Archive — `/opsx archive`

```
/opsx archive
```

Moves the completed change folder to `openspec/archive/<slug>/`. The `openspec/changes/` directory stays clean — only in-flight work lives there.

---

## Iterating with colleagues

**Colleague picks up your spec:**

They pull the branch and run:

```bash
claude
```

Then:

```
Implement the tasks in openspec/changes/agentcore-gateway/tasks.md in order.
The design decisions in design.md are locked — follow them exactly.
```

No context-sharing needed — everything they need is in the spec files.

**Changing a decision mid-implementation:**

If something is wrong, stop, update `design.md` first, then continue:

```
I found that CDK does not support AgentCore Gateway yet. Update D1 in design.md
to use the AWS CLI instead, and update the relevant tasks in tasks.md.
```

---

## Quick command reference

| Command | What it does |
|---|---|
| `/opsx propose` | Creates `proposal.md` and `.openspec.yaml` |
| `/opsx explore` | Reads the codebase to inform the design |
| `/opsx sync` | Generates `specs/<capability>/spec.md` from the design |
| `/opsx apply` | Implements `tasks.md` top-to-bottom |
| `/opsx archive` | Moves a completed change to `openspec/archive/` |

---

## Tips

- Keep the session open while iterating on spec files — Claude remembers what you've discussed.
- Use `Ctrl+C` to interrupt the agent mid-task if you need to correct course.
- Run `/compact` if the session grows very long — it summarises context without losing key decisions.
- Run `/cost` to see how much the session has cost so far.
