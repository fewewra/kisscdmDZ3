import xml.etree.ElementTree as ET
from xml.dom import minidom


class XMLConverter:
    def convert(self, data):
        """
        Преобразует данные из словаря в форматированный XML.
        :param data: Словарь с ключами 'variables' и 'constants'.
        :return: Отформатированный XML как строка.
        """
        root = ET.Element("configuration")

        # Обработка переменных
        variables_element = ET.SubElement(root, "variables")
        for name, value in data["variables"].items():
            var_element = ET.SubElement(variables_element, "variable", name=name)
            var_element.text = self._format_value(value)

        # Обработка констант
        constants_element = ET.SubElement(root, "constants")
        for name, value in data["constants"].items():
            const_element = ET.SubElement(constants_element, "constant", name=name)
            const_element.text = self._format_value(value)

        # Преобразуем в строку с помощью minidom для форматирования
        rough_string = ET.tostring(root, encoding="unicode")
        parsed = minidom.parseString(rough_string)
        formatted_xml = parsed.toprettyxml(indent="    ")

        return formatted_xml

    def _format_value(self, value):
        """
        Форматирует значение для XML.
        Если это массив, преобразует его в строку через запятую.
        Если это строка, убирает лишние кавычки.
        """
        if isinstance(value, list):  # Если это массив
            return ', '.join(map(str, value))
        elif isinstance(value, str):  # Если это строка
            return value.strip("'")  # Убираем одиночные кавычки
        return str(value)  # Для чисел и других типов
