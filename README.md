# skill-maintainer

用于维护 Agent Skill 和指令目录的 Codex Skill，帮助 AI 在修改过程中控制复杂度增长、删除过时规则，并保留必要的判断空间。

`skill-maintainer` is an Agent Skill for maintaining skills and instruction
directories without uncontrolled growth or overly rigid workflows.

## 中文说明

### 解决什么问题

它适合处理以下问题：

- Skill 越改越长，旧规则没有被删除；
- 新增规则与已有规则重复或冲突；
- 单个案例被固化成永久分支；
- 明确的 workflow 逐渐替代了 Agent 的判断；
- 修改涉及触发边界、默认行为、安全要求或输出契约，需要先审查再改。

`skill-maintainer` 采用“先审后改”的维护模型：

```text
discover
  -> inspect
  -> build change ledger
  -> classify risk
  -> propose
  -> apply low-risk changes or wait for confirmation
  -> prune
  -> validate
  -> report
```

每次维护都会区分：

`preserve`、`add`、`replace`、`delete`、`move`、`uncertain`、`agent_judgment_space`

它不会只报告“新增了多少内容”，还会检查是否应该替换或删除旧内容，以及复杂度增加是否带来了明确的行为收益。

### 适用范围

可以审查和维护：

- `SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `assets/`
- `evals/`
- Git 历史和 diff

其中 `SKILL.md` 是主要行为规范源，其他 Agent 指令文件只作为相关上下文读取。

### 安装方式

#### 方式一：使用 Git 克隆

```bash
git clone https://github.com/leijinynag/skill-maintainer.git
cd skill-maintainer
```

#### 方式二：使用 GitHub CLI

```bash
gh repo clone leijinynag/skill-maintainer
cd skill-maintainer
```

#### 方式三：下载 GitHub ZIP

在 GitHub 仓库页面选择 **Code -> Download ZIP**，解压后进入项目目录。

#### 方式四：安装到 Codex 全局 Skill 目录

适合让当前用户的所有 Codex 项目使用：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/leijinynag/skill-maintainer.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

如果已经克隆了仓库，也可以复制：

```bash
cp -R ./skill-maintainer \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

#### 方式五：安装到单个项目

适合团队把 Skill 和项目一起管理：

```bash
mkdir -p .codex/skills
git clone https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

也可以将仓库作为 Git submodule：

```bash
git submodule add \
  https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

#### 方式六：使用软链接进行本地开发

适合修改本仓库并立即在 Codex 中验证：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$PWD" \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

#### 方式七：安装到 Claude 或其他兼容宿主

将整个仓库目录复制到宿主支持的 Skill 目录，并保留以下结构：

```text
skill-maintainer/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── evals/
```

如果宿主只支持单文件 Skill，至少复制 `SKILL.md`；如果需要确定性审计能力，同时复制 `scripts/` 和 `references/`。

### 使用方式

在 Codex 或其他支持 Agent Skill 的环境中使用：

```text
Use $skill-maintainer to audit and simplify this Agent skill before changing it.
```

中文请求示例：

```text
使用 $skill-maintainer 审查这个 SKILL.md，找出重复、过时规则和 workflow 化倾向，再决定哪些内容可以删减。
```

### 风险分级

| 风险 | 默认行为 |
| --- | --- |
| `low` | 审计后可以自动应用低风险清理 |
| `medium` | 只生成修改方案和 patch，等待确认 |
| `high` | 只生成修改方案和 patch，等待确认 |

`medium` 和 `high` 通常包括默认策略、路由、触发边界、安全、权限、写操作、API、输出契约和跨 Skill handoff 的变化。

### 确定性审计

仓库提供不依赖模型调用的结构审计脚本：

```bash
python3 scripts/audit_skill.py <target-dir> \
  --request "删除废弃的 fallback，并合并重复规则" \
  --json-out <report-path> \
  --git-ref main
```

如果不传 `--json-out`，报告默认写入目标项目根目录：

