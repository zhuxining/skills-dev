# 自选清单管理指南

自选清单（Watchlist Groups）是组织股票符号的便捷方式，在 LongPort 中以"分组"的形式存在。本文档介绍如何创建、管理和导出自选清单。

## 核心概念

**自选分组**: LongPort 提供的分组功能，允许用户将感兴趣的股票符号组织到不同的分组中（如"科技股"、"金融股"等）。

**工作流**:
```
创建分组 → 添加/删除成员 → 导出成员列表 → 用于数据获取
```

## 命令行接口

### longport_groups.py 使用手册

脚本位置: `stock-analysis/scripts/longport_groups.py`

#### 列出所有分组

```bash
uv run stock-analysis/scripts/longport_groups.py list
```

**输出格式**:
```
┌─────────────┬────────────┬──────────────┐
│ Group ID    │ Group Name │ Member Count │
├─────────────┼────────────┼──────────────┤
│ 4038104     │ 科技股     │ 5            │
│ 4038105     │ 金融股     │ 3            │
│ 4038106     │ 美股龙头   │ 4            │
└─────────────┴────────────┴──────────────┘
```

每一行代表一个分组，包含：
- **Group ID**: 分组的唯一标识符，用于后续操作
- **Group Name**: 分组的名称（用户定义）
- **Member Count**: 当前分组中包含的股票数量

---

#### 创建新分组

```bash
uv run stock-analysis/scripts/longport_groups.py create \
    --name "分组名称" \
    --symbols SYMBOL1.US,SYMBOL2.HK
```

**参数**:
- `--name` (必需): 分组的名称，任意字符串
- `--symbols` (可选): 初始股票符号，多个符号用逗号分隔。如果不指定，创建的分组为空

**示例**:
```bash
# 创建空分组
uv run stock-analysis/scripts/longport_groups.py create --name "新分组"

# 创建分组并初始化成员
uv run stock-analysis/scripts/longport_groups.py create \
    --name "科技股" \
    --symbols 700.HK,9988.HK,AAPL.US,MSFT.US,NVDA.US
```

**输出**: 成功创建提示及新分组的 ID（用于后续操作）

---

#### 添加/删除/替换分组成员

```bash
uv run stock-analysis/scripts/longport_groups.py update \
    --id GROUP_ID \
    --add-symbols SYMBOL1,SYMBOL2 \
    --remove-symbols SYMBOL3 \
    --symbols SYMBOL4,SYMBOL5
```

**参数**:
- `--id` (必需): 分组 ID，从 `list` 命令获得
- `--add-symbols` (可选): 添加新成员，多个符号用逗号分隔
- `--remove-symbols` (可选): 删除现有成员，多个符号用逗号分隔
- `--symbols` (可选): 替换所有成员（覆盖现有列表）

**示例**:
```bash
# 添加股票到分组 4038104
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038104 \
    --add-symbols 0700.HK,TSLA.US

# 删除分组中的股票
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038104 \
    --remove-symbols AAPL.US

# 替换分组的所有成员
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038104 \
    --symbols MSFT.US,GOOGL.US,NVDA.US
```

---

#### 导出分组成员

```bash
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id GROUP_ID \
    --output OUTPUT_FILE
```

**参数**:
- `--id` (必需): 分组 ID
- `--output` (可选): 输出文件路径。如果不指定，直接打印到控制台

**输出格式**: 纯文本，一行一个符号

**示例**:
```bash
# 打印到控制台
uv run stock-analysis/scripts/longport_groups.py get-symbols --id 4038104

# 输出示例:
# 700.HK
# 9988.HK
# AAPL.US
# MSFT.US
# NVDA.US

# 保存到文件
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id 4038104 \
    --output output/tech_stocks.txt
```

**后续使用**: 导出的文件可以在 bash 循环中使用（见 candlesticks_guide.md 的批量获取示例）

```bash
for symbol in $(cat output/tech_stocks.txt); do
    # 为每只股票获取数据
    echo "Processing $symbol"
done
```

---

#### 删除分组

```bash
uv run stock-analysis/scripts/longport_groups.py delete --id GROUP_ID
```

**参数**:
- `--id` (必需): 分组 ID

**效果**: 清空分组的所有成员。分组本身在 LongPort 中可能仍然存在，但处于空状态。

---

## 常见工作流

### 工作流 1: 创建并维护监视清单

```bash
# 1. 创建分组
uv run stock-analysis/scripts/longport_groups.py create \
    --name "重点跟踪"

# 2. 记下返回的 Group ID，假设为 4038107

# 3. 添加第一批股票
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038107 \
    --add-symbols 700.HK,AAPL.US,TSLA.US

# 4. 后续添加更多股票
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038107 \
    --add-symbols MSFT.US,9988.HK

# 5. 删除不需要的股票
uv run stock-analysis/scripts/longport_groups.py update \
    --id 4038107 \
    --remove-symbols TSLA.US

# 6. 查看最终结果
uv run stock-analysis/scripts/longport_groups.py get-symbols --id 4038107
```

### 工作流 2: 导出清单供数据获取

```bash
# 1. 列出所有分组
uv run stock-analysis/scripts/longport_groups.py list

# 2. 选择需要的分组，导出成员
uv run stock-analysis/scripts/longport_groups.py get-symbols \
    --id 4038104 \
    --output symbols.txt

# 3. 使用导出的符号进行后续数据获取（见 candlesticks_guide.md）
```

---

## 股票符号格式

LongPort 使用标准化的股票符号格式：

| 市场 | 格式示例 | 说明 |
|------|--------|------|
| 香港联交所 | `700.HK` | 腾讯控股 |
| 深圳证券交易所 | `000001.SZ` | 平安银行 |
| 上海证券交易所 | `600000.SH` | 浦发银行 |
| 纳斯达克 | `AAPL.US` | 苹果 |
| 纽约证券交易所 | `BRK.US` | 伯克希尔哈撒韦 |

**重要**: 确保符号格式正确，否则添加会失败。

---

## 错误处理

| 错误信息 | 原因 | 解决方案 |
|--------|------|--------|
| `Group not found` | 指定的 Group ID 不存在 | 运行 `list` 确认 Group ID |
| `Invalid symbol format` | 股票符号格式错误 | 检查符号是否包含正确的市场后缀（如 `.HK`, `.US`) |
| `Symbol already exists` | 尝试添加已存在的符号 | 使用 `get-symbols` 确认成员列表 |
| 网络错误 | API 连接失败 | 检查网络连接和 `.env` 配置 |

---

## 最佳实践

1. **命名约定**: 使用清晰、有意义的分组名称（如"科技股"、"高股息"、"IPO新股"）
2. **成员管理**: 定期审查分组成员，移除不再关注的股票
3. **备份**: 定期导出重要分组的成员列表作为备份
4. **组织方案**: 可以按行业、风格、策略等多个维度创建不同分组
5. **自动化**: 编写脚本定期导出和更新分组，配合数据获取工作流

---

## 下一步

导出分组成员列表后，可以使用这些符号进行数据获取和分析。

详见: [K线数据获取指南](candlesticks_guide.md)
