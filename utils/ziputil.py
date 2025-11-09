import zipfile
import gzip
import os
from io import BytesIO

def zip_files(filename: str, files: list[str], srcpath: str, aliasnames: list[str] = None) -> None:
    """压缩多个文件"""
    if os.path.exists(filename):
        os.remove(filename)
    
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, file in enumerate(files):
            arcname = os.path.relpath(file, srcpath)
            if aliasnames and i < len(aliasnames) and '|' in aliasnames[i]:
                old, new = aliasnames[i].split('|', 1)
                arcname = arcname.replace(old, new)
            zf.write(file, arcname=arcname)

def compress(data: bytes) -> bytes:
    """Gzip压缩"""
    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as f:
        f.write(data)
    return buf.getvalue()

def decompress(data: bytes) -> bytes:
    """Gzip解压缩"""
    with gzip.GzipFile(fileobj=BytesIO(data), mode='rb') as f:
        return f.read()