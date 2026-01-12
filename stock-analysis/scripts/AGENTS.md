# Agent Instructions for scripts

This file provides guidance to Agents when working in `/scripts` for creating Python scripts.

## PEP 723 – Inline script metadata

All Python scripts in this repository MUST follow PEP 723 for inline script metadata. This ensures scripts are self-contained with explicit dependency declarations.

### Required Format

Every script must include a metadata block immediately after the shebang:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "longport>=3.0.18",
# ]
# ///

"""Brief script description.

Usage:
    uv run script_name.py <arguments>
"""
```

### Key Rules

1. **Placement**: Metadata block must appear before any code, after shebang
2. **Syntax**: Use `# /// script` and `# ///` delimiters (TOML format inside)
3. **Dependencies**: List all external packages with version constraints
4. **Python version**: Specify minimum Python version (use `>=3.14` unless specific features needed)
5. **Executable**: Make scripts executable with `chmod +x script.py`

## Documentation Standards

### Module Docstrings

Every script must have a comprehensive module docstring:

```python
"""Brief one-line description.

More detailed description if needed. Explain what the script does,
not how it does it.

Usage:
    uv run script_name.py <arguments>
    uv run script_name.py --help

Args:
    arg1: Description of argument
    arg2: Description of argument

Examples:
    uv run script_name.py value1 value2
    uv run script_name.py --option value
"""
```

### Function Docstrings

Keep function docstrings concise yet informative:

```python
def process_data(data: list[str], threshold: float) -> dict:
    """Process data items above threshold.

    Args:
        data: List of data items to process
        threshold: Minimum value for filtering

    Returns:
        Dictionary with processed results
    """
```

**Rules:**
- One-line summary for simple functions
- Multi-line for complex functions (summary + Args + Returns)
- Avoid obvious descriptions (e.g., "Returns the result" is redundant)
- Focus on **what** and **why**, not **how**

## Error Handling

Follow these strict error handling rules:

### Rules

1. **Catch broad exceptions** - Use `Exception`, no custom exception classes
2. **Print user-friendly messages** - Include context about what failed
3. **Return pattern**:
   - `None` on error, valid value on success
   - Or `(bool, str)` tuple: `(status, error_message)`
4. **No raising to caller** - Handle all errors locally
5. **Early returns** - Check error conditions first

### Examples

**Simple function:**
```python
def fetch_data(url: str) -> dict | None:
    """Fetch data from API endpoint."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"✗ 获取数据失败: {e}", file=sys.stderr)
        return None
```

**Validation function:**
```python
def validate_symbol(symbol: str) -> tuple[bool, str]:
    """Validate stock symbol format."""
    if not symbol:
        return False, "符号不能为空"
    if not symbol.replace(".", "").replace("-", "").isalnum():
        return False, f"符号格式无效: {symbol}"
    return True, ""
```

**Main function:**
```python
def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Script description")
    parser.add_argument("symbol", help="Stock symbol")
    args = parser.parse_args()

    # Validate early
    valid, msg = validate_symbol(args.symbol)
    if not valid:
        print(f"✗ {msg}", file=sys.stderr)
        sys.exit(1)

    # Process
    result = fetch_data(args.symbol)
    if result is None:
        sys.exit(1)

    print(f"✓ 处理完成: {len(result)} 条记录")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✗ 用户中断", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"✗ 未预期错误: {e}", file=sys.stderr)
        sys.exit(1)
```

## Output Formatting

Use consistent output indicators:

- `✓` - Success messages (green when terminal supports colors)
- `✗` - Error messages (red when terminal supports colors)
- Clear, actionable messages in Chinese or English consistently

**Good:**
```python
print(f"✓ 数据已保存: {filename} ({len(data)} 行)")
print(f"✗ 文件不存在: {filepath}")
```

**Bad:**
```python
print("done")  # Too vague
print("ERROR!!!")  # No context
```

## Script Execution with uv

All scripts should be executed using `uv run`:

```bash
# Run a script
uv run scripts/script_name.py args

# From scripts directory
cd scripts
uv run script_name.py args
```

**Benefits:**
- Automatic dependency installation from PEP 723 metadata
- Isolated environments per script
- Fast dependency resolution
- Reproducible execution

## Complete Script Template

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "longport>=3.0.18",
# ]
# ///

"""Brief description of script purpose.

Longer description if needed. Explain use cases and behavior.

Usage:
    uv run script_name.py <arguments>
    uv run script_name.py --help

Args:
    arg1: Description of first argument
    arg2: Description of second argument

Examples:
    uv run script_name.py value1
    uv run script_name.py --option value
"""

import argparse
import sys
from pathlib import Path


def process_item(item: str) -> dict | None:
    """Process a single item.

    Args:
        item: Item to process

    Returns:
        Processed result dictionary, or None on error
    """
    try:
        # Processing logic here
        return {"item": item, "status": "processed"}
    except Exception as e:
        print(f"✗ 处理失败 ({item}): {e}", file=sys.stderr)
        return None


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Script description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input", help="Input value")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    # Validate inputs
    if not args.input:
        print("✗ 输入不能为空", file=sys.stderr)
        sys.exit(1)

    # Process
    result = process_item(args.input)
    if result is None:
        sys.exit(1)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(str(result))
        print(f"✓ 已保存: {output_path}")
    else:
        print(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n✗ 用户中断", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"✗ 错误: {e}", file=sys.stderr)
        sys.exit(1)
```

## Best Practices

1. **PEP 723 metadata** - Required for all scripts, no exceptions
2. **Version constraints** - Use `>=` for minimum versions (e.g., `requests>=2.31.0`)
3. **Execute with uv run** - Never use `python3` directly
4. **Executable permissions** - `chmod +x script.py` for all scripts
5. **Comprehensive docstrings** - Module and function level, with usage examples
6. **Robust error handling** - Catch all exceptions, return None/tuple patterns
7. **User-friendly output** - Use `✓`/`✗` indicators, clear messages
8. **Early validation** - Check inputs before processing
9. **Type hints** - Use for function signatures (args and return types)
10. **Consistent formatting** - Follow script template structure 