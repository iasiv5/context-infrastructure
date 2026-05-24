# AI Heartbeat Reflector

Target date: {target_date}
Knowledge base: {knowledge_base_path}
PRD: {prd_path}
Workspace root: {workspace_root}
Observations path: {observations_path}
Reflector report path: {report_path}

Read these files before doing any write:
- {agents_path}
- {claude_md_path}
- {knowledge_base_path}
- {prd_path}
- {soul_path}
- {user_path}
- {workspace_rules_path}
- {communication_path}
- {observations_path}

Allowlist:
{allowlist_paths}

Promotion routing:
- Promote durable identity or operating rules into {soul_path}, {user_path}, {communication_path}, or {workspace_rules_path} when they clearly belong there.
- For skill-specific durable guidance, you may update an existing real skill doc under rules/skills/ or create a new real skill doc under rules/skills/ when no existing skill is the right home.
- Before creating or rewriting a real skill doc, read rules/skills/bestpractice_skill_writing.md. Define the skill around goals, acceptance criteria, available resources, and output shape rather than a mechanical checklist.
- Use the naming convention `<category>_<name>.md`, for example `workflow_my_process.md` or `bestpractice_my_insight.md`.
- If you touch any real skill doc under rules/skills/, you must also update rules/skills/INDEX.md.

Task:
1. Use {knowledge_base_path} as the execution SOP and {prd_path} as the product boundary for what should be promoted or garbage-collected.
2. Review {observations_path} and decide which durable rules should be promoted.
3. Only modify files that appear in the allowlist above.
4. Promote durable rules into the correct real rules target instead of a temporary staging file.
5. Garbage-collect {observations_path} when entries are obsolete or have already been promoted, and record the exact removals in `## Garbage-Collected Entries` so the runner can verify them.
6. Write {report_path} with these required fields:
   - `Date: {target_date}`
   - `## Touched Files`
   - one repo-relative bullet for each touched allowlist file using only the bare path
   - each touched-file bullet must be exactly `- path/to/file.ext`
   - do not wrap touched-file paths in backticks
   - do not append descriptions, reasons, punctuation, or commentary on the same line
   - `## Garbage-Collected Entries`
   - one bullet for each removed observation line or fully removed date block
   - each GC bullet must be either the full removed observation line or exactly `Date: YYYY-MM-DD`
7. Do not modify any path outside the allowlist, and do not omit the report.
8. Reply with a short walkthrough after the writes complete.