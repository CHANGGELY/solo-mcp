"""搜索工具函数"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
from collections import defaultdict
import fnmatch
from datetime import datetime

from .file_utils import read_file_content, get_file_info, _is_text_file


class SearchResult:
    """搜索结果数据结构"""

    def __init__(
        self, file_path: str, matches: List[Dict[str, Any]], score: float = 0.0
    ):
        self.file_path = file_path
        self.matches = matches
        self.score = score
        self.total_matches = len(matches)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "matches": self.matches,
            "score": self.score,
            "total_matches": self.total_matches,
        }


class FileSearcher:
    """文件搜索器"""

    def __init__(self, root_directory: str):
        self.root_directory = Path(root_directory)
        self.file_cache: Dict[str, Dict[str, Any]] = {}
        self.content_cache: Dict[str, str] = {}

        # 默认忽略的目录和文件
        self.ignore_patterns = {
            "__pycache__",
            ".git",
            ".svn",
            ".hg",
            "node_modules",
            ".vscode",
            ".idea",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "Thumbs.db",
        }

    def add_ignore_pattern(self, pattern: str):
        """添加忽略模式"""
        self.ignore_patterns.add(pattern)

    def should_ignore(self, path: Path) -> bool:
        """检查是否应该忽略该路径"""
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(
                str(path), pattern
            ):
                return True
        return False

    def get_all_files(
        self, extensions: Optional[List[str]] = None, max_size: int = 10 * 1024 * 1024
    ) -> List[str]:
        """获取所有文件

        Args:
            extensions: 文件扩展名过滤器
            max_size: 最大文件大小（字节）

        Returns:
            文件路径列表
        """
        files = []

        try:
            for file_path in self.root_directory.rglob("*"):
                if not file_path.is_file():
                    continue

                if self.should_ignore(file_path):
                    continue

                # 检查文件大小
                try:
                    if file_path.stat().st_size > max_size:
                        continue
                except OSError:
                    continue

                # 检查扩展名
                if extensions:
                    if file_path.suffix.lower() not in [
                        ext.lower() for ext in extensions
                    ]:
                        continue

                files.append(str(file_path))

        except Exception as e:
            print(f"获取文件列表失败: {e}")

        return files

    def search_by_name(self, pattern: str, case_sensitive: bool = False) -> List[str]:
        """按文件名搜索

        Args:
            pattern: 搜索模式（支持通配符）
            case_sensitive: 是否区分大小写

        Returns:
            匹配的文件路径列表
        """
        matches = []

        if not case_sensitive:
            pattern = pattern.lower()

        try:
            for file_path in self.root_directory.rglob("*"):
                if not file_path.is_file():
                    continue

                if self.should_ignore(file_path):
                    continue

                file_name = file_path.name
                if not case_sensitive:
                    file_name = file_name.lower()

                if fnmatch.fnmatch(file_name, pattern):
                    matches.append(str(file_path))

        except Exception as e:
            print(f"按名称搜索失败: {e}")

        return matches

    def search_content(
        self,
        query: str,
        file_extensions: Optional[List[str]] = None,
        case_sensitive: bool = False,
        regex: bool = False,
        max_results: int = 100,
    ) -> List[SearchResult]:
        """搜索文件内容

        Args:
            query: 搜索查询
            file_extensions: 限制搜索的文件扩展名
            case_sensitive: 是否区分大小写
            regex: 是否使用正则表达式
            max_results: 最大结果数量

        Returns:
            搜索结果列表
        """
        results = []
        files = self.get_all_files(file_extensions)

        # 编译正则表达式
        if regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query, flags)
            except re.error as e:
                print(f"正则表达式错误: {e}")
                return []
        else:
            pattern = None

        for file_path in files:
            if len(results) >= max_results:
                break

            try:
                # 检查是否为文本文件
                if not _is_text_file(file_path):
                    continue

                content = self._get_file_content(file_path)
                if not content:
                    continue

                matches = self._find_matches_in_content(
                    content, query, pattern, case_sensitive
                )

                if matches:
                    score = self._calculate_relevance_score(matches, content, query)
                    results.append(SearchResult(file_path, matches, score))

            except Exception as e:
                # 跳过无法处理的文件
                continue

        # 按相关性分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def _get_file_content(self, file_path: str) -> Optional[str]:
        """获取文件内容（带缓存）"""
        if file_path in self.content_cache:
            return self.content_cache[file_path]

        try:
            content = read_file_content(file_path)
            # 限制缓存大小
            if len(self.content_cache) < 100:
                self.content_cache[file_path] = content
            return content
        except Exception:
            return None

    def _find_matches_in_content(
        self,
        content: str,
        query: str,
        pattern: Optional[re.Pattern],
        case_sensitive: bool,
    ) -> List[Dict[str, Any]]:
        """在内容中查找匹配项"""
        matches = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_matches = []

            if pattern:  # 正则表达式搜索
                for match in pattern.finditer(line):
                    line_matches.append(
                        {
                            "start": match.start(),
                            "end": match.end(),
                            "text": match.group(),
                        }
                    )
            else:  # 普通文本搜索
                search_line = line if case_sensitive else line.lower()
                search_query = query if case_sensitive else query.lower()

                start = 0
                while True:
                    pos = search_line.find(search_query, start)
                    if pos == -1:
                        break

                    line_matches.append(
                        {
                            "start": pos,
                            "end": pos + len(query),
                            "text": line[pos : pos + len(query)],
                        }
                    )
                    start = pos + 1

            if line_matches:
                matches.append(
                    {
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "matches": line_matches,
                        "context": self._get_line_context(lines, line_num - 1),
                    }
                )

        return matches

    def _calculate_relevance_score(
        self, matches: List[Dict[str, Any]], content: str, query: str
    ) -> float:
        """计算相关性分数"""
        if not matches:
            return 0.0

        score = 0.0

        # 基础分数：匹配数量
        total_matches = sum(len(match["matches"]) for match in matches)
        score += min(total_matches * 0.1, 1.0)

        # 文件名匹配加分
        file_name = Path(matches[0].get("file_path", "")).name.lower()
        if query.lower() in file_name:
            score += 0.2

        # 匹配密度加分
        content_length = len(content)
        if content_length > 0:
            density = total_matches / (content_length / 100)  # 每100字符的匹配数
            score += min(density * 0.1, 0.3)

        # 完整单词匹配加分
        for match in matches:
            line_content = match["line_content"].lower()
            if f" {query.lower()} " in line_content or line_content.startswith(
                query.lower()
            ):
                score += 0.1

        return min(score, 2.0)  # 限制最大分数

    def _get_line_context(
        self, lines: List[str], line_index: int, context_size: int = 2
    ) -> Dict[str, List[str]]:
        """获取行的上下文"""
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)

        return {"before": lines[start:line_index], "after": lines[line_index + 1 : end]}

    def clear_cache(self):
        """清除缓存"""
        self.file_cache.clear()
        self.content_cache.clear()


def search_files(
    directory: str,
    pattern: str = "*",
    extensions: Optional[List[str]] = None,
    case_sensitive: bool = False,
    max_results: int = 100,
) -> List[str]:
    """搜索文件

    Args:
        directory: 搜索目录
        pattern: 文件名模式
        extensions: 文件扩展名过滤器
        case_sensitive: 是否区分大小写
        max_results: 最大结果数量

    Returns:
        匹配的文件路径列表
    """
    searcher = FileSearcher(directory)

    if pattern == "*":
        # 获取所有文件
        files = searcher.get_all_files(extensions)
    else:
        # 按名称搜索
        files = searcher.search_by_name(pattern, case_sensitive)

        # 应用扩展名过滤器
        if extensions:
            ext_set = {ext.lower() for ext in extensions}
            files = [f for f in files if Path(f).suffix.lower() in ext_set]

    return files[:max_results]


def search_content(
    directory: str,
    query: str,
    file_extensions: Optional[List[str]] = None,
    case_sensitive: bool = False,
    regex: bool = False,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """搜索文件内容

    Args:
        directory: 搜索目录
        query: 搜索查询
        file_extensions: 限制搜索的文件扩展名
        case_sensitive: 是否区分大小写
        regex: 是否使用正则表达式
        max_results: 最大结果数量

    Returns:
        搜索结果字典列表
    """
    searcher = FileSearcher(directory)
    results = searcher.search_content(
        query, file_extensions, case_sensitive, regex, max_results
    )

    return [result.to_dict() for result in results]


def find_similar_files(
    file_path: str, directory: str, similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """查找相似文件

    Args:
        file_path: 参考文件路径
        directory: 搜索目录
        similarity_threshold: 相似度阈值

    Returns:
        相似文件信息列表
    """
    try:
        reference_content = read_file_content(file_path)
        reference_lines = set(
            line.strip() for line in reference_content.split("\n") if line.strip()
        )

        if not reference_lines:
            return []

        searcher = FileSearcher(directory)
        all_files = searcher.get_all_files([Path(file_path).suffix])

        similar_files = []

        for candidate_file in all_files:
            if candidate_file == file_path:
                continue

            try:
                candidate_content = read_file_content(candidate_file)
                candidate_lines = set(
                    line.strip()
                    for line in candidate_content.split("\n")
                    if line.strip()
                )

                if not candidate_lines:
                    continue

                # 计算 Jaccard 相似度
                intersection = len(reference_lines & candidate_lines)
                union = len(reference_lines | candidate_lines)

                if union > 0:
                    similarity = intersection / union

                    if similarity >= similarity_threshold:
                        similar_files.append(
                            {
                                "file_path": candidate_file,
                                "similarity": similarity,
                                "common_lines": intersection,
                                "total_lines_ref": len(reference_lines),
                                "total_lines_candidate": len(candidate_lines),
                            }
                        )

            except Exception:
                continue

        # 按相似度排序
        similar_files.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_files

    except Exception as e:
        print(f"查找相似文件失败: {e}")
        return []


def extract_keywords(
    text: str, min_length: int = 3, max_keywords: int = 20
) -> List[str]:
    """从文本中提取关键词

    Args:
        text: 输入文本
        min_length: 最小关键词长度
        max_keywords: 最大关键词数量

    Returns:
        关键词列表
    """
    # 简单的关键词提取（基于词频）
    import string
    from collections import Counter

    # 清理文本
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))

    # 分词
    words = text.split()

    # 过滤停用词和短词
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "this",
        "that",
        "these",
        "those",
    }

    filtered_words = [
        word for word in words if len(word) >= min_length and word not in stop_words
    ]

    # 计算词频
    word_counts = Counter(filtered_words)

    # 返回最常见的关键词
    return [word for word, count in word_counts.most_common(max_keywords)]


def search_by_keywords(
    directory: str,
    keywords: List[str],
    file_extensions: Optional[List[str]] = None,
    match_all: bool = False,
    max_results: int = 50,
) -> List[Dict[str, Any]]:
    """基于关键词搜索

    Args:
        directory: 搜索目录
        keywords: 关键词列表
        file_extensions: 文件扩展名过滤器
        match_all: 是否需要匹配所有关键词
        max_results: 最大结果数量

    Returns:
        搜索结果列表
    """
    searcher = FileSearcher(directory)
    all_results = []

    for keyword in keywords:
        results = searcher.search_content(
            keyword, file_extensions, max_results=max_results
        )
        all_results.extend(results)

    # 合并结果并计算分数
    file_scores = defaultdict(float)
    file_results = {}

    for result in all_results:
        file_path = result.file_path
        file_scores[file_path] += result.score

        if file_path not in file_results:
            file_results[file_path] = result
        else:
            # 合并匹配项
            file_results[file_path].matches.extend(result.matches)
            file_results[file_path].total_matches += result.total_matches

    # 如果需要匹配所有关键词，过滤结果
    if match_all:
        filtered_results = []
        for file_path, result in file_results.items():
            content = searcher._get_file_content(file_path)
            if content:
                content_lower = content.lower()
                if all(keyword.lower() in content_lower for keyword in keywords):
                    result.score = file_scores[file_path]
                    filtered_results.append(result)
        final_results = filtered_results
    else:
        final_results = list(file_results.values())
        for result in final_results:
            result.score = file_scores[result.file_path]

    # 按分数排序
    final_results.sort(key=lambda x: x.score, reverse=True)

    return [result.to_dict() for result in final_results[:max_results]]
