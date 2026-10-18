#!/usr/bin/env python3
"""Validate aggregate metadata against Git's index and render its catalog."""

import argparse
import configparser
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(*args, cwd=None):
    return subprocess.check_output(["git", *args], cwd=cwd or ROOT, text=True).strip()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(checkouts=False):
    manifest = json.loads((ROOT / "libraries.json").read_text())
    require(manifest["schema_version"] == 1, "unsupported manifest version")
    libraries = manifest["libraries"]
    require(bool(libraries), "empty catalog")
    modules = configparser.ConfigParser(interpolation=None, strict=True)
    modules.read(ROOT / ".gitmodules")
    declared = {}
    for section in modules.sections():
        match = re.fullmatch(r'submodule "([a-zA-Z0-9_.-]+)"', section)
        require(match is not None, f"invalid submodule section: {section}")
        entry = modules[section]
        path = entry["path"]
        require(path not in declared, f"duplicate submodule path: {path}")
        require("branch" not in entry, f"use pinned gitlinks, not branch tracking: {path}")
        declared[path] = (match.group(1), entry["url"])
    links = {}
    for row in git("ls-files", "--stage", "-z").split("\0"):
        if not row:
            continue
        metadata, path = row.split("\t", 1)
        mode, sha, stage = metadata.split()
        require(stage == "0", f"unresolved index entry: {path}")
        if mode == "160000":
            links[path] = sha
    names, paths = set(), set()
    for item in libraries:
        name, path = item["name"], item["path"]
        require(re.fullmatch(r"[A-Za-z0-9_.-]+", name), f"invalid name: {name}")
        require(name not in names and path not in paths, f"duplicate catalog entry: {name}")
        names.add(name)
        paths.add(path)
        parts = PurePosixPath(path).parts
        require(not path.startswith("/") and ".." not in parts, f"unsafe path: {path}")
        require(re.fullmatch(r"[a-zA-Z0-9_./-]+", path), f"invalid path: {path}")
        require(len(parts) >= 3 and parts[0] == item["language"], f"language mismatch: {path}")
        require("/".join(parts[1:-1]) == item["domain"], f"domain mismatch: {path}")
        require(re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git", item["repository"]), f"invalid repository URL: {name}")
        require(item["kind"] in ("containers", "client", "library", "sdk"), f"invalid kind: {name}")
        require(declared.get(path) == (name, item["repository"]), f"submodule mismatch: {path}")
        require(path in links, f"missing gitlink: {path}")
        license_file = item["license_file"]
        require(license_file is None or re.fullmatch(r"[A-Za-z0-9_.-]+", license_file), f"unsafe license path: {name}")
        if checkouts:
            directory = ROOT / path
            require((directory / ".git").exists(), f"uninitialized checkout: {path}")
            require(git("rev-parse", "HEAD", cwd=directory) == links[path], f"checkout differs from gitlink: {path}")
            require(not git("status", "--porcelain", cwd=directory), f"dirty checkout: {path}")
            if item["language"] == "go":
                content = (directory / "go.mod").read_text()
                match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
                require(match is not None and match.group(1) == item["module"], f"Go module mismatch: {name}")
            if license_file:
                require((directory / license_file).is_file(), f"missing declared license: {name}")
    require(paths == set(declared) == set(links), "catalog, .gitmodules and gitlinks must have identical paths")
    return libraries


def render(libraries):
    lines = ["# 开发库目录", "", "由 `libraries.json` 生成；执行 `make catalog` 更新。源码版本以聚合仓库 gitlink 为准。", "", "状态统一为已收录，组件功能与生产质量仍以各仓库的版本和测试证据为准。", ""]
    for language in sorted({item["language"] for item in libraries}):
        lines += [f"## {language}", "", "| 领域 | 库 | 类型 | 包路径 | 许可证文件 |", "|---|---|---|---|---|"]
        for item in sorted((x for x in libraries if x["language"] == language), key=lambda x: x["path"]):
            name = f'[{item["name"]}]({item["repository"].removesuffix(".git")}) · [源码]({item["path"]})'
            license_info = f'[{item["license_file"]}]({item["path"]}/{item["license_file"]})' if item["license_file"] else "未发现根许可证文件，待核对"
            module = f'`{item["module"]}`' if item["module"] else "见组件说明"
            lines.append(f'| {item["domain"]} | {name} | {item["kind"]} | {module} | {license_info} |')
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "check"))
    parser.add_argument("--checkouts", action="store_true")
    args = parser.parse_args()
    try:
        libraries = validate(args.checkouts)
        expected = render(libraries)
        catalog = ROOT / "CATALOG.md"
        if args.command == "generate":
            catalog.write_text(expected)
        else:
            require(catalog.exists() and catalog.read_text() == expected, "CATALOG.md drift: run make catalog")
        print(f"PASS: {len(libraries)} libraries; catalog, gitlinks and metadata consistent" + ("; checkouts verified" if args.checkouts else ""))
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, configparser.Error) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
