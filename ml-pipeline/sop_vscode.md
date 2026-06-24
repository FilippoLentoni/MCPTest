# SOP: OpenSpec Workflow with the Claude VS Code Extension

Use this SOP when working inside VS Code. The Claude extension gives you a chat panel alongside your editor, so you can read spec files and talk to Claude in the same window.

---

## Prerequisites

1. Install the **Claude** extension from the VS Code marketplace (search "Claude by Anthropic" or "Claude Code")
2. Sign in: open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`) → **Claude: Sign In**
3. Open your project folder in VS Code

---

## Opening Claude

- Click the **Claude icon** in the Activity Bar (left sidebar), or
- `Cmd+Shift+P` → **Claude: Open Chat**

The chat panel opens. Claude can see the files in your workspace.

---

## Starting a new change

### 1. Propose the change

Type in the chat panel:

```
I want to add a new change to this project.
Use the openspec/ folder structure (see the existing example under
openspec/changes/build-training-pipeline/ for the file layout).

Feature: create an AWS AgentCore Gateway in account columbia (169976659173),
region us-east-1, that will serve as the MCP endpoint for Claude Code.
Create proposal.md and .openspec.yaml for this change.
```

Claude creates the files. They appear in the Explorer panel — click to open them.

---

### 2. Review inline

With `proposal.md` open in the editor, **select the text you want to change** and then type in the chat:

```
The capability name should be "agentcore-gateway-resource" not "gateway".
Also remove the Lambda registration — that is a separate change.
```

Claude edits the file directly. You see the diff in the editor.

> **Tip:** You do not need to select text. Claude can see any file you have open. Saying "update the proposal" is enough if only one file is open.

---

### 3. Write the design

```
Now explore the openspec/ folder for context and write design.md for this change.
Lock in these decisions:
- Gateway name: mcp-tools-gateway
- Auth: IAM (SigV4)
- Create via AWS Console (no IaC for first iteration)
- Record gateway_id and endpoint URL in gateway_config.json
```

Claude creates `design.md`. Open it in a split editor (`Cmd+\`) so you can read it while chatting.

---

### 4. Generate specs

```
Write specs/gateway-resource/spec.md from the design.
Use SHALL statements for requirements and Given/When/Then for scenarios.
```

Claude creates the spec file. Review the scenarios in the editor.

---

### 5. Generate tasks

```
Write tasks.md from the design and specs.
Tasks should be concrete enough for an agent to execute without asking questions.
```

Claude creates `tasks.md`. Each unchecked item `[ ]` is one unit of work.

---

### 6. Open a spec PR

```
Commit the spec files for agentcore-gateway and open a PR on GitHub.
Branch name: spec/agentcore-gateway
PR title: "spec: agentcore-gateway — MCP entry point"
No implementation code — spec files only.
```

Claude uses the VS Code integrated terminal to run `git` and `gh` commands. You can watch the output in the **Terminal** panel (`Ctrl+\``).

---

### 7. Implement

Once the PR is approved:

```
Implement the tasks in openspec/changes/agentcore-gateway/tasks.md.
Work through them in order. Check each item off as you complete it.
Follow the decisions in design.md — do not deviate from them.
```

Keep `tasks.md` open in a split editor so you can watch the checkboxes fill in as Claude works. Claude will write files, run commands in the terminal, and show you test output.

---

## Referencing spec files explicitly

When you want Claude to focus on a specific file, type `@` and pick the file from the autocomplete:

```
Look at @openspec/changes/agentcore-gateway/design.md — is decision D3 consistent
with what we discussed?
```

Or drag a file from the Explorer panel into the chat to attach it.

---

## Iterating with colleagues (VS Code)

**Colleague reviews the spec:**

They open the PR in VS Code (via the **GitHub Pull Requests** extension) or just pull the branch:

```bash
git fetch origin
git checkout spec/agentcore-gateway
```

Open the spec files in the editor. To ask questions or suggest changes, they open Claude chat and type:

```
I'm reviewing the spec in openspec/changes/agentcore-gateway/.
I think D1 (Console creation) is risky — can you draft an alternative D1
using the AWS CLI so the creation is scriptable?
```

Claude proposes the edit. The colleague commits it to the branch — the PR updates automatically.

---

## Running OpenSpec slash commands from VS Code

You can run the same `/opsx` commands as the CLI — type them directly in the chat panel:

| What to type | What happens |
|---|---|
| `/opsx propose` | Claude starts the proposal wizard |
| `/opsx explore` | Claude reads the repo for context |
| `/opsx sync` | Claude regenerates specs from design |
| `/opsx apply` | Claude implements tasks.md |
| `/opsx archive` | Claude archives the completed change |

---

## Tips

- **Split editor + chat** — keep the spec file open on the left, Claude chat on the right. You can read and comment without switching windows.
- **Inline edits are immediate** — Claude edits files in your working directory. You see the unsaved change in the editor gutter before it is saved.
- **Terminal is shared** — when Claude runs `sam deploy` or `pytest`, the output appears in the VS Code terminal. You can scroll through it or copy error messages and paste them into the chat.
- **Source control panel** — use the VS Code Git panel (`Ctrl+Shift+G`) to review staged changes before Claude commits.
- **New window for implementation** — when moving from spec to implementation, opening a fresh Claude chat (click the `+` in the chat panel header) clears accumulated spec-writing context so the agent focuses on code.
