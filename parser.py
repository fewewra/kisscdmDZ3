from config_parser.exceptions import SyntaxError
import re

class ConfigParser:
    def __init__(self):
        self.var_pattern = re.compile(r"var\s+([_a-zA-Z][_a-zA-Z0-9]*)\s*:=\s*(.+);")
        self.constant_pattern = re.compile(r"@\[([_a-zA-Z][_a-zA-Z0-9]*)\]")
        self.comment_pattern = re.compile(r"\*.*")
        self.array_pattern = re.compile(r"\{(.+?)\}")
        self.string_pattern = re.compile(r"'([^']*)'")
        self.number_pattern = re.compile(r"\b\d+\b")

    def parse(self, text):
        lines = text.splitlines()
        parsed_data = {"variables": {}, "constants": {}}

        for line in lines:
            line = line.strip()

            # Пропускаем комментарии
            if self.comment_pattern.match(line):
                continue

            # Обработка переменных
            var_match = self.var_pattern.match(line)
            if var_match:
                var_name, var_value = var_match.groups()
                parsed_data["variables"][var_name] = self.parse_value(var_value)
                continue

            # Обработка констант
            const_match = self.constant_pattern.match(line)
            if const_match:
                const_name = const_match.groups()[0]
                if const_name in parsed_data["variables"]:
                    parsed_data["constants"][const_name] = parsed_data["variables"][const_name]
                else:
                    raise SyntaxError(f"Undefined variable '{const_name}' in constant expression.")

        return parsed_data

    def parse_value(self, value):
        if self.number_pattern.match(value):
            return int(value)
        elif self.string_pattern.match(value):
            return value.strip("'")
        elif self.array_pattern.match(value):
            items = value.strip("{}").split(",")
            return [self.parse_value(item.strip()) for item in items]
        else:
            raise SyntaxError(f"Invalid value: {value}")


# Вспомогательная функция для интеграции
def parse_config(input_text):
    parser = ConfigParser()
    return parser.parse(input_text)


if __name__ == "__main__":
    import sys
    from xml_converter import XMLConverter

    input_text = sys.stdin.read().strip()
    if not input_text:
        print("No input provided", file=sys.stderr)
        sys.exit(1)

    try:
        parsed_data = parse_config(input_text)
        converter = XMLConverter()
        xml_output = converter.convert(parsed_data)
        print(xml_output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