```text
.skill-maintainer/audit-report.json
```

审计脚本检查：

- `SKILL.md` frontmatter；
- Skill 名称与目录名是否一致；
- Markdown 和上下文中的本地文件引用；
- 断链；
- 重复标题和重复规则；
- 可能冲突的 `MUST` / `SHOULD` / `MAY`；
- `SKILL.md` 行数、标题数和规则数；
- references 嵌套；
- Git diff 的新增/删除比例；
- 只增不删的复杂度增长；
- JSON 报告字段完整性。

退出码：

- `0`：审计通过；
- `1`：发现一般问题或需要复核的告警；
- `2`：目标目录、`SKILL.md` 或 Git ref 无效。

脚本只报告可确定的结构事实，不替代领域判断，也不会修改目标文件或 Git 历史。

### 审查报告

报告包含以下主要字段：

```json
{
  "report_version": "0.1.0",
  "target": {},
  "git_context": {},
  "baseline_metrics": {},
  "change_request": "",
  "change_ledger": {},
  "findings": [],
  "risk": {},
  "proposed_changes": [],
  "applied_changes": [],
  "eval_cases": [],
  "validation": {}
}
```

报告需要区分：

- `fact`：脚本或文件直接确认的事实；
- `evidence`：支持判断的文件、行号、diff 或测试；
- `inference`：基于事实作出的推断；
- `unknown`：当前证据无法确认的内容。

### 当前限制

第一版有意保持范围较小：

- 不执行自动模型评测，只生成 framework-neutral 的 eval 清单；
- 不创建、提交、回退或重写 Git 历史；
- 不执行 release、rollback 或远程发布管理；
- 不访问业务 API，也不依赖特定公司的内部路径；
- 结构审计不能独立判断领域规则是否语义正确；
- 中、高风险变更需要人工确认后才能应用。

后续可以增加 Skill 版本快照、release channel、回滚辅助和模型评测 runner。

### 开发与测试

运行单元测试：

```bash
python3 -m unittest discover scripts -p 'test_*.py'
```

使用 Codex 官方 Skill 校验器：

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py .
```

运行仓库本地校验：

```bash
python3 scripts/validate_skill.py .
```

运行自身审计：

```bash
python3 scripts/audit_skill.py . --request "审查仓库 Skill"
```

行为 eval 位于 `evals/`，用于人工或独立模型评测框架进行前向测试。GitHub Actions 会在 push 和 pull request 时运行单元测试、Skill 结构校验和自身审计，不会执行真实模型调用或业务 API。

## English Documentation

### What It Solves

`skill-maintainer` is designed for cases where:

- a Skill keeps getting longer without removing obsolete rules;
- new guidance duplicates or conflicts with existing guidance;
- one-off incidents become permanent branches;
- a rigid workflow gradually replaces agent judgment;
- a change affects trigger boundaries, defaults, safety, permissions, or output contracts.

It follows a review-before-editing model:

```text
discover
  -> inspect
  -> build change ledger
  -> classify risk
  -> propose
  -> apply low-risk changes or wait for confirmation
  -> prune
  -> validate
  -> report
```

Each maintenance pass separates:

`preserve`, `add`, `replace`, `delete`, `move`, `uncertain`, and
`agent_judgment_space`.

The goal is not merely to count added lines. The Skill also checks whether existing
rules should be replaced or removed and whether added complexity has a concrete
behavioral benefit.

### Supported Scope

The Skill can inspect and maintain:

- `SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`
- `assets/`
- `evals/`
- Git history and diffs

`SKILL.md` is treated as the primary behavior source. Other agent instruction
files are read as related context rather than separate host-specific workflows.

### Installation

#### Option 1: Clone with Git

```bash
git clone https://github.com/leijinynag/skill-maintainer.git
cd skill-maintainer
```

#### Option 2: Clone with GitHub CLI

```bash
gh repo clone leijinynag/skill-maintainer
cd skill-maintainer
```

#### Option 3: Download a ZIP archive

Open the repository page, select **Code -> Download ZIP**, extract the archive,
and enter the extracted directory.

#### Option 4: Install globally for Codex

This makes the Skill available to all Codex projects for the current user:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/leijinynag/skill-maintainer.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

If the repository has already been cloned:

```bash
cp -R ./skill-maintainer \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

