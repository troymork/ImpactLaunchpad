#!/bin/bash

echo "🧠 Launching Oracle Agents..."

function launch_agent() {
  AGENT_PATH=$1
  AGENT_NAME=$2
  echo "🚀 Launching $AGENT_NAME..."
  osascript <<EOF
tell application "Terminal"
    do script "cd ~/ImpactLaunchpad/meeting-oracle && source ../.venv/bin/activate && python $AGENT_PATH"
end tell
EOF
  sleep 2
}

launch_agent "scripts/task_watcher.py" "Task Watcher"
launch_agent "scripts/git_auto_push_agent.py" "Git Auto Push"
launch_agent "scripts/extract_action_items_agent.py" "Action Items"
launch_agent "scripts/extract_quotes_agent.py" "Quote Extractor"
launch_agent "scripts/generate_insights_agent.py" "Insight Generator"

echo "✅ All agents launched safely."
