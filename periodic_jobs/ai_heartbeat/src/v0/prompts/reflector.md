# AI Heartbeat Reflector

Target date: {target_date}
Knowledge base: {knowledge_base_path}
PRD: {prd_path}
Workspace root: {workspace_root}
Observations path: {observations_path}
Rules promotion path: {rules_promotion_path}
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

Task:
1. Use {knowledge_base_path} as the execution SOP and {prd_path} as the product boundary for what should be promoted or garbage-collected.
2. Review {observations_path} and decide which durable rules should be promoted.
3. Only modify files that appear in the allowlist above.
4. Update {rules_promotion_path} only when a durable promotion is justified.
5. Garbage-collect {observations_path} when entries are obsolete or have already been promoted.
6. Write {report_path} with these required fields:
   - `Date: {target_date}`
   - `## Touched Files`
   - one repo-relative bullet for each touched allowlist file using only the bare path
   - each touched-file bullet must be exactly `- path/to/file.ext`
   - do not wrap touched-file paths in backticks
   - do not append descriptions, reasons, punctuation, or commentary on the same line
7. Do not modify any path outside the allowlist, and do not omit the report.
8. Reply with a short walkthrough after the writes complete.