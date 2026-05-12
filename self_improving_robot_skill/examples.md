py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" --help
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-plan --request "创建一个测试用 hello world Python CLI 工具" --tool-name "hello_world_tool" --language python
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建一个测试用 hello world Python CLI 工具，支持 --name 参数，输出 Hello name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-check --path "D:\bot\tool\hello_world_tool"
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" create-skill --name "hello_world_skill" --request "创建一个 Hello World OpenClaw Skill，支持 Telegram 调用" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" skill-health
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" export-system-context
