# Multi-file / Directory Linting (PLAN.md Phase 3)

## Problem

`pyhdl-lint <path_to_hdl_file>` accepts exactly one file. Real projects have many
files across VHDL/Verilog/SystemVerilog; there's no way to lint a whole tree in one
invocation.

## Decisions

- **Single path arg: file or directory.** No new argument-parsing surface (no glob
  flags, no multiple positional args) — shells already expand globs before argv, and a
  directory argument covers the real need. Recursive discovery under a directory.
- **Directory scan silently skips non-HDL files** (`.md`, `.py`, etc. living in the
  same tree aren't errors) but an explicit single unsupported-extension file argument
  still errors exactly as today — these are different code paths, not unified, so the
  existing single-file behavior has zero regression risk.
- **Summary only for directories.** `Reporter.report_summary(total_files,
  total_violations)` already exists but is never called; wiring it up only for the
  directory path keeps single-file output byte-for-byte identical to today (nothing
  parsing current stdout breaks).
- **`main()` returns an exit code instead of calling `sys.exit()` internally.** This
  makes it testable in-process (a `sys.exit` call would kill the pytest process), and
  is also the technically correct shape for a `[project.scripts]` entry point — the
  generated console-script launcher already wraps the target callable in
  `sys.exit(main())` itself.

## Design

```python
def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: pyhdl-lint <file_or_directory_path>")
        return 1

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Error: Path {target} not found.")
        return 1

    reporter = Reporter()
    config = Config.load()

    if target.is_file():
        language = EXTENSION_TO_LANGUAGE.get(target.suffix.lower())
        if not language:
            print(f"Error: Unsupported file extension {target.suffix}")
            return 1
        engine = _load_engine(language)
        if not reporter.quiet:
            print(f"Running {len(engine.rules)} rules for {language}...")
        total_violations = _lint_file(target, language, engine, config, reporter)
        return 1 if total_violations else 0

    files = sorted(
        p for p in target.rglob("*")
        if p.is_file() and p.suffix.lower() in EXTENSION_TO_LANGUAGE
    )
    if not files:
        print(f"No VHDL/Verilog/SystemVerilog files found under {target}.")
        return 0

    engines: dict[str, Engine] = {}
    total_violations = 0
    for file_path in files:
        language = EXTENSION_TO_LANGUAGE[file_path.suffix.lower()]
        if language not in engines:
            engines[language] = _load_engine(language)
            if not reporter.quiet:
                print(f"Running {len(engines[language].rules)} rules for {language}...")
        total_violations += _lint_file(file_path, language, engines[language], config, reporter)

    reporter.report_summary(len(files), total_violations)
    return 1 if total_violations else 0


if __name__ == "__main__":
    sys.exit(main())
```

`_load_engine(language)` and `_lint_file(...)` are small extracted helpers (load rules
dir for a language; run + report for one file) shared by both branches to avoid
duplicating the load/run/report calls, without unifying the two branches' control flow.

## Testing

`tests/test_main.py`: monkeypatch `sys.argv`, call `main()` directly (now returns an
int, no process exit), assert the returned code and capture stdout (`capsys`) for:
single file with violations / clean / unsupported extension / nonexistent path;
directory with mixed-language files (asserts each language's engine loads once via a
call-count check or by asserting correct per-file violations aggregate); empty
directory; directory with no matching files.

## Out of scope

- No glob-flag or multiple-positional-arg support.
- No parallelization across files (out of scope for "real-world usability" here;
  revisit only if lint time on large trees becomes a real complaint).
- No change to `Engine`/`Parser`/rule classes.
