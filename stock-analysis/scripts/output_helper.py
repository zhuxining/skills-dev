"""输出路径处理工具

统一管理所有脚本的输出路径, 确保输出文件都在项目根目录的 output/ 文件夹中。

Functions:
  - resolve_output_path: 解析输出路径, 统一输出到 output/ 文件夹
  - get_output_dir: 获取 output 目录的绝对路径

Usage:
  from output_helper import resolve_output_path

  output_path = resolve_output_path("data.csv")
  df.to_csv(output_path)
"""

from pathlib import Path


def get_output_dir() -> Path:
    """获取项目根目录下的 output 文件夹路径。

    Returns:
        output 目录的绝对路径
    """
    # 脚本在 stock-analysis/scripts/ 目录, 项目根目录是上上级
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "output"

    # 确保 output 目录存在
    output_dir.mkdir(exist_ok=True)

    return output_dir


def resolve_output_path(filename: str) -> Path:
    """解析输出路径, 统一输出到项目根目录的 output/ 文件夹。

    所有输出都强制在 output/ 文件夹下, 如果 filename 包含路径分隔符,
    会创建相应的子目录结构。

    Args:
        filename: 输出文件名或相对路径 (如 "data.csv" 或 "stocks/700.hk.csv")

    Returns:
        解析后的绝对路径, 位于 output/ 文件夹下

    Examples:
        >>> resolve_output_path("data.csv")
        PosixPath('/path/to/project/output/data.csv')

        >>> resolve_output_path("stocks/700.hk.csv")
        PosixPath('/path/to/project/output/stocks/700.hk.csv')
    """
    output_dir = get_output_dir()
    output_path = output_dir / filename

    # 确保父目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path


__all__ = ["get_output_dir", "resolve_output_path"]
