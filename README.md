# check-dco

一个 **纯 Python、零依赖** 的 pre-commit hook，在 `commit-msg` 阶段验证 commit message 包含有效的 `Signed-off-by` 行，确保 **Developer Certificate of Origin (DCO)** 合规。

## 为什么需要它

[CNCF](https://github.com/cncf/foundation/blob/main/docs/dco-guidelines.md)、Linux Foundation 等顶级开源项目强制要求每个 commit 携带 `Signed-off-by: Name <email>`。没有本地拦截，只能在 CI 推送后才能发现，浪费 runner 时间。

check-dco 把这个检查**左移**到 `commit-msg` 阶段——commit 瞬间拦截，0 网络依赖，0 外部依赖。

## 快速开始

### 1. 在项目中添加配置

在项目根目录的 `.pre-commit-config.yaml` 中添加：

```yaml
repos:
  - repo: https://github.com/Ikalus1988/pre-commit-hooks
    rev: e63f77e   # 使用最新的全绿 commit
    hooks:
      - id: check-dco
```

> 等上游 `pre-commit/pre-commit-hooks` 官方合入并发布新版本后，可将 `repo` 换回官方地址。

### 2. 安装 commit-msg hook

```bash
pre-commit install --hook-type commit-msg
```

⚠️ 这一步**不能省略**。只运行 `pre-commit install` 只会注入默认的 pre-commit 阶段钩子，check-dco 是 `commit-msg` 阶段，必须用 `--hook-type commit-msg`。

### 3. 验证

```bash
# 正常提交（带 Signed-off-by）
echo -e "feat: add search\n\nSigned-off-by: Alice <alice@example.com>" | pre-commit try-repo https://github.com/Ikalus1988/pre-commit-hooks check-dco --ref e63f77e --commit-msg-filename /dev/stdin

# 被拦截的提交（缺少 Signed-off-by）
echo -e "feat: quick fix" | pre-commit try-repo https://github.com/Ikalus1988/pre-commit-hooks check-dco --ref e63f77e --commit-msg-filename /dev/stdin
```

## 测试计划

### 单元测试套件

项目包含 225 行 pytest 测试用例，覆盖全部功能路径。在 `pre-commit-hooks` 项目的 CI 中自动运行：

```bash
# 在本地运行测试
cd pre-commit-hooks
pip install -e .
pytest tests/check_dco_test.py -v
```

**测试文件**: `tests/check_dco_test.py`

| 测试分组 | 用例数 | 覆盖目标 |
|----------|--------|----------|
| ✅ Success cases | 7 | 标准 sign-off、多 co-author、body 中间、全名、+ 地址、多段落 |
| ❌ Failure cases | 6 | 缺 sign-off、空消息、缺 email、缺 name、小写、缺冒号 |
| 🧪 main() integration | 3 | CLI 入口通过、失败、--help |

### 测试场景矩阵

```
输入                                          → 期望 exit code
─────────────────────────────────────────────────────────────
"feat: add search\n\nSigned-off-by: A <a@b>"  →  0
空消息                                          →  1
无 Signed-off-by 行                             →  1
Signed-off-by: JustName                       →  1
Signed-off-by: <anon@example.com>              →  1
signed-off-by: alice <alice@example.com>       →  1
Signed-off-by alice <alice@example.com>        →  1
```

### CI 流水线

| 检查层 | 工具 | 失败时行为 |
|--------|------|-----------|
| pre-commit.ci（lint） | flake8, mypy, pyupgrade 等 14 项 | 阻塞 PR |
| GitHub Actions（test） | tox + pytest (py310–py313) | 阻塞 PR |
| GitHub Actions（collector） | 官方 hook 注册校验 | 阻塞 PR |
| GitHub Actions（Windows） | tox + pytest (py310) | 阻塞 PR |

### 端到端验证

```bash
# 1. 模拟有效 sign-off
echo -e "feat: add search\n\nSigned-off-by: Alice <alice@example.com>" > /tmp/msg
python3 pre_commit_hooks/check_dco.py /tmp/msg
echo $?   # 预期输出: 0，无 stderr

# 2. 模拟缺失 sign-off
echo -e "feat: quick fix" > /tmp/msg
python3 pre_commit_hooks/check_dco.py /tmp/msg
echo $?   # 预期输出: 1，stderr 提示 missing Signed-off-by

# 3. 通过 pre-commit 框架触发
pre-commit try-repo https://github.com/Ikalus1988/pre-commit-hooks \
    check-dco --ref e63f77e --commit-msg-filename /tmp/msg
```

---

## 验收标准

### 功能验收

| 编号 | 标准 | 验证方式 | 通过条件 |
|------|------|----------|----------|
| AC-1 | 有效 sign-off 通过 | `pytest tests/check_dco_test.py::test_standard_signoff` | exit 0 |
| AC-2 | 多 co-author sign-off 通过 | `pytest tests/check_dco_test.py::test_multiple_signoffs` | exit 0 |
| AC-3 | 缺 sign-off 被拦截 | `pytest tests/check_dco_test.py::test_missing_signoff` | exit 1 |
| AC-4 | 空消息被拦截 | `pytest tests/check_dco_test.py::test_empty_message` | exit 1 |
| AC-5 | malformed 格式被拦截（缺 email） | `pytest tests/check_dco_test.py::test_signoff_without_email` | exit 1 |
| AC-6 | malformed 格式被拦截（缺 name） | `pytest tests/check_dco_test.py::test_signoff_without_name` | exit 1 |
| AC-7 | 大小写敏感校验 | `pytest tests/check_dco_test.py::test_lowercase_signoff_only` | exit 1 |
| AC-8 | 缺冒号被拦截 | `pytest tests/check_dco_test.py::test_signoff_only_no_colon` | exit 1 |
| AC-9 | CLI 入口 main() 有效 sign-off | `pytest tests/check_dco_test.py::test_main_passes_with_valid_signoff` | exit 0 |
| AC-10 | CLI 入口 main() 缺 sign-off | `pytest tests/check_dco_test.py::test_main_fails_without_signoff` | exit 1 |

### CI 验收

| 编号 | 标准 | 验证方式 | 通过条件 |
|------|------|----------|----------|
| AC-CI-1 | pre-commit.ci 全绿 | PR Checks 页面的 `pre-commit.ci - pr` | status: success |
| AC-CI-2 | GitHub Actions collector 通过 | `main-linux / collector` + `main-windows / collector` | conclusion: success |
| AC-CI-3 | tox 测试矩阵全部通过 | py310 / py311 / py312 / py313（Linux + Windows） | conclusion: success |
| AC-CI-4 | flake8 无警告 | 在 pre-commit.ci 输出中检查 | flake8: Passed |
| AC-CI-5 | mypy 类型检查通过 | 在 pre-commit.ci 输出中检查 | mypy: Passed |
| AC-CI-6 | README 与 hooks 清单同步 | `test_readme_contains_all_hooks` | 测试通过 |

### AI 代理集成验收

| 编号 | 标准 | 验证方式 | 通过条件 |
|------|------|----------|----------|
| AC-AGENT-1 | hook 安装正确 | `.git/hooks/commit-msg` 存在且为 pre-commit 生成 | 文件存在, 含 `pre-commit` 标识 |
| AC-AGENT-2 | 代理 commit 带 -s 不被拦截 | 代理环境中执行 `git commit -s -m "test"` | commit 成功, exit 0 |
| AC-AGENT-3 | 代理 commit 不带 -s 被拦截 | 代理环境中执行 `git commit -m "test"` | commit 被中止, exit 1 |
| AC-AGENT-4 | 供应链安全 | fork 已镜像到可控组织仓库 | 镜像仓库中有同步的代码 |

### 回归测试

每次修改后应执行完整的验收套件：

```bash
# 1. 代码风格
pre-commit run --all-files

# 2. 单元测试
pytest tests/check_dco_test.py -v --tb=short

# 3. README 一致性检查
pytest tests/readme_test.py -v

# 4. 端到端
pre-commit try-repo . check-dco --commit-msg-filename <(echo -e "test\n\nSigned-off-by: CI <ci@test>")
```

---

## 工作原理

| 阶段 | 说明 |
|------|------|
| **触发时机** | `git commit` 执行时，编辑器/消息写入后 |
| **输入** | pre-commit 传入的临时 commit message 文件路径 (`argv[1]`) |
| **检查规则** | 正则匹配 `Signed-off-by: Name <email>`（严格模式） |
| **成功** | exit 0，commit 正常进行 |
| **失败** | exit 1，打印错误详情，commit 被中止 |

### 检查覆盖的场景

| 场景 | 结果 |
|------|------|
| `Signed-off-by: Alice <alice@example.com>` | ✅ 通过 |
| 多个 co-author sign-off | ✅ 通过 |
| sign-off 在 body 中间 | ✅ 通过 |
| 缺少 sign-off | ❌ 拦截 |
| `Signed-off-by: justname`（缺 email） | ❌ 拦截 |
| `signed-off-by:`（小写） | ❌ 拦截 |
| `Signed-off-by alice <alice@example.com>`（缺冒号） | ❌ 拦截 |

## AI 代理（马甲）配置指南

如果你使用 AI 代理自动提 PR（如 `zsxh1990`、`sheldonisspark-lab`），建议在代理环境中做以下配置：

### 方案 A：全局 commit 模板（推荐）

```bash
# 设置 commit 模板，自动带出 Signed-off-by 行
git config --global commit.template ~/.gitmessage

# 在 ~/.gitmessage 中写入：
# Signed-off-by: Agent Name <agent@your-org.com>
```

### 方案 B：git 别名覆盖

```bash
# 让 git commit 自动带上 -s 标志
git config --global alias.commit 'commit -s'
```

### 方案 C：脚本封装（最稳妥）

在代理的启动脚本中重写 git commit：

```bash
# 将原始的 git commit 封装为 git commit -s
git() {
  if [[ "$1" == "commit" ]]; then
    command git commit -s "${@:2}"
  else
    command git "$@"
  fi
}
```

### 方案 D：pre-commit hook 安装

```bash
# 在代理项目初始化时执行
pip install pre-commit
pre-commit install --hook-type commit-msg
```

## 与 dco-audit 的关系

| 工具 | 阶段 | 作用 |
|------|------|------|
| **check-dco**（本工具） | 本地 `commit-msg` | 在开发者/AI commit 的瞬间拦截，左移检查 |
| [dco-audit](https://github.com/Ikalus1988/dco-audit) | CI `pull_request` | 在 PR 时对所有 commit 做全量审计，并发布修复指引 comment |

两者互补：check-dco 阻止问题发生，dco-audit 兜底兜住漏网之鱼。

## Plan B：独立仓库

如果官方维护者因"DCO 应由远端服务处理"等理由拒绝合入，本仓库可独立为 `pre-commit-dco`：

```bash
git clone https://github.com/Ikalus1988/pre-commit-hooks pre-commit-dco
cd pre-commit-dco
git filter-branch --subdirectory-filter .
```

独立后继续维护，保持与官方的同步。

## 许可证

MIT
