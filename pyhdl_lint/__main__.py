import sys
from pathlib import Path
from typing import Dict

from pyhdl_lint.core.engine import Engine
from pyhdl_lint.core.reporter import Reporter
from pyhdl_lint.utils.config import Config

EXTENSION_TO_LANGUAGE = {
    ".vhd": "vhdl",
    ".vhdl": "vhdl",
    ".v": "verilog",
    ".sv": "systemverilog",
}

def _load_engine(language: str) -> Engine:
    engine = Engine()
    rules_dir = Path(__file__).parent / "languages" / language / "rules"
    engine.load_rules(rules_dir)
    return engine

def _lint_file(file_path: Path, language: str, engine: Engine, config: Config, reporter: Reporter) -> int:
    violations = engine.run(file_path, language, config=config)
    reporter.report(file_path, violations)
    return len(violations)

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

    engines: Dict[str, Engine] = {}
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
