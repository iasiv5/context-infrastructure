#!/usr/bin/env python3
"""
L2 Reflector Agent (Trigger Script)
Instructs OpenCode-Builder to perform memory garbage collection directly on the file.
"""
import os
import sys
from datetime import datetime
import heartbeat_state

KNOWLEDGE_BASE = "/path/to/your/workspace/periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md"

PROMPT_TEMPLATE = """
执行记忆系统的"反思与晋升"任务。

SOP: {kb_path}

步骤：
1. 读取 /contexts/memory/OBSERVATIONS.md，分析 🔴 和高优 🟡 条目
2. 将具有普适性的内容晋升到 rules/，按职责边界分类：
   - SOUL.md: Agent 身份与核心价值观
   - USER.md: 用户画像与人生哲学
   - COMMUNICATION.md: 沟通风格（仅限沟通，不含技术知识）
   - WORKSPACE.md: 目录路由
   - skills/: 技术方法论、工作流、最佳实践
3. GC：重写 OBSERVATIONS.md，删除已晋升及过期 🟢 记录

晋升门槛：跨项目通用 + 多次验证 + 有明确适用场景
完成后回复简短晋升汇报。
"""

def main():
    import argparse
    parser = argparse.ArgumentParser(description='L2 Reflector Agent')
    parser.add_argument('--model', default='<your-model-id>',
                        choices=['<your-model-id>'],
                        help='Model ID to use')
    args = parser.parse_args()
    
    model_id = args.model
    target_date = datetime.now().strftime("%Y-%m-%d")

    try:
        print(f"Triggering Fully Agentic Reflector using model: {model_id}...")
        from opencode_client import OpenCodeClient

        client = OpenCodeClient()

        session_id = client.create_session(f"Heartbeat L2 Reflector - {target_date}")
        if not session_id:
            heartbeat_state.persist_failure(
                "reflector",
                error="Failed to create OpenCode session.",
                target_date=target_date,
            )
            return

        prompt = PROMPT_TEMPLATE.format(kb_path=KNOWLEDGE_BASE)
        client.send_message(session_id, prompt, model_id=model_id)
        # If send_message timed out, agent may still be running; poll until done
        print("Waiting for session to complete (sync mode)...")
        completed = client.wait_for_session_complete(session_id)
        if not completed:
            heartbeat_state.persist_failure(
                "reflector",
                error="Reflector session did not complete before timeout.",
                target_date=target_date,
            )
            return

        heartbeat_state.persist_success("reflector", target_date=target_date)
        print(f"Task complete (Session: {session_id}).")
    except Exception as exc:
        heartbeat_state.persist_failure("reflector", error=str(exc), target_date=target_date)
        print(f"Reflector failed: {exc}")

if __name__ == "__main__":
    main()
