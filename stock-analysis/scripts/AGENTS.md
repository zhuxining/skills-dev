# Agent Instructions for scripts

This file provides guidance to Agents when creating Python scripts in `/scripts`.

## PEP 723 – Inline script metadata

All Python scripts MUST include PEP 723 metadata block after the shebang:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "longport>=3.0.18",
#     "pandas>=2.3.3",
# ]
# ///

"""One-line description. Longer description if needed.

Usage:
    uv run script_name.py --help
"""
```

**Key Rules:**
1. Metadata must appear before any code
2. Use `# /// script` and `# ///` delimiters (TOML format inside)
3. List ALL external dependencies with version constraints (`>=` minimum version)
4. Specify Python version (use `>=3.14` default)

### Recommended Dependencies

```toml
"longport>=3.0.18",      # LongPort OpenAPI SDK
"akshare>=1.18.9",        # Alternative data source
"ta-lib>=0.6.8",          # TA-Lib technical analysis
"pandas>=2.3.3",          # Data manipulation
"numpy>=2.4.1",           # Numerical computing
```

## Documentation Standards

**Module Docstring:**
```python
"""Brief description explaining what the script does.

Usage:
    uv run script_name.py --input value
    uv run script_name.py --help
"""
```

**Function Docstring:**
```python
def process_data(data: list, threshold: float) -> dict | None:
    """Brief description.
    
    Args:
        data: Input data list
        threshold: Minimum threshold value
    
    Returns:
        Processed result or None on error
    """
```

**Rules:** One-line for simple functions, multi-line (summary + Args + Returns) for complex ones. Focus on **what** not **how**.

## Error Handling

**Rules:**
1. Catch broad exceptions: `except Exception as e:`
2. Print user-friendly messages to stderr
3. Return `None` on error, valid value on success
4. For validation: return `(bool, str)` tuple
5. No raising exceptions to caller—handle locally

**Example:**
```python
def fetch_data(url: str) -> dict | None:
    """Fetch data from API."""
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"✗ 获取数据失败: {e}", file=sys.stderr)
        return None
```

## Output Formatting

Use consistent indicators:
- `✓` - Success (file saved, processing completed)
- `✗` - Error (with context)

```python
print(f"✓ 已保存: output/data.csv (100 行, 50.2 KB)")
print(f"✗ 文件不存在: {filepath}", file=sys.stderr)
```

## Input/Output Standards

### Input

**Command-line Arguments:**
```python
parser.add_argument("--symbol", required=True, help="Stock symbol (e.g., 700.HK)")
parser.add_argument("--period", default="day", help="Period (default: day)")
parser.add_argument("--output", help="Output filename (saves to output/ folder)")
```

**Rules:** Required args for critical inputs, optional with defaults for config, validate early.

### Output

**Directory Convention:**
- Results: `output/` (CSV, JSON, reports)
- Test data: `input/` (sample files)
- Logs: `output/logs/`

**File Export Pattern:**
```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if args.output:
    output_path = OUTPUT_DIR / args.output
    df.to_csv(output_path, index=False)
    size_kb = output_path.stat().st_size / 1024
    print(f"✓ 已保存: output/{args.output} ({len(df)} 行, {size_kb:.1f} KB)")
else:
    print(df.head())
    print(f"总行数: {len(df)}")
```

**Data Format:**
- CSV: UTF-8, headers, ISO 8601 dates, 2-4 decimals
- JSON: snake_case keys, ISO 8601 dates, with metadata
- Console: aligned columns, include units

### Output Examples

```bash
# File export
uv run scripts/longport_candlesticks.py --symbol 700.HK --period day --output 700.csv
✓ 已保存: output/700.csv (100 行, 45.2 KB)

# Console preview
uv run scripts/longport_candlesticks.py --symbol 700.HK --period day
              open    high     low   close   volume
datetime
2024-01-02    ...
总行数: 100
```

## Quick Checklist

- [ ] PEP 723 metadata block present
- [ ] All dependencies listed with versions
- [ ] Module and function docstrings complete
- [ ] Error handling: try/except with user messages
- [ ] `--output` saves to `output/` folder with size info
- [ ] Console output includes summary (row count, columns)
- [ ] Use `✓` for success, `✗` for errors
- [ ] Execute with `uv run scripts/script_name.py` 