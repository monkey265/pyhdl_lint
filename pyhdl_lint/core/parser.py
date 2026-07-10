from pathlib import Path
from typing import Optional

from hdlConvertor import HdlConvertor
from hdlConvertor._hdlConvertor import PyHdlLanguageEnum, ParseException

from pyhdl_lint.core.rule_base import LintContext

LANGUAGE_TO_HDL_ENUM = {
    "vhdl": PyHdlLanguageEnum.VHDL_2008,
    "verilog": PyHdlLanguageEnum.VERILOG_2005,
    "systemverilog": PyHdlLanguageEnum.SYSTEM_VERILOG_2017,
}

class Parser:
    """
    Parser class utilizing hdlConvertor to build a universal AST.
    """
    def __init__(self, language: str) -> None:
        self.language = language

    def get_context(self, file_path: Path) -> LintContext:
        content = file_path.read_text(encoding="utf-8")

        lang_enum = LANGUAGE_TO_HDL_ENUM.get(self.language.lower(), PyHdlLanguageEnum.VHDL_2008)

        ast: Optional[object] = None
        parse_error: Optional[str] = None
        try:
            converter = HdlConvertor()
            # parse takes (filenames, language, incdirs)
            ast = converter.parse(str(file_path), lang_enum, [])
        except ParseException as e:
            parse_error = str(e)

        return LintContext(
            file_path=file_path,
            content=content,
            lines=content.splitlines(),
            language=self.language,
            ast=ast,
            parse_error=parse_error,
        )
