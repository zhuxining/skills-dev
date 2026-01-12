# Skill 打包工具

## 功能

将技能文件夹打包到 `./dist/` 目录下,自动排除环境文件、版本控制文件等不必要的文件。

## 使用方法

```bash
python3 build/package_skill.py <skill-folder>
```

### 示例

```bash
python3 build/package_skill.py skill-name
```

## 自动排除的文件类型

脚本会自动排除以下类型的文件和目录：

### 环境文件
- `.env`, `.env.local`, `.env.development`, `.env.production`, `.env.test`

### 版本控制
- `.git`, `.gitignore`, `.gitattributes`

### Python 相关
- `__pycache__`, `*.pyc`, `*.pyo`, `*.pyd`
- `venv`, `env`, `.venv`

### Node.js 相关
- `node_modules`, `package-lock.json`, `yarn.lock`

### IDE 和编辑器
- `.vscode`, `.idea`, `.DS_Store`
- `*.swp`, `*.swo`, `*~`

### 构建产物
- `dist`, `build`, `*.egg-info`

### 日志和临时文件
- `*.log`, `logs`
- `.tmp`, `tmp`, `*.tmp`, `*.bak`, `*.cache`

## 输出

打包完成后,技能文件会保存在：
```
./dist/<skill-name>/
```

输出目录将包含：
- 完整的技能文件夹结构
- 所有必需的文件(排除上述不必要的文件)
- 保留文件权限和时间戳

## 验证

脚本会在打包前自动验证技能结构：
1. 检查 `SKILL.md` 是否存在
2. 验证 YAML frontmatter 格式
3. 确认 `name` 和 `description` 字段存在

## 错误处理

如果出现以下情况,脚本会报错并退出：
- 技能文件夹不存在
- 缺少 `SKILL.md` 文件
- frontmatter 格式不正确
- 缺少必需的 `name` 或 `description` 字段

## 重复打包

如果 `dist/<skill-name>/` 已经存在,脚本会自动删除旧文件并重新打包。
