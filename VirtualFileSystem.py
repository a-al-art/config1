import csv
import os
import base64


class VirtualFileSystem:
    def __init__(self, vfs_path):
        self.vfs = {"type": "directory", "content": {}}
        self.load_vfs(vfs_path)
        self.vfs = self._process_vfs_data(self.vfs)

    def load_vfs(self, vfs_path):
        """Загружает VFS из CSV"""
        if not os.path.exists(vfs_path):
            raise FileNotFoundError(f"Файл VFS '{vfs_path}' не найден")

        with open(vfs_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                path = row["path"].strip()
                node_type = row["type"].strip()
                content = row.get("content", "")
                content_b64 = row.get("content_b64", "")

                node_data = {"type": node_type}
                if node_type == "file":
                    if content_b64:
                        node_data["content_b64"] = content_b64
                    else:
                        node_data["content"] = content
                else:
                    node_data["content"] = {}

                self.add_node(path, node_type, node_data)

    def add_node(self, path, node_type, node_data):
        """Добавляет узел (файл или директорию) в дерево"""
        parts = [p for p in path.strip("/").split("/") if p]
        node = self.vfs

        for i, part in enumerate(parts):
            is_last = i == len(parts) - 1

            if is_last:
                node["content"][part] = node_data
            else:
                if part not in node["content"]:
                    node["content"][part] = {"type": "directory", "content": {}}
                elif node["content"][part]["type"] != "directory":
                    raise RuntimeError(f"Невозможно создать '{'/'.join(parts[:i + 1])}': файл блокирует путь")
                node = node["content"][part]

    def _process_vfs_data(self, node, path=""):
        """Обрабатывает данные VFS, декодируя base64 если нужно"""
        if node['type'] == 'file' and 'content_b64' in node:
            try:
                node['content'] = base64.b64decode(node['content_b64']).decode('utf-8')
                del node['content_b64']
            except Exception as e:
                node['content'] = f"Ошибка декодирования: {e}"
        elif node['type'] == 'directory' and "content" in node and isinstance(node['content'], dict):
            for name, child in node['content'].items():
                child_path = f"{path}/{name}" if path else name
                node['content'][name] = self._process_vfs_data(child, child_path)
        return node

    def resolve_path(self, current_path, target_path):
        """Разрешает относительный и абсолютный путь"""
        if target_path.startswith("/"):
            full_path = target_path
        else:
            if current_path == "/":
                full_path = "/" + target_path
            else:
                full_path = current_path.rstrip("/") + "/" + target_path

        # Нормализуем путь
        parts = full_path.split('/')
        stack = []
        for part in parts:
            if part == '..':
                if stack and stack[-1] != '..':
                    stack.pop()
            elif part and part != '.':
                stack.append(part)

        if not stack:
            normalized_path = '/'
        else:
            normalized_path = '/' + '/'.join(stack)

        # Теперь разрешаем путь
        parts = normalized_path.strip("/").split("/") if normalized_path != "/" else []
        node = self.vfs
        for part in parts:
            if not part:
                continue
            if "content" not in node or part not in node["content"]:
                return None
            node = node["content"][part]
        return node

    def get_file_content(self, current_path, file_path):
        """Возвращает содержимое файла"""
        node = self.resolve_path(current_path, file_path)
        if node and node["type"] == "file":
            return node["content"]
        return None

    def get_motd(self):
        """Получает содержимое файла /motd, если он существует"""
        node = self.resolve_path("/", "motd")
        if node and node["type"] == "file":
            return node["content"]
        return None