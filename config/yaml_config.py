from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Union
import yaml
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
# /d:/Projects/python/test1/test01.py
# 读取同目录下的 test01.yml，解析为对象模型并以 JSON 输出



@dataclass
class YamlConfig:
    """
    通用的 YAML 对象模型。
    _value 可以是 dict / list / 原始类型，提供属性访问和 to_primitive() 转回原生结构。
    """
    _value: Any

    @classmethod
    def from_obj(cls, obj: Any) -> "YamlConfig":
        if isinstance(obj, dict):
            return cls({k: cls.from_obj(v) for k, v in obj.items()})
        if isinstance(obj, list):
            return cls([cls.from_obj(v) for v in obj])
        return cls(obj)

    def to_primitive(self) -> Any:
        if isinstance(self._value, dict):
            return {k: v.to_primitive() for k, v in self._value.items()}
        if isinstance(self._value, list):
            return [v.to_primitive() for v in self._value]
        return self._value

    def __getattr__(self, name: str) -> Any:
        # 允许通过属性访问映射中的键：model.somekey
        if isinstance(self._value, dict) and name in self._value:
            return self._value[name]
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!s}")

    def __repr__(self) -> str:
        return f"{self._value!r}"


def load_yaml_config(path: Union[str, Path]) -> YamlConfig:
    """
    Load YAML from a local file path or an http/https URL and return a YamlConfig.
    Supports using 'requests' if available, otherwise falls back to urllib.
    """
    import urllib.parse

    path_str = str(path)
    parsed = urllib.parse.urlparse(path_str)

    # URL case
    if parsed.scheme in ("http", "https"):
        try:
            # prefer requests if installed
            import requests  # type: ignore

            resp = requests.get(path_str, timeout=10)
            resp.raise_for_status()
            text = resp.text
        except Exception:
            # fallback to urllib
            try:

                req = Request(path_str, headers={"User-Agent": "python-urllib/3"})
                with urlopen(req, timeout=10) as r:
                    # try to get charset from headers, default to utf-8
                    charset = r.headers.get_content_charset() or "utf-8"
                    text = r.read().decode(charset)
            except (HTTPError, URLError) as e:
                raise RuntimeError(f"Failed to fetch URL {path_str}: {e}") from e

        data = yaml.safe_load(text)
        return YamlConfig.from_obj(data)

    # Local file case
    else:
        p = Path(path_str)
        if not p.exists():
            raise FileNotFoundError(f"YAML file not found: {p}")
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return YamlConfig.from_obj(data)
