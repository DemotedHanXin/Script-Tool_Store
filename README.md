# Script-Tool_Store

[English](README.EN.md) | 简体中文

个人 Windows 工具与脚本归档，用于保存 JetBrains 软件订阅管理程序，以及 AI Assistant 模型列表加载超时问题的修复脚本和排查记录。

## 工具一览

| 目录 | 用途 | 文件类型 |
| --- | --- | --- |
| [jetbrains-crack-toolbox_2.3.0_win](./jetbrains-crack-toolbox_2.3.0_win/) | JetBrains 软件订阅、授权管理程序 | Windows 安装包和可执行程序 |
| [jetbrains_AI_Assistant](./jetbrains_AI_Assistant/) | 延长 AI Assistant 获取第三方模型列表的等待时间，处理因超时导致的“无模型”问题 | Python 脚本和 Markdown 文档 |

## 目录结构

```text
Script-Tool_Store/
├── README.md
├── README.en.md
├── jetbrains-crack-toolbox_2.3.0_win/
│   ├── jetbrains-crack-toolbox_2.3.0_x64-setup.exe
│   └── jetbrains-crack-toolbox.exe
└── jetbrains_AI_Assistant/
    ├── patch_jetbrains_ai_timeout.py
    ├── JetBrains-AI-补丁使用说明.md
    └── JetBrains-AI-诊断结论.md
```

`.idea/` 是编辑本仓库时生成的 IDE 项目配置，不属于工具运行所需文件。

## JetBrains 订阅管理程序

目录：`jetbrains-crack-toolbox_2.3.0_win/`。

该目录按 JetBrains 软件订阅、授权管理用途归档，保留原程序名称。使用时根据需要选择安装程序或现有可执行文件，在程序界面中查看具体操作说明。

| 文件 | 说明 | 本地文件版本信息 |
| --- | --- | --- |
| `jetbrains-crack-toolbox_2.3.0_x64-setup.exe` | Windows x64 安装程序 | `2.3.0` |
| `jetbrains-crack-toolbox.exe` | 程序可执行文件 | `2.0.0` |

**版本说明：** 上表版本来自两个 EXE 的文件属性。虽然目录名称包含 `2.3.0`，两份文件的版本元数据并不一致，不能据此认定独立 EXE 也是 2.3.0。

当前目录仅包含二进制程序，没有源码或上游使用文档。本 README 记录文件用途与入口，未验证程序的具体管理功能、支持产品范围或两个文件之间的打包关系。

## AI Assistant 模型列表超时补丁

脚本：[patch_jetbrains_ai_timeout.py](./jetbrains_AI_Assistant/patch_jetbrains_ai_timeout.py)。

### 处理的问题

在已排查的环境中，PyCharm、CLion 和 IntelliJ IDEA 的 AI Assistant 会出现以下现象：

- 已配置 API，测试连接显示成功。
- AI 聊天中的模型列表为空，显示“无模型”。
- 重新填写 API 后仍无法加载模型。

原因是该版本插件获取第三方模型列表时设置了 **2.5 秒**的等待上限，而当时经代理访问接口需要约 **3.5～3.8 秒**。模型列表请求提前被取消，界面因此无法取得可用模型。

脚本将这一处超时常量从 **2500 毫秒改为 30000 毫秒**，让模型列表请求最多等待 **30 秒**。它延长的是获取模型列表的等待时间，不是聊天生成回复的超时，也不会提高网络速度。

**本机验证结果：** 2026-10-05，分别应用补丁后，CLion、PyCharm 和 IntelliJ IDEA 均已由使用者确认恢复模型加载。

### 使用条件与适用范围

- Windows，已安装 Python 3；脚本只使用标准库，无需安装第三方 Python 包或编译 Java/Kotlin。
- 本次验证的 AI Assistant 插件版本为 `262.10968.169`，默认目标为下表中的 IDE 配置目录。
- 脚本使用目标类的 SHA-256 检查兼容性，只有与本次验证一致的类才能修改；版本名称相同也不能代替这项检查。
- 应用或恢复补丁前，正常退出 **CLion、PyCharm 和 IntelliJ IDEA**。脚本会检查这些 IDE 的运行进程。

| `--ide` 参数 | 默认配置目录 |
| --- | --- |
| `clion` | `%APPDATA%\JetBrains\CLion2026.2` |
| `pycharm` | `%APPDATA%\JetBrains\PyCharm2026.2` |
| `idea` | `%APPDATA%\JetBrains\IntelliJIdea2026.2` |

### 快速使用

打开 PowerShell，进入本仓库根目录：

