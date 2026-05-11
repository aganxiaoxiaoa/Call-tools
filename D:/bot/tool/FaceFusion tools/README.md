# FaceFusion OpenClaw Skill（Windows 本地）

## 1) 安装依赖

```bash
pip install requests
```

## 2) 启动 FaceFusion（headless）

确保本地 API 可访问：`http://localhost:7860/api/face_swap`

```bash
python facefusion.py --headless --open-browser false
```

## 3) 配置 FACE_LIBRARY

编辑 `facefusion_swap.py` 中的 `FACE_LIBRARY`：

```python
FACE_LIBRARY = {
    "me": r"D:\bot\faces\my_face.jpg",
    "zhangsan": r"D:\bot\faces\zhangsan.jpg",
}
```

- 当 `--source me` 时会自动映射到 `D:\bot\faces\my_face.jpg`。
- 若 `--source` 不在字典中，则按真实路径处理。

## 4) 手动测试命令

### 使用别名（推荐）
```bash
python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source me --target "D:\test\target.jpg"
```

### 使用 source 真实路径
```bash
python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source "D:\faces\another.jpg" --target "D:\test\target.jpg"
```

### 指定输出路径
```bash
python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source me --target "D:\test\target.jpg" --output "D:\bot\outputs\facefusion\result.png"
```

## 5) Telegram 调用示例

- 用户说：“换脸” / “用 me 换脸”
  - 调用：
  ```bash
  python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source me --target "{{MediaPath}}"
  ```

- 用户说：“用 zhangsan 换脸”
  - 调用：
  ```bash
  python "D:\bot\tool\FaceFusion tools\facefusion_swap.py" --source zhangsan --target "{{MediaPath}}"
  ```

成功后脚本标准输出仅一行：

```text
MEDIA:file:///绝对路径
```

## 6) 常见错误排查

1. **连接失败 / 端口不通**
   - 确认 FaceFusion 已启动。
   - 确认 `http://localhost:7860` 可访问。

2. **source 不存在**
   - 检查 `FACE_LIBRARY` 映射路径是否正确。
   - 或检查 `--source` 直接路径是否存在。

3. **target 不存在**
   - 确认 OpenClaw 传入的 `{{MediaPath}}` 指向真实文件。

4. **API 返回非 200**
   - 查看 stderr 中的状态码与响应摘要。
   - 检查 FaceFusion 输入格式是否满足当前模型配置。

5. **缺少 requests**
   - 安装：`pip install requests`
