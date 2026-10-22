# 三个实用开源工具：需求证据与定位

调研日期：2026-10-22。方法：先用 GitHub 连接器搜索原始 issue，再读取 GitHub 原帖、维护者回复与官方文档。以下是定性需求信号，不是市场规模调查；未进行用户访谈、下载量统计或付费意愿测试。三个方向均有成熟替代品，不应宣传为“市场空白”。建议交付为可单独运行的 CLI，加可选 AI Skill，避免只有提示词。

## 1. CSV → 全文本 XLSX

**建议做，优先级最高。** 面向学号、订单号、账号等标识符表格交付，默认所有单元格保留为文本，避免自动类型推断造成不可逆损失。这个定位比通用格式转换更明确。

原始需求：

- [TableTool #103](https://github.com/jakob/TableTool/issues/103)：2023-02-25 用户处理长度不固定、带前导零的账号，明确表示补齐到固定长度的办法不可用，要求打开 CSV 时保留原值。本次网页显示 Open。
- [ng-csv #213](https://github.com/asafdav/ng-csv/issues/213)：2017-08-02 用户导出账号 `00000001` 遇到前导零丢失，尝试额外引号和转义开关均未解决。本次网页显示 Open。这是长期痛点的历史证据，不能据此断言该旧项目今天仍活跃。
- [AlaSQL #960](https://github.com/AlaSQL/alasql/issues/960)：CSV 中账号转成数值后再转字符串，前导零已经无法恢复；连接器读取了完整复现。这里只作为补充，不声称当前版本仍有同样问题。

现有方案：

- [XlsxWriter](https://github.com/jmcnamara/XlsxWriter) 已能写 XLSX；[官方 worksheet 文档](https://xlsxwriter.readthedocs.io/worksheet.html) 明确区分字符串、数值、公式和 URL，并提供 `write_string()`。核心技术能力已解决，新工具的价值在安全默认值和直接可用的命令，而非新格式技术。
- [TableTool](https://github.com/jakob/TableTool) 是现成 CSV 编辑器，也是上述需求发生的环境；它与专注交付的命令行转换流程有不同入口。

建议验收：原始字段逐格保留；前导零、18 位标识符、日期样式、科学计数法样式、等号开头文本均按文本写出；拒绝超出 XLSX 限制的输入，不能静默截断；支持显式编码与分隔符；禁止覆盖源文件。公式应作为字符串保存，不能用新增公式来“保留数字”。必须说明全文本输出不适合直接数值计算，也无法恢复已经被上游软件破坏的数据。桌面 Excel/WPS 实机行为仍需单独验证。

## 2. 文件交付 manifest create / verify

**建议做，定位轻量交付检查器。** 面向作业、研究附件、素材包和数据目录搬运后的完整性对照，一次给出 missing / changed / extra，并保留机器可读 JSON。

原始需求：

- [RHash #198](https://github.com/rhash/RHash/issues/198)：2022-02-27 用户要求区分清单中缺失的文件和目录里未列入清单的文件。重要：维护者 2023-07-27 已给出 `--missing`、`--unverified` 的使用示例；该功能已经存在，不能将此 issue 当作尚未解决的空白。后续用户仍反映调用语法和目录范围不直观。
- [RHash #208](https://github.com/rhash/RHash/issues/208)：2022-06-27 用户抱怨长路径导致校验输出难读，要求把结果状态放在每行开头。本次网页显示 Open。它支持“报告可读性有价值”的判断，而不是证明哈希功能稀缺。
- [bagit-python #186](https://github.com/LibraryOfCongress/bagit-python/issues/186)：用户提出重复打包会出现 bag 套 bag，希望警告。这是修改目录结构的打包流程与只读检查流程存在差异的例子，不是指 BagIt 不可靠。

现有方案：

- [RHash](https://github.com/rhash/RHash)：成熟的多算法哈希与校验工具，已提供缺失与未验证文件检查。
- [bagit-python](https://github.com/LibraryOfCongress/bagit-python)：Library of Congress 的 BagIt 工具，可创建和验证规范化数据包；官方 README 有 SHA256 与 validate 命令。需要正式档案交换规范时应优先考虑它。

建议差异化：Python 标准库即可运行；保持原目录结构，不移动、不删除、不修复源文件；清单相对路径、SHA256、大小；一次输出分类和退出码；校验拒绝路径穿越、绝对路径、链接越界；扫描中变化不能报告为可信快照。它不是备份，不证明来源真实性；清单与文件同时被篡改无法靠同一清单发现。对持续写入目录应提示不是原子快照。

## 3. .env.example / .env 只读检查器

**可以做，但竞争最充分，不能卖“首次解决缺少环境变量”。** 价值聚焦：AI 助手排查配置时只拿到键名和诊断，值留在本机；提供零第三方依赖的静态 CLI，不初始化应用。

原始需求：

- [dotenv-linter #728](https://github.com/dotenv-linter/dotenv-linter/issues/728)：2023-11-21 用户有提交到仓库的模板和每人本地的私有配置，想识别并补齐缺少键。2024-07-14 回复进一步追问应复制值还是只复制键。本次网页显示 Open，但本工具只覆盖识别与指导，不满足自动复制请求。
- [dotenv-linter #541](https://github.com/dotenv-linter/dotenv-linter/issues/541)：用户区分完整 `.env` 与只包含覆盖项的 `.env.local`，不希望后者因缺少所有键而被误报。维护者和用户讨论覆盖模式与继承规则。它说明简单对称键集合比较会误报；本工具首版必须明确“模板要求检查”与“多层覆盖解析”不同，不能宣传覆盖全部框架。

现有方案：

- [dotenv-linter](https://github.com/dotenv-linter/dotenv-linter)：当前 README 已有重复键检查、修复、`diff .env .env.example`、CI 与 pre-commit 接入，基础需求已覆盖。历史 issue 中的 `compare` 名字与当前 README 的 `diff` 不同，文档不可盲抄旧命令。
- [dotenv-safe](https://github.com/rolodato/dotenv-safe)：从 `.env.example` 读取要求的变量名，在 Node 初始化后检查 `process.env`；README 明确不验证值格式或有效性。因此静态文件检查器应说明不验证外部进程环境，也不证明凭证能登录。

建议验收：缺少键、重复键、空值、可配置占位符；结果和错误只含键名/行号，不输出原行或原始值；拒绝执行命令替换与变量展开；只读；明确支持的 dotenv 语法，遇到不支持的多行/语法不能静默通过。占位符判断是启发式，不应将所有包含 `example` 的合法值都判错。报告键名本身也可能带业务信息，分享前仍应由用户判断。

## 综合决策

这三个项目可以做成小而完整的工具，分别服务表格交付、文件交付、项目配置。推荐优先级为 CSV 文本保真、文件交付校验、环境配置检查。需求证据足以支持开发可试用 MVP，尚不足以支持“需求很大”“会火”“比所有竞品更好”等结论。README 应主动列出上面的成熟替代品，说明选择本工具的具体理由和未覆盖的工作流。
