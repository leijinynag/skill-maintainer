# skill-maintainer

用于维护 Agent Skill 和指令目录的 Codex Skill，帮助 AI 在修改过程中控制复杂度增长、删除过时规则，并保留必要的判断空间。

它适合处理以下问题：

- Skill 越改越长，旧规则没有被删除；
- 新增规则与已有规则重复或冲突；
- 单个案例被固化成永久分支；
- 明确的 workflow 逐渐替代了 Agent 的判断；
- 修改涉及触发边界、默认行为、安全要求或输出契约，需要先审查再改。

## 解决什么问题

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

每次维护都会区分以下变更类型：

`preserve`、`add`、`replace`、`delete`、`move`、`uncertain`、`agent_judgment_space`

它不会只报告“新增了多少内容”，还会检查是否应该替换或删除旧内容，以及复杂度增加是否带来了明确的行为收益。

## 适用范围

可以审查和维护以下内容：

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

## 安装

### Codex

将仓库复制或链接到 Codex 的 Skill 目录：

```bash
cp -R . "${CODEX_HOME:-$HOME/.codex}/skills/skill-maintainer"
```

也可以直接将仓库中的 `SKILL.md` 和相关资源安装到宿主环境支持的 Skill 目录。

### Claude 兼容环境

使用宿主环境支持的 Skill 安装目录，或在项目配置中引用本仓库的 `SKILL.md`。

## 使用方式

在 Codex 或其他支持 Agent Skill 的环境中使用：

```text
Use $skill-maintainer to audit and simplify this Agent skill before changing it.
```

中文请求示例：

```text
使用 $skill-maintainer 审查这个 SKILL.md，找出重复、过时规则和 workflow 化倾向，再决定哪些内容可以删减。
```

维护时，Skill 会先读取目标目录和 Git 上下文，生成变更账本并分类风险：

| 风险 | 默认行为 |
| --- | --- |
| `low` | 审计后可以自动应用低风险清理 |
| `medium` | 只生成修改方案和 patch，等待确认 |
| `high` | 只生成修改方案和 patch，等待确认 |

`medium` 和 `high` 通常包括默认策略、路由、触发边界、安全、权限、写操作、API、输出契约和跨 Skill handoff 的变化。

## 确定性审计

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

报告需要区分：

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

后续可以增加 Skill 版本快照、release channel、回滚辅助和模型评测 runner。

## 开发与测试

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

## 许可证

[MIT License](LICENSE)
