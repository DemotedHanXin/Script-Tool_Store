# Script-Tool_Store

[English](README.EN.md) | [简体中文](README.md)

A personal archive of Windows tools and scripts. It contains a JetBrains subscription management program and a troubleshooting patch for AI Assistant model-list timeouts.

## Tools at a glance

| Directory | Purpose | Contents |
| --- | --- | --- |
| [jetbrains-crack-toolbox_2.3.0_win](./jetbrains-crack-toolbox_2.3.0_win/) | Program archived for managing JetBrains subscriptions and licenses | Windows installer and executable |
| [jetbrains_AI_Assistant](./jetbrains_AI_Assistant/) | Extends the wait time for fetching third-party AI Assistant models | Python script and Markdown documentation |

## Repository layout

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

`.idea/` contains IDE project settings created while editing this repository. It is not required to run either tool.

## JetBrains subscription management program

Directory: `jetbrains-crack-toolbox_2.3.0_win/`.

This directory archives a program for managing JetBrains software subscriptions and licenses. Choose the installer or executable as needed, and refer to the program interface for its available operations.

| File | Description | Local file version metadata |
| --- | --- | --- |
| `jetbrains-crack-toolbox_2.3.0_x64-setup.exe` | Windows x64 installer | `2.3.0` |
| `jetbrains-crack-toolbox.exe` | Program executable | `2.0.0` |

**Version note:** The versions above come from the files' Windows version properties. The directory name includes `2.3.0`, but the two executables have different version metadata. The standalone executable should not be assumed to be version 2.3.0.

This directory contains binaries only; it does not include source code or upstream usage documentation. This README records the files and their intended purpose. It does not verify the program's specific features, supported products, or the relationship between the installer and standalone executable.

## AI Assistant model-list timeout patch

Script: [patch_jetbrains_ai_timeout.py](./jetbrains_AI_Assistant/patch_jetbrains_ai_timeout.py).

### Problem addressed

In the environment investigated, AI Assistant in PyCharm, CLion, and IntelliJ IDEA showed these symptoms:

- An API was configured and the connection test succeeded.
- The model list in AI Chat was empty and showed “No model.”
- Re-entering the API settings did not restore the models.

The investigated plugin version allowed only **2.5 seconds** to fetch a third-party model list, while requests through the proxy took about **3.5–3.8 seconds**. The plugin cancelled the request before receiving the list, so the models were not displayed.

The script changes this timeout constant from **2,500 ms to 30,000 ms**, allowing up to **30 seconds** for model-list retrieval. It changes the wait for fetching the model list; it does not change chat response timeouts or improve network speed.

**Verified on this PC:** On 2026-10-05, after applying the patch separately, the user confirmed that model loading recovered in CLion, PyCharm, and IntelliJ IDEA.

### Requirements and supported scope

- Windows with Python 3. The script uses only the standard library; it needs no third-party Python packages and no Java/Kotlin compilation.
- The verified AI Assistant plugin version is `262.10968.169`. By default, the script targets the IDE configuration directories below.
- The script checks the target class SHA-256 and modifies only the verified class. Matching version labels alone are not sufficient.
- Before applying or restoring a patch, fully exit **CLion, PyCharm, and IntelliJ IDEA**. The script checks whether these IDE processes are running.

| `--ide` value | Default configuration directory |
| --- | --- |
| `clion` | `%APPDATA%\JetBrains\CLion2026.2` |
| `pycharm` | `%APPDATA%\JetBrains\PyCharm2026.2` |
| `idea` | `%APPDATA%\JetBrains\IntelliJIdea2026.2` |

### Quick start

Open PowerShell and change to the repository root:

```powershell
Set-Location "E:\My_Library\Script-Tool_Store"
python --version
```

The commands below assume the repository root is the current directory. If you move the repository, update only the `Set-Location` path.

**1. Read-only check**

```powershell
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide clion --check
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide pycharm --check
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide idea --check
```

