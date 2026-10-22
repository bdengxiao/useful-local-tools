# Useful Local Tools

**三个可直接运行、也可交给 AI 助手调用的本地工具。** 处理表格编号损坏、文件交付漏件、项目配置缺项。MIT 开源；没有在线服务、API Key 或遥测。

[English](README.en.md) · [需求证据与竞品](DEMAND.md) · [测试记录](VALIDATION.md)

| 工具 | 什么时候用 | 得到什么 |
| --- | --- | --- |
| **CSV Text Safe** | CSV 中的学号、订单号不能丢零或变科学计数法 | 全部单元格按文本保存的 `.xlsx` |
| **Handoff Check** | 作业、素材或数据目录复制后，确认没有漏件或变动 | SHA-256 清单及 `missing / changed / extra` 报告 |
| **Env Preflight** | 项目下载后启动失败，怀疑 `.env` 配置不全 | 只包含键名与诊断的 JSON，不输出密钥值 |

## 60 秒试用

需要 Python **3.10 或更新版本**。下载仓库 ZIP 并解压，或：

```sh
git clone https://github.com/bdengxiao/useful-local-tools.git
cd useful-local-tools
python -m pip install -r requirements.txt
python run.py csv examples/orders.csv orders-text.xlsx
python run.py handoff create examples/handoff handoff-manifest.json
python run.py handoff verify examples/handoff handoff-manifest.json
python run.py env --example examples/config/.env.example --env examples/config/ready.sample
```

在 Windows 可将 `python` 换为 `py`，macOS/Linux 常用 `python3`。建议在自己的虚拟环境内安装依赖。**只有 CSV 工具需要 openpyxl；另两个仅用 Python 标准库，不必安装 requirements.txt。** 示例数据均为虚构。重复试跑 CSV/清单创建时请换新输出名，工具不会覆盖已有文件。

### 1. CSV Text Safe：保住原始编号

```sh
python run.py csv input.csv output.xlsx
python run.py csv input.tsv output.xlsx --delimiter tab --encoding gb18030
python run.py csv input.csv output.xlsx --no-header
```

`0000123`、`12345678901234567890`、`01-02`、`1E10` 和 `=1+2` 都写成原始文本，公式样式内容不会写成 Excel 公式，URL 不自动变成超链接。默认 UTF-8（兼容 BOM）、逗号分隔、首行为表头；有表头时冻结首行并加筛选。

原文件保持不变。输出文件存在、记录列数不齐、编码错误、非法控制字符、超过 Excel 行/列/单元格长度限制时直接报错，不静默截断。输入按流读取；Excel 最大 1,048,576 行、16,384 列、单元格 32,767 个 UTF-16 单元。空字符串在 Excel 中表现为空单元格。

**适合交付标识符，不适合直接做数值计算。** 不自动猜测编码/分隔符，也无法恢复上游已经丢失的数字。之后重新导出 CSV，再让 Excel 自动导入，仍可能发生类型转换。

### 2. Handoff Check：对照交付目录

```sh
python run.py handoff create ./original ./manifest.json
python run.py handoff verify ./copied ./manifest.json
```

清单保存相对路径、字节数和 SHA-256，可以换电脑核验。输出示意：

```json
{"ok": false, "missing": ["report.pdf"], "changed": ["data.csv"], "extra": ["notes.txt"], "checked": 1}
```

清单可放在目录内，其自身路径会被排除；复制时保留同一相对位置。包括隐藏文件；没有默认忽略规则。不移动、不修复、不删除文件。拒绝符号链接、Windows junction/reparse point 和非法清单路径；清单上限 64 MiB。

仅核验普通文件内容，不核验空文件夹、权限或时间戳。应对停止写入的目录使用：这是逐文件扫描，**不是原子快照**。文件与清单一起被篡改时无法证明真实性，也不能替代备份或证明业务软件能打开文件。不面向恶意进程并发改变文件系统链接的场景。

### 3. Env Preflight：排查缺项，不回显密钥

