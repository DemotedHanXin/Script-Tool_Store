"""Patch the verified AI Assistant model-list timeout from 2.5 s to 30 s.

Standard-library only. No network, credentials, or chat-history access.
Default mode is read-only. Supports only the exact class verified on this PC.
"""

import argparse
import csv
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


CLASS = (
    "com/intellij/ml/llm/core/providers/"
    "AiaThirdPartyLlmProviderClient$loadAvailableProfiles$2.class"
)
ORIGINAL_SHA256 = "f12e74a68e5468f8db783c15e0a8f6791376082b6305c06ed41377e662c563a1"
OFFSET = 0xE73  # Exact file offset in the hash-verified class, not in the JAR.
OLD = bytes.fromhex("11 09 c4")  # sipush 2500
NEW = bytes.fromhex("11 75 30")  # sipush 30000; same bytecode length and stack effect.
BACKUP_SUFFIX = ".codex-ai-timeout-2500ms.bak"
PROFILES = {
    "clion": "CLion2026.2",
    "pycharm": "PyCharm2026.2",
    "idea": "IntelliJIdea2026.2",
}
IDE_PROCESSES = {"clion64.exe", "pycharm64.exe", "idea64.exe"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def class_status(data):
    if digest(data) == ORIGINAL_SHA256 and data[OFFSET:OFFSET + 3] == OLD:
        return "original"
    if data[OFFSET:OFFSET + 3] == NEW:
        original = data[:OFFSET] + OLD + data[OFFSET + 3:]
        if digest(original) == ORIGINAL_SHA256:
            return "patched"
    raise RuntimeError("Unknown class/version: refusing to modify this plugin.")


def inspect_jar(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError("Duplicate JAR entries: refusing to modify.")
        if any(n.upper().startswith("META-INF/") and
               n.upper().endswith((".SF", ".RSA", ".DSA", ".EC")) for n in names):
            raise RuntimeError("Signed JAR detected: refusing to modify its signature.")
        return class_status(archive.read(CLASS))


def require_closed_ides():
    if os.name != "nt":
        raise RuntimeError("This script targets the verified Windows installation only.")
    tasklist = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/tasklist.exe"
    result = subprocess.run(
        [str(tasklist), "/FO", "CSV", "/NH"], capture_output=True,
        encoding="mbcs", errors="replace", check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    running = sorted({row[0].lower() for row in csv.reader(io.StringIO(result.stdout))
                      if row and row[0].lower() in IDE_PROCESSES})
    if running:
        raise RuntimeError("Close these IDEs first, then retry: " + ", ".join(running))


def verify_pair(original_path, patched_path):
    """Verify every uncompressed entry, allowing only the two intended bytes."""
    with zipfile.ZipFile(original_path) as original, zipfile.ZipFile(patched_path) as patched:
        if original.namelist() != patched.namelist() or original.comment != patched.comment:
            raise RuntimeError("JAR structure changed unexpectedly.")
        for entry in original.infolist():
            before = original.read(entry.filename)
            after = patched.read(entry.filename)
            if entry.filename == CLASS:
                if class_status(before) != "original" or class_status(after) != "patched":
                    raise RuntimeError("Unexpected target class state.")
                expected = before[:OFFSET] + NEW + before[OFFSET + 3:]
                if after != expected:
                    raise RuntimeError("Target class differs beyond the timeout patch.")
            elif before != after:
                raise RuntimeError("Unexpected change to JAR entry: " + entry.filename)


def temp_path(parent):
    descriptor, name = tempfile.mkstemp(prefix=".codex-ai-timeout-", suffix=".tmp", dir=parent)
    os.close(descriptor)
    return Path(name)


def apply_patch(jar):
    status = inspect_jar(jar)
    if status == "patched":
        print("Already patched: model-list timeout = 30 seconds; no changes.")
        return
    require_closed_ides()
    source_hash = file_digest(jar)
    backup = jar.with_name(jar.name + BACKUP_SUFFIX)
    if backup.exists():
        if file_digest(backup) != source_hash:
            raise RuntimeError("Existing backup differs from current original; refusing to overwrite it.")
    else:
        try:
            with jar.open("rb") as source, backup.open("xb") as target:
                shutil.copyfileobj(source, target)
                target.flush()
                os.fsync(target.fileno())
        except FileExistsError:
            raise RuntimeError("Backup appeared concurrently; retry after checking it.")
        if file_digest(backup) != source_hash:
            raise RuntimeError("Backup verification failed. Original JAR has not been modified.")

    temporary = temp_path(jar.parent)
    try:
        with zipfile.ZipFile(jar) as source, zipfile.ZipFile(temporary, "w") as target:
            target.comment = source.comment
            for entry in source.infolist():
                data = source.read(entry.filename)
                if entry.filename == CLASS:
                    if class_status(data) != "original":
                        raise RuntimeError("Source changed while patching.")
                    data = data[:OFFSET] + NEW + data[OFFSET + 3:]
                target.writestr(entry, data)
        verify_pair(backup, temporary)
        if file_digest(jar) != source_hash:
            raise RuntimeError("Original JAR changed concurrently; replacement cancelled.")
        require_closed_ides()
        shutil.copymode(jar, temporary)
        os.replace(temporary, jar)
        print("PATCHED: 2500 ms -> 30000 ms (model-list loading only).")
        print("Backup:", backup)
        print("Start the IDE and verify the model selector.")
    finally:
        if temporary.exists():
            temporary.unlink()


def restore_backup(jar):
    require_closed_ides()
    backup = jar.with_name(jar.name + BACKUP_SUFFIX)
    if not backup.is_file():
        raise RuntimeError("Backup not found: " + str(backup))
    if inspect_jar(backup) != "original":
        raise RuntimeError("Backup is not the verified original class.")
    source_hash = file_digest(jar)
    if source_hash == file_digest(backup):
        print("Already restored; no changes.")
        return
    if inspect_jar(jar) != "patched":
        raise RuntimeError("Current JAR is not this script's patch; refusing to overwrite it.")
    verify_pair(backup, jar)
    temporary = temp_path(jar.parent)
    try:
        shutil.copy2(backup, temporary)
        if file_digest(temporary) != file_digest(backup):
            raise RuntimeError("Restore-copy verification failed.")
        if file_digest(jar) != source_hash:
            raise RuntimeError("Current JAR changed concurrently; restore cancelled.")
        require_closed_ides()
        os.replace(temporary, jar)
        print("RESTORED: original JAR restored exactly; backup retained.")
    finally:
        if temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--ide", choices=PROFILES, help="IDE profile (default: clion)")
    selection.add_argument("--jar", type=Path, help="Explicit JAR path, for testing a copy")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Inspect only (the default)")
    mode.add_argument("--apply", action="store_true", help="Back up and apply the 30-second patch")
    mode.add_argument("--restore", action="store_true", help="Restore the original backup")
    args = parser.parse_args()
    jar = args.jar
    if jar is None:
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise RuntimeError("APPDATA is unavailable; use --jar with an explicit path.")
        jar = Path(appdata) / "JetBrains" / PROFILES[args.ide or "clion"] / (
            "plugins/ml-llm/lib/modules/intellij.ml.llm.core.jar")
    jar = jar.resolve(strict=True)
    print("Target:", jar)
    if args.apply:
        apply_patch(jar)
    elif args.restore:
        restore_backup(jar)
    else:
        status = inspect_jar(jar)
        print("VERIFIED:", "original, 2.5 seconds" if status == "original" else "patched, 30 seconds")
        print("Read-only check complete. No files changed.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, KeyError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print("STOP:", error, file=sys.stderr)
        sys.exit(1)
