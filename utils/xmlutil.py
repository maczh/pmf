import xml.etree.ElementTree as ET
from typing import Dict, IO, Any, Optional


def decode_xml_to_map(xml_file: IO[Any]) -> Dict[str, str]:
    """将XML文件解析为一级子节点的键值对（忽略包含子节点的节点）"""
    result = {}
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    for child in root:
        # 检查子节点是否有子节点，有则跳过
        if len(child) == 0:
            result[child.tag] = child.text.strip() if child.text else ""
    return result


def encode_xml_from_map(data: Dict[str, str], root_name: str) -> str:
    """将字典转换为XML字符串"""
    root = ET.Element(root_name)
    for key, value in data.items():
        child = ET.SubElement(root, key)
        child.text = value
    
    # 生成XML字符串（包含声明）
    ET.indent(root)  # 格式化缩进
    return ET.tostring(root, encoding='unicode', xml_declaration=True)