import sys
from parser import ConfigParser
from xml_converter import XMLConverter

def main():
    # Чтение входных данных из стандартного ввода
    #input_text = sys.stdin.read()
    input_lines = []
    print("Enter configuration data line by line. Type 'END' on a new line to finish:")

    while True:
        line = input()
        if line.strip().upper() == "END":  # Условие завершения
            break
        input_lines.append(line)

    input_text = "\n".join(input_lines)

    # Создаем парсер
    parser = ConfigParser()

    try:
        # Парсим текст на учебном конфигурационном языке
        parsed_data = parser.parse(input_text)

        # Преобразуем результат в XML
        converter = XMLConverter()
        xml_output = converter.convert(parsed_data)

        # Выводим XML
        print(xml_output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()