#### Option 5: Install in one project

Use this when the project should pin and review the Skill together with its code:

```bash
mkdir -p .codex/skills
git clone https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

You can also add it as a Git submodule:

```bash
git submodule add \
  https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

#### Option 6: Use a symlink for local development

This is useful when editing this repository and testing changes immediately:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$PWD" \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

#### Option 7: Install in Claude or another compatible host

Copy the whole repository into the host's supported Skill directory and preserve
this structure:

```text
skill-maintainer/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── evals/
```

If the host only supports a single Skill file, copy at least `SKILL.md`. To keep
deterministic auditing available, also copy `scripts/` and `references/`.

### Usage

Invoke it in Codex or another Agent Skill-compatible environment:

```text
Use $skill-maintainer to audit and simplify this Agent skill before changing it.
```

Example:

```text
Use $skill-maintainer to review this SKILL.md, remove obsolete and duplicate
rules, and identify any workflow branches that unnecessarily reduce judgment.
```

### Risk Levels

| Risk | Default behavior |
| --- | --- |
| `low` | Apply low-risk cleanup after auditing when the user requested edits |
| `medium` | Produce a proposal and patch; wait for confirmation |
| `high` | Produce a proposal and patch; wait for confirmation |

Medium and high risk changes generally include changes to defaults, routing,
trigger boundaries, safety, permissions, writes, APIs, output contracts, or
cross-Skill handoffs.

### Deterministic Audit

Run the dependency-free structural auditor:

```bash
python3 scripts/audit_skill.py <target-dir> \
  --request "Remove the obsolete fallback and merge duplicate rules." \
  --json-out <report-path> \
  --git-ref main
```

Without `--json-out`, the report is written to:

```text
.skill-maintainer/audit-report.json
```

The auditor checks frontmatter, naming, local references, broken links,
duplicate headings and rules, conflicting strong rules, metrics, reference
nesting, Git diff growth, append-only changes, and report completeness.

Exit codes:

- `0`: audit passed;
- `1`: ordinary findings or warnings require review;
- `2`: the target, `SKILL.md`, or Git ref is invalid.

The script reports deterministic structural facts. It does not decide whether a
domain-specific rule is semantically correct and does not modify files or Git
history.

### Report Format

Reports include:

```json
{
  "report_version": "0.1.0",
  "target": {},
  "git_context": {},
  "baseline_metrics": {},
  "change_request": "",
  "change_ledger": {},
  "findings": [],
  "risk": {},
  "proposed_changes": [],
  "applied_changes": [],
  "eval_cases": [],
  "validation": {}
}
```

Reports should distinguish facts, evidence, inferences, and unknowns.

### Limitations

The first release intentionally stays small:

- no automatic model-evaluation runner; only framework-neutral eval cases;
- no Git commit, rollback, history rewrite, release, or remote publishing;
- no business API access or company-specific internal paths;
- structural checks cannot establish semantic correctness for a domain rule;
- medium and high risk changes require explicit human confirmation.

Future versions may add Skill snapshots, release channels, rollback assistance,
and a model-evaluation runner.

### Development and Testing

Run unit tests:

```bash
python3 -m unittest discover scripts -p 'test_*.py'
```

Run the official Codex Skill validator:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py .
```

Run the repository-local validator:

```bash
python3 scripts/validate_skill.py .
```

Run a self-audit:

```bash
python3 scripts/audit_skill.py . --request "Audit the repository Skill"
```

The `evals/` directory contains cases for manual or independent model-based
forward testing. GitHub Actions runs unit tests, Skill validation, and a
self-audit on pushes and pull requests. It does not call real models or business
APIs.

## License

[MIT License](LICENSE)
