# skill-maintainer

[English](README.md) | [简体中文](README.zh-CN.md)

`skill-maintainer` 是一个用于维护、重构和审查 Agent Skill 及指令目录的
Agent Skill，目标是控制复杂度增长，删除过时规则，并保留 Agent 必要的判断空间。

## 解决的问题

适用于以下场景：

- Skill 越改越长，但旧规则没有被删除；
- 新规则与已有规则重复或冲突；
- 单个案例被固化成永久分支；
- 明确的 workflow 逐渐替代 Agent 判断；
- “认真处理”“保证质量”等默认就会遵守的 no-op 指令堆积；
- 重复检查、重试或澄清没有信息增益；
- 修改会影响触发边界、默认行为、安全、权限或输出契约。

Skill 采用“先审后改”模型：

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

每次维护都区分：

`preserve`、`add`、`replace`、`delete`、`move`、`uncertain`、
`agent_judgment_space`

## 支持范围

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

其中 `SKILL.md` 是主要行为规范源，其他 Agent 指令文件作为相关上下文读取，
不会为不同宿主复制出多套独立 workflow。

## 安装方式

### 使用 Git 克隆

```bash
git clone https://github.com/leijinynag/skill-maintainer.git
cd skill-maintainer
```

### 使用 GitHub CLI

```bash
gh repo clone leijinynag/skill-maintainer
cd skill-maintainer
```

### 下载 GitHub ZIP

打开仓库页面，选择 **Code -> Download ZIP**，解压后进入项目目录。

### 安装到 Codex 全局 Skill 目录

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/leijinynag/skill-maintainer.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

更新已有安装：

```bash
git -C "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer" pull
```

### 安装到单个项目

```bash
mkdir -p .codex/skills
git clone https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

也可以使用 Git submodule 固定版本：

```bash
git submodule add \
  https://github.com/leijinynag/skill-maintainer.git \
  .codex/skills/skill-maintainer
```

### 使用软链接进行本地开发

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn "$PWD" \
  "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

### 安装到 Claude 或其他兼容宿主

将整个仓库目录复制到宿主支持的 Skill 目录，并保留以下结构：

```text
skill-maintainer/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── evals/
```

如果宿主只支持单文件 Skill，至少复制 `SKILL.md`。如果还需要确定性审计能力，
同时复制 `scripts/` 和 `references/`。

## 使用方式

在 Codex 或其他支持 Agent Skill 的环境中调用：

```text
Use $skill-maintainer to audit and simplify this Agent skill before changing it.
```

中文示例：

```text
使用 $skill-maintainer 审查这个 SKILL.md，删除重复和过时规则，
并识别是否存在不必要的 workflow 分支。
```

## 风险分级

| 风险 | 默认行为 |
| --- | --- |
| `low` | 审计后可自动应用低风险清理 |
| `medium` | 只生成修改方案和 patch，等待确认 |
| `high` | 只生成修改方案和 patch，等待确认 |

`medium` 和 `high` 通常包括默认策略、路由、触发边界、安全、权限、写操作、
API、输出契约和跨 Skill handoff 的变化。

## 确定性审计

运行不依赖模型调用的结构审计脚本：

```bash
python3 scripts/audit_skill.py <target-dir> \
  --request "删除废弃的 fallback，并合并重复规则" \
  --json-out <report-path> \
  --git-ref main
```

不传 `--json-out` 时，报告默认写入目标项目根目录：

```text
.skill-maintainer/audit-report.json
```

审计内容包括：

- frontmatter 和 Skill 名称；
- 本地文件引用和断链；
- 重复标题和重复规则；
- 可能冲突的 `MUST` / `SHOULD` / `MAY`；
- 负向规则密度、相邻禁令和缺少替代动作；
- 无边界检查、重试或澄清导致空转的可能信号；
- 缺少可观察动作或完成条件的 no-op 指令；
- reference 嵌套和 Git diff 增长；
- 只增不删的复杂度增长和报告完整性。

负向规则、空转和 no-op 只作为复核信号，不会自动判定 Skill 错误。
安全类 Skill 即使包含较多必要 guardrail，也不会仅因禁令密度较高而失败。

退出码：

- `0`：审计通过；
- `1`：发现一般问题或需要复核的告警；
- `2`：目标目录、`SKILL.md` 或 Git ref 无效。

脚本只报告确定性的结构事实，不替代领域判断，也不会修改目标文件或 Git 历史。

## 审查报告

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

报告应区分：

- `fact`：脚本或文件直接确认的事实；
- `evidence`：支持判断的文件、行号、diff 或测试；
- `inference`：基于事实作出的推断；
- `unknown`：当前证据无法确认的内容。

## 当前限制

第一版有意保持范围较小：

- 不执行自动模型评测，只生成 framework-neutral 的 eval 清单；
- 不创建、提交、回退或重写 Git 历史；
- 不执行 release、rollback 或远程发布管理；
- 不访问业务 API，也不依赖特定公司的内部路径；
- 结构审计不能独立判断领域规则是否语义正确；
- 中、高风险变更需要人工确认后才能应用。

后续可以增加 Skill 快照、release channel、回滚辅助和模型评测 runner。

## 开发与测试

```bash
python3 -m unittest discover scripts -p 'test_*.py'
python3 scripts/validate_skill.py .
python3 /path/to/skill-creator/scripts/quick_validate.py .
python3 scripts/audit_skill.py . --request "审查仓库 Skill"
```

`evals/` 目录包含用于人工或独立模型评测框架的前向测试案例。
GitHub Actions 会在 push 和 pull request 时运行单元测试、Skill 校验和自身审计，
不会调用真实模型或业务 API。

## 许可证

[MIT License](LICENSE)