```sh
python run.py env --example .env.example --env .env
python run.py env --allow-empty OPTIONAL_LABEL --strict-extra
python run.py env --example examples/config/.env.example --env examples/config/local.sample
```

最后一条故意演示失败：`ACCESS_TOKEN` 还是占位符，`OPTIONAL_LABEL` 为空。报告缺少键、空值、重复键、模板错误和疑似占位符；不输出变量值或原始错误行，不修改文件、不执行 `$()` 或 `${...}`。

- 支持 UTF-8/BOM、可选 `export`、ASCII 键名、单行引号/非引号值与注释；文件上限 4 MiB。
- 不支持多行引号值；遇到此类语法会失败，不假装检查通过。
- 占位符启发式覆盖 `changeme`、`change_me`、`replace-me`、`your_*`、`<...>`、`TODO` 等；并非完整秘密扫描器。
- 额外键默认是提示，`--strict-extra` 将其视为失败。`--allow-empty KEY` 可重复；拼错键名会报错。
- `unexpanded` 仅提示插值样式文本，不执行或验证它；不合并系统环境、`.env.local` 或框架配置层。
- 不检查凭证是否有效。键名也可能暴露业务信息；分享报告前仍需自行判断。

### 退出码与自动化

`0`：本次检查/转换通过。`1`：Handoff/Env 检查发现差异。`2`：参数、输入或读取错误。JSON 可供 CI 或 AI 助手读取。三个脚本也能单独运行，根目录 `run.py` 只是便捷入口。

## 作为 AI Skill 使用

把 `skills/` 下面需要的**整个技能文件夹**复制到你的助手技能目录。Codex 通常使用 `~/.codex/skills/`（Windows 是 `%USERPROFILE%\.codex\skills\`）；如已有同名技能，先比较，不要直接覆盖。其他支持 `SKILL.md` 的助手按其安装方式使用。

- `csv-text-safe`：例如“把这份 CSV 转成 Excel，订单号和前导零要保持原样”。首次使用需安装该技能目录里的 requirements.txt。
- `handoff-check`：例如“给这个文件夹生成校验清单，再检查复制过去的版本有没有漏文件”。
- `env-preflight`：例如“对照 .env.example 检查本地配置，只告诉我缺哪些键，不要输出密钥”。

脚本和说明随技能文件夹一起分发，不依赖仓库内其他模块；安装技能不是上传用户文件。

## 测试与贡献

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

GitHub Actions 配置覆盖 Windows、Linux、macOS × Python 3.10/3.12。以仓库实际运行结果为准；本地记录见 [VALIDATION.md](VALIDATION.md)。测试使用临时合成数据，覆盖编号保真、公式字符串、编码失败、源文件不变、拒绝覆盖、目录复制/改动、恶意清单路径、配置值不回显和 CLI 退出码。

欢迎带最小复现的 Issue/PR。**不要上传真实 `.env`、密钥、个人编号或私有业务文件。** 修复时请附合成回归用例。

## 为什么做这三个

[TableTool #103](https://github.com/jakob/TableTool/issues/103) 中用户要求保留长度不固定的带零账号；[RHash #198](https://github.com/rhash/RHash/issues/198) 讨论漏件/多件检查；[dotenv-linter #728](https://github.com/dotenv-linter/dotenv-linter/issues/728) 讨论模板与私有配置的缺项。这是具体需求信号，**不等于已验证的大市场或商业成功**。

成熟替代品包括 [XlsxWriter](https://github.com/jmcnamara/XlsxWriter)、[RHash](https://github.com/rhash/RHash)、[bagit-python](https://github.com/LibraryOfCongress/bagit-python)、[dotenv-linter](https://github.com/dotenv-linter/dotenv-linter) 和 [dotenv-safe](https://github.com/rolodato/dotenv-safe)。其中多项需求已经得到解决。本项目选择小范围、保守默认值、可读诊断与可独立分发的 Skill。完整来源和局限见 [DEMAND.md](DEMAND.md)。
