class Parser:
    """
    Base parser class. In future this will use
    libraries like hdlConvertor or a custom lexer.
    """
    def __init__(self, language):
        self.language = language

    def get_context(self, file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        
        # In the future, add tokenization or AST generation here
        return {
            "file_path": file_path,
            "content": content,
            "lines": content.splitlines(),
            "language": self.language
        }