`VERIFIED: original, 2.5 seconds` means the plugin is the supported original and is ready to patch. `VERIFIED: patched, 30 seconds` means the patch is already applied. A read-only check does not modify files.

**2. Apply the patch**

Exit all three IDEs, then run the command for each IDE you want to patch:

```powershell
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide clion --apply
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide pycharm --apply
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide idea --apply
```

`PATCHED: 2500 ms -> 30000 ms` confirms the file was changed; the terminal also prints the backup path. `Already patched` means no further change is needed.

**3. Check model loading**

Start the IDE normally, open a project and AI Chat, then wait for the model list and check the model selector. You do not need to re-enter the API settings. If a request still takes more than 30 seconds, or there is another network or API issue, further troubleshooting may be needed.

### Patched file and backup

For the selected IDE, the script modifies this plugin file inside its configuration directory:

```text
plugins\ml-llm\lib\modules\intellij.ml.llm.core.jar
```

For example, CLion's full path is:

```text
%APPDATA%\JetBrains\CLion2026.2\plugins\ml-llm\lib\modules\intellij.ml.llm.core.jar
```

Paste the containing folder path into File Explorer's address bar to locate it. Before changing the JAR, the script creates a backup in the same directory:

```text
intellij.ml.llm.core.jar.codex-ai-timeout-2500ms.bak
```

The patch changes only the timeout constant in `AiaThirdPartyLlmProviderClient$loadAvailableProfiles$2.class` inside the JAR. The script checks every other entry's contents and replaces the original only after the temporary patched archive passes verification.

The script does not read API keys or chat history, and does not change project files, accounts, proxy settings, or IDE startup options.

### Restore the original plugin

Exit all three IDEs, then run the command for each IDE you want to restore:

```powershell
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide clion --restore
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide pycharm --restore
python ".\jetbrains_AI_Assistant\patch_jetbrains_ai_timeout.py" --ide idea --restore
```

The script checks the backup and current plugin, restores the original JAR byte for byte when they match, and keeps the backup. If the plugin has been updated or contains additional changes, the script stops to avoid overwriting them.

### Options and common messages

| Option or message | Meaning / action |
| --- | --- |
| No operation option / `--check` | Read-only inspection; CLion is the default if no IDE is specified |
| `--apply` | Back up the JAR and apply the 30-second patch |
| `--restore` | Restore the backup in the same directory |
| `--ide clion` / `pycharm` / `idea` | Select one IDE; each IDE has its own plugin copy |
| `--jar` | Specify a JAR path, mainly for testing a copy; mutually exclusive with `--ide` and subject to the same compatibility checks |
| `--help` | Show command-line help |
| `Close these IDEs first` | Exit the IDEs named in the message, then retry |
| `Unknown class/version` | This plugin is outside the script's verified scope; re-check its version and implementation |
| `Signed JAR detected` | The script detected a standard JAR signature and refused to modify it |
| `Backup not found` | The original backup is missing, so `--restore` cannot proceed |
| Existing backup differs or extra changes are detected | Keep the current JAR and backup; check the version before proceeding |

### Maintenance

- Applying the patch changes the plugin once. The IDE uses the modified plugin on later launches and does not run this Python script at startup.
- Keep the script and `.bak` files for future checks or restoration. The script can move with the repository; backups should stay beside their corresponding JARs.
- An AI Assistant plugin update or reinstall may overwrite the patch. Run `--check` after an update. If the class no longer matches, re-verify compatibility; do not bypass the hash check.
- The patch retains a 30-second timeout. It does not change how the original plugin handles a timeout.

## Troubleshooting notes

- [JetBrains AI diagnostic findings](./jetbrains_AI_Assistant/JetBrains-AI-诊断结论.md): original symptoms, latency measurements, exception chain, and investigation.
- [JetBrains AI patch instructions](./jetbrains_AI_Assistant/JetBrains-AI-补丁使用说明.md): instructions from the initial delivery.

These two documents preserve the original investigation and delivery state. Some commands still use the former `D:\Codex_work` path. Use this README for the current repository path and final recovery status.
