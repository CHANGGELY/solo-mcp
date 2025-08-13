"""文件操作工具函数"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import mimetypes
from datetime import datetime


def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
    """读取文件内容

    Args:
        file_path: 文件路径
        encoding: 文件编码，默认为 utf-8

    Returns:
        文件内容字符串

    Raises:
        FileNotFoundError: 文件不存在
        UnicodeDecodeError: 编码错误
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        # 尝试其他编码
        encodings = ["utf-8", "gbk", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"无法解码文件 {file_path}")


def write_file_content(file_path: str, content: str, encoding: str = "utf-8") -> bool:
    """写入文件内容

    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码，默认为 utf-8

    Returns:
        是否写入成功
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False


def get_file_info(file_path: str) -> Dict[str, Any]:
    """获取文件信息

    Args:
        file_path: 文件路径

    Returns:
        包含文件信息的字典
    """
    if not os.path.exists(file_path):
        return {"exists": False, "path": file_path, "error": "File not found"}

    try:
        stat = os.stat(file_path)
        path_obj = Path(file_path)

        # 获取 MIME 类型
        mime_type, _ = mimetypes.guess_type(file_path)

        return {
            "exists": True,
            "path": file_path,
            "name": path_obj.name,
            "stem": path_obj.stem,
            "suffix": path_obj.suffix,
            "size": stat.st_size,
            "size_human": _format_file_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "is_file": os.path.isfile(file_path),
            "is_dir": os.path.isdir(file_path),
            "mime_type": mime_type,
            "is_text": _is_text_file(file_path, mime_type),
            "is_binary": _is_binary_file(file_path, mime_type),
        }
    except Exception as e:
        return {"exists": True, "path": file_path, "error": str(e)}


def list_files(
    directory: str, pattern: str = "*", recursive: bool = False
) -> List[str]:
    """列出目录中的文件

    Args:
        directory: 目录路径
        pattern: 文件模式，默认为 '*'
        recursive: 是否递归搜索子目录

    Returns:
        文件路径列表
    """
    try:
        path_obj = Path(directory)
        if not path_obj.exists():
            return []

        if recursive:
            files = list(path_obj.rglob(pattern))
        else:
            files = list(path_obj.glob(pattern))

        return [str(f) for f in files if f.is_file()]
    except Exception as e:
        print(f"列出文件失败: {e}")
        return []


def find_files_by_extension(
    directory: str, extensions: List[str], recursive: bool = True
) -> List[str]:
    """根据扩展名查找文件

    Args:
        directory: 搜索目录
        extensions: 文件扩展名列表（如 ['.py', '.txt']）
        recursive: 是否递归搜索

    Returns:
        匹配的文件路径列表
    """
    files = []
    extensions = [ext.lower() for ext in extensions]

    try:
        path_obj = Path(directory)
        if not path_obj.exists():
            return []

        if recursive:
            all_files = path_obj.rglob("*")
        else:
            all_files = path_obj.glob("*")

        for file_path in all_files:
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                files.append(str(file_path))
    except Exception as e:
        print(f"查找文件失败: {e}")

    return files


def search_in_files(
    directory: str,
    search_text: str,
    file_extensions: List[str] = None,
    case_sensitive: bool = False,
    recursive: bool = True,
) -> List[Dict[str, Any]]:
    """在文件中搜索文本

    Args:
        directory: 搜索目录
        search_text: 要搜索的文本
        file_extensions: 限制搜索的文件扩展名
        case_sensitive: 是否区分大小写
        recursive: 是否递归搜索

    Returns:
        包含搜索结果的字典列表
    """
    results = []

    if file_extensions:
        files = find_files_by_extension(directory, file_extensions, recursive)
    else:
        files = list_files(directory, recursive=recursive)

    search_text_lower = search_text.lower() if not case_sensitive else search_text

    for file_path in files:
        try:
            content = read_file_content(file_path)
            content_to_search = content.lower() if not case_sensitive else content

            if search_text_lower in content_to_search:
                # 找到匹配的行
                lines = content.split("\n")
                matching_lines = []

                for i, line in enumerate(lines, 1):
                    line_to_search = line.lower() if not case_sensitive else line
                    if search_text_lower in line_to_search:
                        matching_lines.append(
                            {
                                "line_number": i,
                                "content": line.strip(),
                                "context": _get_line_context(lines, i - 1, 2),
                            }
                        )

                if matching_lines:
                    results.append(
                        {
                            "file_path": file_path,
                            "matches": matching_lines,
                            "total_matches": len(matching_lines),
                        }
                    )
        except Exception as e:
            # 跳过无法读取的文件
            continue

    return results


def _format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def _is_text_file(file_path: str, mime_type: Optional[str] = None) -> bool:
    """判断是否为文本文件"""
    if mime_type:
        return mime_type.startswith("text/") or mime_type in [
            "application/json",
            "application/xml",
            "application/javascript",
            "application/x-python-code",
        ]

    # 基于扩展名判断
    text_extensions = {
        ".txt",
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".md",
        ".yml",
        ".yaml",
        ".ini",
        ".cfg",
        ".conf",
        ".log",
        ".csv",
        ".tsv",
        ".sql",
        ".sh",
        ".bat",
        ".ps1",
        ".c",
        ".cpp",
        ".h",
        ".hpp",
        ".java",
        ".cs",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".swift",
    }

    return Path(file_path).suffix.lower() in text_extensions


def _is_binary_file(file_path: str, mime_type: Optional[str] = None) -> bool:
    """判断是否为二进制文件"""
    if mime_type:
        return not _is_text_file(file_path, mime_type)

    # 基于扩展名判断
    binary_extensions = {
        ".exe",
        ".dll",
        ".so",
        ".dylib",
        ".bin",
        ".dat",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".ico",
        ".svg",
        ".webp",
        ".mp3",
        ".wav",
        ".flac",
        ".ogg",
        ".m4a",
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
        ".xz",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
    }

    return Path(file_path).suffix.lower() in binary_extensions


def _get_line_context(
    lines: List[str], line_index: int, context_size: int = 2
) -> Dict[str, List[str]]:
    """获取行的上下文"""
    start = max(0, line_index - context_size)
    end = min(len(lines), line_index + context_size + 1)

    return {"before": lines[start:line_index], "after": lines[line_index + 1 : end]}


def ensure_directory(directory: str) -> bool:
    """确保目录存在

    Args:
        directory: 目录路径

    Returns:
        是否成功创建或目录已存在
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False


def copy_file(src: str, dst: str) -> bool:
    """复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        是否复制成功
    """
    try:
        import shutil

        # 确保目标目录存在
        ensure_directory(os.path.dirname(dst))

        shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(f"复制文件失败: {e}")
        return False


def move_file(src: str, dst: str) -> bool:
    """移动文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        是否移动成功
    """
    try:
        import shutil

        # 确保目标目录存在
        ensure_directory(os.path.dirname(dst))

        shutil.move(src, dst)
        return True
    except Exception as e:
        print(f"移动文件失败: {e}")
        return False


def delete_file(file_path: str) -> bool:
    """删除文件

    Args:
        file_path: 文件路径

    Returns:
        是否删除成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


def get_file_hash(file_path: str, algorithm: str = "md5") -> Optional[str]:
    """计算文件哈希值

    Args:
        file_path: 文件路径
        algorithm: 哈希算法 ('md5', 'sha1', 'sha256')

    Returns:
        文件哈希值，失败时返回 None
    """
    try:
        import hashlib

        hash_func = getattr(hashlib, algorithm.lower())()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)

        return hash_func.hexdigest()
    except Exception as e:
        print(f"计算文件哈希失败: {e}")
        return None
