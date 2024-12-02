import unittest
import subprocess
import os
from xml.etree import ElementTree as ET
from xml_converter import XMLConverter


class TestParser(unittest.TestCase):
    #Тесты для синтаксического анализа parser.py.
    def setUp(self):
        self.tool_path = os.path.join(os.path.dirname(__file__), "parser.py")
        if not os.path.exists(self.tool_path):
            raise FileNotFoundError(f"Parser not found at {self.tool_path}")

    def run_tool(self, input_data):
        #Запускает parser.py через subprocess и возвращает стандартный вывод.
        result = subprocess.run(
            ["python", self.tool_path],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=10  # Ограничение времени выполнения на 5 секунд
        )
        if result.returncode != 0:
            raise RuntimeError(f"Parser execution failed with error: {result.stderr}")
        return result.stdout

    def test_single_line_comments(self):
        #Проверка обработки однострочных комментариев
        inputs = [
            "* Это комментарий\nvar x := 42;",
            "var y := 10; * Комментарий",
            "* Вложенный комментарий: * Вложенный текст\nvar z := 99;"
        ]
        expected_outputs = ["<variable name=\"x\">42</variable>",
                            "<variable name=\"y\">10</variable>",
                            "<variable name=\"z\">99</variable>"]
        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_arrays(self):
        #Проверка обработки массивов
        inputs = [
            "var array := {1, 2, 3};",
            "var data := {10, 20, 30, 40};",
            "var nested := {100, 200};"
        ]
        expected_outputs = [
            "<variable name=\"array\">1, 2, 3</variable>",
            "<variable name=\"data\">10, 20, 30, 40</variable>",
            "<variable name=\"nested\">100, 200</variable>"
        ]

        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_arrays_two(self):
        #Проверка обработки массивов
        inputs = [
            "var array := {7, 1, 10, 83, 0};",
            "var data := {1, 2};",
            "var nested := {100000, 9999999};"
        ]
        expected_outputs = [
            "<variable name=\"array\">7, 1, 10, 83, 0</variable>",
            "<variable name=\"data\">1, 2</variable>",
            "<variable name=\"nested\">100000, 9999999</variable>"
        ]

        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_values(self):
        #Проверка обработки чисел, строк и массивов
        inputs = [
            "var num := 42;",
            "var text := 'hello';",
            "var array := {5, 'text', 7};"
        ]
        expected_outputs = [
            "<variable name=\"num\">42</variable>",
            "<variable name=\"text\">hello</variable>",
            "<variable name=\"array\">5, text, 7</variable>"
        ]
        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_constant_declarations(self):
        #Проверка объявлений констант
        inputs = [
            "var const1 := 10;",
            "var const2 := 'constant';",
            "var const3 := {1, 2};"
        ]
        expected_outputs = [
            "<variable name=\"const1\">10</variable>",
            "<variable name=\"const2\">constant</variable>",
            "<variable name=\"const3\">1, 2</variable>"
        ]
        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_names(self):
        #Тест имен переменных
        inputs = [
            "var _validName := 42;",
            "var anotherName123 := 'hello';",
            "var myVar := {1, 2, 3};"
        ]
        expected_outputs = [
            "<variable name=\"_validName\">42</variable>",
            "<variable name=\"anotherName123\">hello</variable>",
            "<variable name=\"myVar\">1, 2, 3</variable>"
        ]
        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_constant_computations(self):
        #Проверка вычисления констант
        inputs = [
            "var x := 10;\n@[x]",
            "var y := 'test';\n@[y]",
            "var z := {100};\n@[z]"
        ]
        expected_outputs = [
            "<constant name=\"x\">10</constant>",
            "<constant name=\"y\">test</constant>",
            "<constant name=\"z\">100</constant>"
        ]
        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)

    def test_constant_computations_two(self):
        #Тест вычисления констант
        inputs = [
            "var x := 1;\n@[x]",
            "var y := 'wow';\n@[y]",
            "var z := {75};\n@[z]"
        ]
        expected_outputs = [
            "<constant name=\"x\">1</constant>",
            "<constant name=\"y\">wow</constant>",
            "<constant name=\"z\">75</constant>"
        ]
        for input_data, expected_output in zip(inputs, expected_outputs):
            xml_output = self.run_tool(input_data)
            self.assertIn(expected_output, xml_output)


class TestXMLConverter(unittest.TestCase):

    #Тесты для XMLConverter.
    def setUp(self):
        self.converter = XMLConverter()

    def test_conversion(self):
        data = {"variables": {"x": 42}, "constants": {"y": 43}}
        xml_output = self.converter.convert(data)

        expected_output = '''
        <configuration>
            <variables>
                <variable name="x">42</variable>
            </variables>
            <constants>
                <constant name="y">43</constant>
            </constants>
        </configuration>
        '''
        parsed_output = ET.fromstring(xml_output)
        parsed_expected = ET.fromstring(expected_output)
        self.assertTrue(self.compare_elements(parsed_output, parsed_expected))

    def compare_elements(self, elem1, elem2):
        #Сравнение двух XML-элементов
        if elem1.tag != elem2.tag or elem1.text.strip() != elem2.text.strip():
            return False
        if elem1.attrib != elem2.attrib:
            return False
        if len(elem1) != len(elem2):
            return False
        return all(self.compare_elements(c1, c2) for c1, c2 in zip(elem1, elem2))

if __name__ == "__main__":
    unittest.main()