```powershell
Set-Location "E:\My_Library\Script-Tool_Store"
python --version
```

以下命令均以仓库根目录为当前目录。以后移动仓库，只需调整 `Set-Location` 的路径。

**1. 只读检查**

```powershell
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide clion --check
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide pycharm --check
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide idea --check
```

`VERIFIED: original, 2.5 seconds` 表示当前是可修改的原版；`VERIFIED: patched, 30 seconds` 表示已应用补丁。只读检查不会修改文件。

**2. 应用补丁**

退出三个 IDE 后，根据需要执行对应命令：

```powershell
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide clion --apply
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide pycharm --apply
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide idea --apply
```

显示 `PATCHED: 2500 ms -> 30000 ms` 表示文件修改成功，终端同时会显示备份位置。显示 `Already patched` 表示无需重复修改。

**3. 验证模型加载**

正常启动对应 IDE，打开项目及 AI 聊天，等待模型列表加载并检查模型下拉框。无需重新填写 API。若请求仍然超过 30 秒，或存在其他网络、接口问题，仍需继续排查。

### 修改位置与备份

脚本修改所选 IDE 配置目录内的这个插件文件：

```text
plugins\ml-llm\lib\modules\intellij.ml.llm.core.jar
```

例如 CLion 的完整位置为：

```text
%APPDATA%\JetBrains\CLion2026.2\plugins\ml-llm\lib\modules\intellij.ml.llm.core.jar
```

可以将上述路径的文件夹部分粘贴到资源管理器地址栏查看。修改前，脚本会在原 JAR 的同一目录创建备份：

```text
intellij.ml.llm.core.jar.codex-ai-timeout-2500ms.bak
```

补丁只修改 JAR 内 `AiaThirdPartyLlmProviderClient$loadAvailableProfiles$2.class` 的超时常量。其他文件条目的内容会逐一校验，临时补丁文件通过校验后才替换原文件。

脚本不读取 API 密钥或聊天历史，不修改项目代码、账号、代理配置和 IDE 启动参数。

### 恢复原插件

退出三个 IDE，根据需要运行：

```powershell
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide clion --restore
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide pycharm --restore
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide idea --restore
```

恢复时会检查原备份和当前插件，确认兼容后逐字节恢复原始 JAR，并保留备份。如果插件已更新或出现额外改动，脚本会停止，避免覆盖其他内容。

### 参数与常见提示

| 参数或提示 | 含义 / 处理方式 |
| --- | --- |
| 不加操作参数 / `--check` | 只读检查；未指定 IDE 时默认检查 CLion |
| `--apply` | 备份并应用 30 秒补丁 |
| `--restore` | 使用同目录备份恢复原文件 |
| `--ide clion` / `pycharm` / `idea` | 选择一个 IDE；每个 IDE 的插件副本分别处理 |
| `--jar` | 显式指定 JAR，主要用于测试副本；与 `--ide` 互斥，仍需通过同样的兼容性检查 |
| `--help` | 查看命令行帮助 |
| `Close these IDEs first` | 退出提示中列出的 IDE，再重试 |
| `Unknown class/version` | 当前插件不在脚本支持范围内，需重新核实版本和实现 |
| `Signed JAR detected` | 检测到标准 JAR 签名，脚本拒绝修改 |
| `Backup not found` | 缺少原始备份，无法使用 `--restore` 恢复 |
| 提示现有备份不同或文件被额外修改 | 保留当前文件与备份，核对版本后再处理 |

### 保存与维护

- 补丁是一次性文件修改。IDE 每次启动时直接使用修改后的插件，不会调用这个 Python 脚本。
- 建议保留脚本和 `.bak` 备份，方便以后检查、恢复。脚本可以随仓库移动；备份应留在对应 JAR 的目录中。
- 这是本地补丁，插件更新或重装可能覆盖它。更新后先执行 `--check`；不兼容时需重新验证，不能跳过哈希检查。
- 该补丁保留 30 秒超时，并未改变原插件对超时取消的处理逻辑。

## 排查记录与补充说明

- [JetBrains AI 诊断结论](./jetbrains_AI_Assistant/JetBrains-AI-诊断结论.md)：原始问题、延迟测量、异常链及定位过程。
- [JetBrains AI 补丁使用说明](./jetbrains_AI_Assistant/JetBrains-AI-补丁使用说明.md)：初次交付时的操作说明。

这两份文档保留了早期排查和交付时的状态，部分命令仍使用原来的 `D:\Codex_work` 路径。当前仓库的运行路径及最终恢复情况以本 README 为准。
