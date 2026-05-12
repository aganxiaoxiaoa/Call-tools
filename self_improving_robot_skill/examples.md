py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" init-store
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-plan --request "创建测试工具" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-generate --plan-file "D:\bot\store\05_workflows\code_plans\code_plan_xxx.json" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-check --path "D:\bot\tool\hello_world_tool"
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-fix --check-report "D:\bot\store\07_outputs\maintenance\code_check_xxx.json" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" code-cycle --request "创建一个测试用 hello world Python CLI 工具，支持 --name 参数，输出 Hello name" --target-dir "D:\bot\tool\hello_world_tool" --tool-name "hello_world_tool" --language python --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" create-skill --name "hello_world_skill" --request "创建 Hello World Skill" --yes
py "D:\bot\tool\self_improving_robot_skill\self_improving_robot.py" skill-health
