# PR Branch Policy Rule

This rule ensures that all Pull Requests (PRs) or merges are targeted towards the `development` branch by default.

## Policy
1. All Pull Requests must be raised against the `development` branch.
2. The agent must never target `main`, `master`, or any other branch for automated PR creation or merge suggestions unless the user explicitly specifies a different target branch in the current request.
3. If the agent is about to suggest a PR, it should confirm (or state) that the target branch is `development`.

## Application
- Applied when suggesting git commands for PR creation (e.g., `gh pr create`).
- Applied when suggesting merge strategies.
- Applied when performing automated git operations.
