# Safe dry-run first
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-plan --request "create hello world test tool" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-generate --plan-file "D:\bot\store\05_workflows\code_plans\code_plan_xxx.json" --dry-run
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-check --path "D:\bot\tool\hello_world_tool"

# Confirmed write examples
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-generate --plan-file "D:\bot\store\05_workflows\code_plans\code_plan_xxx.json" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建一个测试用 hello world Python CLI 工具，支持 --name 参数，输出 Hello name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" create-skill --name "hello_world_skill" --request "创建 Hello World OpenClaw Skill" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" registry-audit
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" skill-health
