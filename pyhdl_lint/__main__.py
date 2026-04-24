import sys
import os
from pyhdl_lint.core.engine import Engine

def main():
    if len(sys.argv) < 2:
        print("Usage: pyhdl-lint <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    # Determine language from extension
    ext = os.path.splitext(file_path)[1].lower()
    lang_map = {
        ".vhd": "vhdl",
        ".vhdl": "vhdl",
        ".v": "verilog",
        ".sv": "systemverilog"
    }

    language = lang_map.get(ext)
    if not language:
        print(f"Error: Unsupported file extension {ext}")
        sys.exit(1)

    from pyhdl_lint.core.reporter import Reporter
    from pyhdl_lint.utils.config import Config
    
    reporter = Reporter()
    config = Config.load()
    engine = Engine()
    
    # Load rules for the specific language
    base_path = os.path.dirname(os.path.dirname(__file__))
    rules_dir = os.path.join(base_path, "pyhdl_lint", "languages", language, "rules")
    
    engine.load_rules(rules_dir)
    
    if not reporter.quiet:
        print(f"Running {len(engine.rules)} rules for {language}...")
        
    violations = engine.run(file_path, language, config=config)
    reporter.report(file_path, violations)

    if violations:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
