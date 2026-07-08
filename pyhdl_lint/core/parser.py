from hdlConvertor import HdlConvertor
from hdlConvertor._hdlConvertor import PyHdlLanguageEnum, ParseException

class Parser:
    """
    Parser class utilizing hdlConvertor to build a universal AST.
    """
    def __init__(self, language):
        self.language = language

    def get_context(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Map input language to PyHdlLanguageEnum
        lang_map = {
            "vhdl": PyHdlLanguageEnum.VHDL_2008,
            "verilog": PyHdlLanguageEnum.VERILOG_2005,
            "systemverilog": PyHdlLanguageEnum.SYSTEM_VERILOG_2017
        }
        lang_enum = lang_map.get(self.language.lower(), PyHdlLanguageEnum.VHDL_2008)
        
        ast = None
        parse_error = None
        try:
            converter = HdlConvertor()
            # parse takes (filenames, language, incdirs)
            ast = converter.parse(file_path, lang_enum, [])
        except ParseException as e:
            parse_error = str(e)
        
        return {
            "file_path": file_path,
            "content": content,
            "lines": content.splitlines(),
            "language": self.language,
            "ast": ast,
            "parse_error": parse_error
        }
