# AI Heartbeat Observer

Target date: {target_date}
Knowledge base: {knowledge_base_path}
PRD: {prd_path}
Workspace root: {workspace_root}
Observations path: {observations_path}

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

Task:
1. If {observations_path} already contains `Date: {target_date}`, do not modify files and reply exactly `Entry for {target_date} already exists, skipping`.
2. Use {knowledge_base_path} as the operating SOP and {prd_path} as the product intent for what counts as a valuable observation.
3. Scan the recent, relevant workspace changes under {workspace_root}.
4. Append exactly one new observer entry to {observations_path} for {target_date}. The entry must begin with `Date: {target_date}`.
5. Use repo-relative paths whenever you mention files.
6. Only edit {observations_path}. Do not modify any file under `rules/` and do not perform reflector work.
7. Reply with a short walkthrough after the write completes.