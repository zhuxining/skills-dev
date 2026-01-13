#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "longport>=3.0.18",
# ]
# ///

"""LongPort 自选分组命令行管理工具。

支持分组的增删改查及成员批量导出功能。

Usage:
    uv run longport_groups.py list
    uv run longport_groups.py create --name my_group --symbols 700.HK,AAPL.US
    uv run longport_groups.py update --id 4038104 --add-symbols 000001.SZ
    uv run longport_groups.py get-symbols --id 4038104
    uv run longport_groups.py delete --id 4038104

Commands:
    list: 列出所有分组
    create: 创建新分组
    update: 更新分组成员(增/删/替换)
    get-symbols: 导出分组成员列表
    delete: 清空分组

Examples:
    uv run longport_groups.py list
    uv run longport_groups.py create --name "科技股" --symbols AAPL.US,MSFT.US
    uv run longport_groups.py update --id 4038104 --add-symbols 700.HK,9988.HK
    uv run longport_groups.py get-symbols --id 4038104 --output symbols.txt
"""

import argparse
from collections.abc import Iterator
from contextlib import contextmanager
import sys

from longport.openapi import Config, QuoteContext, SecuritiesUpdateMode

from _output_helper import resolve_output_path


@contextmanager
def open_quote_ctx() -> Iterator[QuoteContext]:
    """从 .env 初始化 QuoteContext 并自动关闭。"""
    ctx = QuoteContext(Config.from_env())
    try:
        yield ctx
    finally:
        close_fn = getattr(ctx, "close", None)
        if callable(close_fn):
            close_fn()


def list_groups(args: argparse.Namespace) -> None:
    """列出所有分组。"""
    with open_quote_ctx() as ctx:
        groups = ctx.watchlist()
        if not groups:
            print("无分组")
            return
        print(f"{'ID':<8} {'Name':<30} {'Count':<10}")
        print("-" * 50)
        for g in groups:
            name = g.name[:28] if len(g.name) > 28 else g.name
            print(f"{g.id:<8} {name:<30} {len(g.securities):<10}")


def create_group(args: argparse.Namespace) -> None:
    """创建新分组。

    Args:
        args: 包含 name 和可选 symbols 参数的命名空间
    """
    symbols = None
    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]

    with open_quote_ctx() as ctx:
        group_id = ctx.create_watchlist_group(name=args.name, securities=symbols)

    count = len(symbols) if symbols else 0
    print(f"✓ 分组已创建: ID={group_id}, Name={args.name}, Count={count}")


def update_group(args: argparse.Namespace) -> None:
    """更新分组成员(增/删/替换)。

    Args:
        args: 包含 id 和操作参数的命名空间
    """
    # 确定更新模式
    mode = SecuritiesUpdateMode.Add
    if args.remove_symbols:
        mode = SecuritiesUpdateMode.Remove
    elif args.replace_symbols:
        mode = SecuritiesUpdateMode.Replace

    # 解析符号列表
    symbols = None
    if args.add_symbols:
        symbols = [s.strip() for s in args.add_symbols.split(",") if s.strip()]
    elif args.remove_symbols:
        symbols = [s.strip() for s in args.remove_symbols.split(",") if s.strip()]
    elif args.replace_symbols:
        symbols = [s.strip() for s in args.replace_symbols.split(",") if s.strip()]

    if symbols is None:
        print(
            "✗ 错误: 需要 --add-symbols 或 --remove-symbols 或 --replace-symbols", file=sys.stderr
        )
        sys.exit(1)

    with open_quote_ctx() as ctx:
        ctx.update_watchlist_group(args.id, securities=symbols, mode=mode)
        groups = ctx.watchlist()
        updated = next((g for g in groups if g.id == args.id), None)

        if updated is None:
            print(f"✗ 错误: 分组不存在 (ID={args.id})", file=sys.stderr)
            sys.exit(1)
        else:
            print(
                f"✓ 分组已更新: ID={args.id}, Name={updated.name}, Count={len(updated.securities)}"
            )


def get_symbols(args: argparse.Namespace) -> None:
    """导出分组成员列表。

    Args:
        args: 包含 id 和可选 output 参数的命名空间
    """
    with open_quote_ctx() as ctx:
        groups = ctx.watchlist()
        group = next((g for g in groups if g.id == args.id), None)

        if group is None:
            print(f"✗ 错误: 分组不存在 (ID={args.id})", file=sys.stderr)
            sys.exit(1)
        else:
            symbols = [s.symbol for s in group.securities]

    if not symbols:
        print("分组为空")
        return

    if args.output:
        output_path = resolve_output_path(args.output)
        output_path.write_text("\n".join(symbols) + "\n")
        print(f"✓ 已保存: {output_path} ({len(symbols)} 个符号)")
    else:
        print("\n".join(symbols))


def delete_group(args: argparse.Namespace) -> None:
    """清空分组(替换为空列表)。

    Args:
        args: 包含 id 参数的命名空间
    """
    with open_quote_ctx() as ctx:
        groups = ctx.watchlist()
        group = next((g for g in groups if g.id == args.id), None)

        if group is None:
            print(f"✗ 错误: 分组不存在 (ID={args.id})", file=sys.stderr)
            sys.exit(1)
        else:
            ctx.update_watchlist_group(args.id, securities=[], mode=SecuritiesUpdateMode.Replace)
            print(f"✓ 分组已清空: ID={args.id}, Name={group.name}")


def main() -> None:
    """主入口函数。"""
    parser = argparse.ArgumentParser(
        description="LongPort 自选分组管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # list
    subparsers.add_parser("list", help="列出所有分组")

    # create
    create_p = subparsers.add_parser("create", help="创建新分组")
    create_p.add_argument("--name", required=True, help="分组名称")
    create_p.add_argument("--symbols", help="初始成员,逗号分隔,如 700.HK,AAPL.US")

    # update
    update_p = subparsers.add_parser("update", help="更新分组成员")
    update_p.add_argument("--id", type=int, required=True, help="分组 ID")
    update_p.add_argument("--add-symbols", help="增加成员,逗号分隔")
    update_p.add_argument("--remove-symbols", help="删除成员,逗号分隔")
    update_p.add_argument("--replace-symbols", help="替换全部成员,逗号分隔")

    # get-symbols
    get_p = subparsers.add_parser("get-symbols", help="导出分组成员")
    get_p.add_argument("--id", type=int, required=True, help="分组 ID")
    get_p.add_argument(
        "--output", help="输出文件名(逐行一个符号), 保存在 output/ 文件夹; 不填则打印到 stdout"
    )

    # delete
    delete_p = subparsers.add_parser("delete", help="清空分组")
    delete_p.add_argument("--id", type=int, required=True, help="分组 ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 路由到对应的处理函数
    handlers = {
        "list": list_groups,
        "create": create_group,
        "update": update_group,
        "get-symbols": get_symbols,
        "delete": delete_group,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"✗ 未知命令: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✗ 用户中断", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"✗ 未预期错误: {e}", file=sys.stderr)
        sys.exit(1)
