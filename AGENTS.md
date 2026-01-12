# Agent Instructions for skills-dev

This file provides guidance to Agents when working in this repository for creating optimization AI agent "skills".

## About Skills

Skills are modular, self-contained packages that extend Agent's capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks—they transform Claude from a general-purpose agent into a specialized agent equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Claude needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Claude is already very smart.** Only add context Claude doesn't already have. Challenge each piece of information: "Does Claude really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Claude as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required, Body content - max 500 lines)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Claude reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Claude for patching or environment-specific adjustments
- **Execution**: All scripts must be directly executable via bash with proper shebang and executable permissions

Take python as an example, it can be a node/bash script.

**Module Docstrings:**

```python
"""
#!/usr/bin/env python3
Module purpose and functionality.

Usage:
    python3 script_name.py <arguments>
"""
```

**Function Docstrings:**

```python
def function_name(param1, param2):
    """
    Brief description of function.

    Args:
        param1: Description of parameter
        param2: Description of parameter

    Returns:
        Description of return value
    """
```

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Claude's process and thinking.

- **When to include**: For documentation that Claude should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Claude determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Claude produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Claude to use files without loading them into context

**Rules:**

- Catch broad exceptions (`Exception`) - no custom exception classes
- Print user-friendly error messages with context
- Return `None` on error, valid value on success
- For validation: return `(bool, str)` tuple (status, message)
- No raising exceptions to caller (handle locally)
- Early returns for error conditions

#### Input/Output (optional)

**Input (`input/`)**

Example input data and test files to demonstrate skill usage.

- **When to include**: When the skill needs reference inputs, test data, or sample files
- **Examples**: `input/sample_data.json`, `input/test_cases/`, `input/example_config.yaml`
- **Use cases**: Test data, sample configurations, example inputs, edge case files
- **Benefits**: Provides runnable examples, validates skill behavior, helps with testing

**Output (`output/`)**

Example outputs and templates showing expected results.

- **When to include**: When the skill needs to demonstrate output format or provide templates
- **Examples**: `output/result_template.md`, `output/sample_report.pdf`, `output/expected_format.json`
- **Use cases**: Output templates, expected results, format examples, reference outputs
- **Benefits**: Shows expected format, provides templates, validates output quality

## Best Practices

1. **Context Efficiency:** Minimize token usage through concise code, small file sizes, and reduced complexity
2. **Progressive Disclosure:** Load only what's needed (3-level: metadata → body → resources)
3. **Clear Output:** Use emoji indicators and descriptive messages
