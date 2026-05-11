# FACEFUSION_SKILL

## 触发意图（Telegram）
当用户表达以下意图时，优先调用 FaceFusion 本地换脸：

- 换脸
- 用 me 换脸
- 把这张图换成 me
- FaceFusion 换脸
- 对这张图片做人脸替换

## 默认调用命令
```bash
python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source me --target "{{MediaPath}}"
```

## 用户指定 source 别名时
例如用户说“用 zhangsan 换脸”，调用：

```bash
python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source zhangsan --target "{{MediaPath}}"
```

## 安全规则
- 默认只处理用户明确发送的图片或视频。
- 不要修改原文件。
- 输出文件保存到系统临时目录，或 `D:\bot\outputs\facefusion`。
- 成功结果必须返回：`MEDIA:file:///...`。
- 若 FaceFusion 未启动，提示先运行：

```bash
python facefusion.py --headless --open-browser false
```
