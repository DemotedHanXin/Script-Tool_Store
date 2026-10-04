# AI Assistant 模型列表超时补丁

脚本已经保存在 `D:\Codex_work\patch_jetbrains_ai_timeout.py`。

使用 Python 3 运行，不需要安装第三方包，也不需要编译 Java/Kotlin。
本机已有可用的 Python：`D:\work\anacounda3\python.exe`。
该脚本将当前已验证插件的模型列表加载超时从 2.5 秒改为 30 秒。

## 先处理 CLion

1. 正常退出 PyCharm、CLion 和 IntelliJ IDEA。脚本发现这些进程仍运行时会拒绝修改。
2. 打开 PowerShell，先运行只读检查：

```powershell
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide clion --check
```

3. 如果显示 `VERIFIED: original, 2.5 seconds`，运行：

```powershell
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide clion --apply
```

4. 显示 `PATCHED: 2500 ms -> 30000 ms` 后，正常启动 CLion，打开项目与 AI 聊天，等待模型列表加载。补丁修改已验证，但实际网络恢复效果仍需这一步确认。

如果系统提示找不到 `python`，将命令开头的 `python` 替换为：

```powershell
& "D:\work\anacounda3\python.exe"
```

## PyCharm 和 IDEA

先确认 CLion 恢复，再退出三个 IDE，并分别运行：

```powershell
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide pycharm --apply
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide idea --apply
```

## 撤销补丁

退出三个 IDE，按需运行：

```powershell
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide clion --restore
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide pycharm --restore
python "D:\Codex_work\patch_jetbrains_ai_timeout.py" --ide idea --restore
```

脚本会在目标 JAR 的同一目录保存原始备份：

`intellij.ml.llm.core.jar.codex-ai-timeout-2500ms.bak`

原插件的相对位置是：

`%APPDATA%\JetBrains\对应IDE2026.2\plugins\ml-llm\lib\modules\intellij.ml.llm.core.jar`

无需将脚本放进 IDE 安装目录，也不要手工编辑压缩 JAR。

## 范围和检查

- 默认运行或 `--check` 只读取状态，不修改文件。
- `--apply` 在备份、完整校验临时补丁文件后才替换目标 JAR。
- 只允许本次核实的目标类 SHA-256，其他版本会停止。
- 改动的是 `sipush 2500` 到 `sipush 30000`，字节码长度不变。
- 所有其他 JAR 条目的内容必须保持相同；带标准 JAR 签名的文件会拒绝修改。
- `--restore` 逐字节恢复原始 JAR；发现更新或额外改动时会停止，避免覆盖新版本。
- 不读取 API Key 或聊天历史，也不修改账号、代理和启动参数。
- 这是本地非官方补丁，插件更新或重装可能覆盖它。不要把此脚本用于其他版本或强行跳过哈希检查。
- 30 秒超时后仍会取消；该补丁延长等待时间，没有修改原插件对超时的处理方式。

交付时原安装文件未被改写。补丁与撤销已在临时副本上完成验证。
