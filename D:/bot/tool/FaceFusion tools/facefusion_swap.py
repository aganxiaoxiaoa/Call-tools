#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaceFusion 本地换脸调用脚本（用于 OpenClaw / Telegram 机器人）

功能概述：
1) 解析命令行参数（source / target / output / api-url / timeout）
2) 根据 FACE_LIBRARY 将 source 别名映射为真实图片路径
3) 检查 source 与 target 文件是否存在
4) 通过 requests.Session() 以 multipart/form-data 调用 FaceFusion API
5) 将 API 返回的二进制结果写入 output 文件
6) 成功时仅输出：MEDIA:file:///绝对路径
7) 失败时将错误写入 stderr，并以非 0 状态码退出

注意：
- 本脚本默认面向 Windows 路径，同时也兼容其他平台。
- 为避免日志污染，严禁直接打印 API 返回的二进制内容。
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

# 预置人脸库（可按需修改）
FACE_LIBRARY = {
    "me": r"D:\bot\faces\my_face.jpg",
    "zhangsan": r"D:\bot\faces\zhangsan.jpg",
}


def eprint(message: str) -> None:
    """将错误信息打印到 stderr（UTF-8 友好）。"""
    print(message, file=sys.stderr)


def to_file_uri(path: Path) -> str:
    """将本地绝对路径转换为 file URI，确保 Windows 路径可用。"""
    abs_path = path.resolve()
    # pathlib.Path.as_uri 对 Windows / POSIX 都可用（绝对路径前提）
    return abs_path.as_uri() if abs_path.is_absolute() else Path(os.path.abspath(abs_path)).as_uri()


def resolve_source(source_value: str) -> Path:
    """
    解析 --source：
    - 若命中 FACE_LIBRARY，则使用映射路径
    - 否则将 source_value 视为真实文件路径
    """
    mapped = FACE_LIBRARY.get(source_value, source_value)
    return Path(mapped)


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="调用本地 FaceFusion API (/api/face_swap) 进行换脸并输出 MEDIA URI"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="源人脸图片名称（FACE_LIBRARY 键）或图片文件路径",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="目标图片/视频路径（例如 OpenClaw 传入的 {{MediaPath}}）",
    )
    parser.add_argument(
        "--output",
        default=str(Path(tempfile.gettempdir()) / "swap_result.png"),
        help="输出文件路径，默认系统临时目录下的 swap_result.png",
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:7860/api/face_swap",
        help="FaceFusion API 地址，默认 http://localhost:7860/api/face_swap",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="请求超时时间（秒），默认 300",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # 延迟导入 requests：若未安装，给出明确安装提示
    try:
        import requests
    except ImportError:
        eprint("缺少依赖 requests，请先安装：pip install requests")
        return 2

    source_path = resolve_source(args.source)
    target_path = Path(args.target)
    output_path = Path(args.output)

    # 输入文件存在性检查
    if not source_path.exists() or not source_path.is_file():
        eprint(f"source 文件不存在或不可读: {source_path}")
        return 3

    if not target_path.exists() or not target_path.is_file():
        eprint(f"target 文件不存在或不可读: {target_path}")
        return 4

    # 确保输出目录存在（不修改原文件，仅写新文件）
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 使用二进制模式读取输入；通过 multipart/form-data 上传
    try:
        with requests.Session() as session:
            with source_path.open("rb") as src_fp, target_path.open("rb") as tgt_fp:
                files = {
                    # 字段名必须为 source / target
                    "source": (source_path.name, src_fp, "application/octet-stream"),
                    "target": (target_path.name, tgt_fp, "application/octet-stream"),
                }

                response = session.post(
                    args.api_url,
                    files=files,
                    timeout=args.timeout,
                )

            if response.status_code != 200:
                # 仅打印简要文本，避免输出大量内容
                snippet = (response.text or "")[:500]
                eprint(
                    f"FaceFusion API 返回非 200 状态码: {response.status_code}; 响应摘要: {snippet}"
                )
                return 5

            # 将返回二进制写入输出文件
            with output_path.open("wb") as out_fp:
                out_fp.write(response.content)

    except requests.exceptions.RequestException as exc:
        eprint(f"请求 FaceFusion API 失败: {exc}")
        return 6
    except OSError as exc:
        eprint(f"文件读写失败: {exc}")
        return 7

    # 成功时 stdout 只能输出这一行
    print(f"MEDIA:{to_file_uri(output_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
