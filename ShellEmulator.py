import shlex
import socket
import getpass
import os
import sys
import platform
from VirtualFileSystem import VirtualFileSystem


class ShellEmulator:
    def __init__(self, vfs_path, script_path=None):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.vfs = VirtualFileSystem(vfs_path)
        self.current_path = '/home/user'
        self.running = True
        self.script_path = script_path
        self.script_mode = script_path is not None
        self.script_lines = []
        self.script_index = 0

        if self.script_mode:
            self.load_script()

    def load_script(self):
        """Загружает скрипт из файла"""
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                self.script_lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        except Exception as e:
            print(f"Ошибка загрузки скрипта: {e}")
            sys.exit(1)

    def get_prompt(self):
        """Формирует приглашение к вводу"""
        if self.current_path.startswith('/home/user'):
            display_path = '~' + self.current_path[len('/home/user'):]
        else:
            display_path = self.current_path

        return f"{self.username}@{self.hostname}:{display_path}$ "

    def parse_command(self, command_line):
        """Парсит командную строку с учетом кавычек"""
        try:
            return shlex.split(command_line)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            return None

    def execute_command(self, command_parts):
        """Выполняет команду с остановкой при ошибке в скриптовом режиме"""
        if not command_parts:
            return True

        command = command_parts[0]
        args = command_parts[1:]

        try:
            if command == "exit":
                self.running = False
                print("Выход из эмулятора")
                return False

            elif command == "ls":
                self.ls_command(args)

            elif command == "cd":
                self.cd_command(args)

            elif command == "pwd":
                print(self.current_path)

            elif command == "cat":
                self.cat_command(args)

            elif command == "echo":
                self.echo_command(args)

            elif command == "mkdir":
                self.mkdir_command(args)

            elif command == "touch":
                self.touch_command(args)

            elif command == "uname":
                self.uname_command(args)

            else:
                print(f"{command}: команда не найдена")
                if self.script_mode:
                    raise RuntimeError(f"Неизвестная команда: {command}")

            return True

        except Exception as e:
            if self.script_mode:
                print(f"Ошибка в скрипте: {e}")
                raise  # Пробрасываем ошибку выше для остановки скрипта
            return True

    def ls_command(self, args):
        """Команда ls"""
        target_path = self.current_path
        if args:
            target_path = args[0]

        node = self.vfs.resolve_path(self.current_path, target_path)
        if not node:
            raise RuntimeError(f"Нет доступа к '{target_path}': Нет такого файла или каталога")

        if node['type'] != 'directory':
            raise RuntimeError(f"'{target_path}': Не директория")

        files = list(node['content'].keys())
        for file in sorted(files):
            file_type = node['content'][file]['type']
            indicator = '/' if file_type == 'directory' else ''
            print(f"{file}{indicator}")

    def cd_command(self, args):
        """Команда cd"""
        if not args:
            self.current_path = "/home/user"
            return

        if len(args) > 1:
            raise RuntimeError("Слишком много аргументов")

        target_path = args[0]
        new_node = self.vfs.resolve_path(self.current_path, target_path)

        if not new_node:
            raise RuntimeError(f"'{target_path}': Нет такой директории")

        if new_node['type'] != 'directory':
            raise RuntimeError(f"'{target_path}': Не директория")

        # Обновляем путь
        if target_path.startswith('/'):
            self.current_path = target_path
        else:
            if self.current_path == '/':
                self.current_path = '/' + target_path
            else:
                self.current_path = self.current_path + '/' + target_path

        self.normalize_path()

    def cat_command(self, args):
        """Команда cat"""
        if not args:
            print("Отсутствуют аргументы")
            return

        for file_path in args:
            content = self.vfs.get_file_content(self.current_path, file_path)
            if content is None:
                print(f"Файл '{file_path}' не существует")
            else:
                print(content)

    def echo_command(self, args):
        """Команда echo"""
        print(' '.join(args))

    def mkdir_command(self, args):
        """Команда mkdir (заглушка)"""
        if not args:
            raise RuntimeError("Отсутствуют аргументы")
        print(f"mkdir: создание директорий {args} (в памяти VFS)")

    def touch_command(self, args):
        """Команда touch (заглушка)"""
        if not args:
            raise RuntimeError("Отсутствуют аргументы")
        print(f"touch: создание файлов {args} (в памяти VFS)")

    def uname_command(self, args):
        """Команда uname"""
        # Обработка флагов
        sysname = platform.system()
        nodename = self.hostname
        release = platform.release()
        version = platform.version()
        machine = platform.machine()

        if not args:
            # Если нет флагов - выводим только имя системы
            print(sysname)
            return

        for arg in args:
            if arg == "-a":
                # Все поля
                print(f"{sysname} {nodename} {release} {version} {machine}")
            elif arg == "-s":
                print(sysname)
            elif arg == "-n":
                print(nodename)
            elif arg == "-r":
                print(release)
            elif arg == "-v":
                print(version)
            elif arg == "-m":
                print(machine)
            else:
                print(f"uname: неподдерживаемый флаг: {arg}")
                if self.script_mode:
                    raise RuntimeError(f"Неподдерживаемый флаг: {arg}")

    def normalize_path(self):
        """Нормализует путь"""
        # Разбиваем путь на части
        parts = self.current_path.split('/')
        stack = []
        for part in parts:
            if part == '..':
                if stack and stack[-1] != '..':
                    stack.pop()
            elif part and part != '.':
                stack.append(part)

        # Собираем нормализованный путь
        if not stack:
            self.current_path = '/'
        else:
            self.current_path = '/' + '/'.join(stack)

    def run_script_mode(self):
        """Режим выполнения скрипта с остановкой при ошибках"""
        # Проверяем и выводим motd
        motd = self.vfs.get_motd()
        if motd:
            print(motd)

        for i, line in enumerate(self.script_lines, 1):
            prompt = self.get_prompt()
            print(f"{prompt}{line}")

            command_parts = self.parse_command(line)
            if command_parts is None:
                raise RuntimeError("Синтаксическая ошибка в команде")

            should_continue = self.execute_command(command_parts)
            if not should_continue:
                return True  # Нормальное завершение по exit
            print()  # Пустая строка для читаемости

        return True

    def run_interactive_mode(self):
        """Интерактивный режим"""
        # Проверяем и выводим motd
        motd = self.vfs.get_motd()
        if motd:
            print(motd)

        self.terminal_start()

        while self.running:
            try:
                command_line = input(self.get_prompt()).strip()
                if not command_line:
                    continue

                command_parts = self.parse_command(command_line)
                if command_parts is None:
                    continue

                self.execute_command(command_parts)
                print()

            except KeyboardInterrupt:
                print("\nДля выхода введите 'exit'")
            except EOFError:
                print("\nВыход из эмулятора")
                break
            except Exception as e:
                print(f"Ошибка: {e}")

    def terminal_start(self):
        """Приветственное сообщение (как в оригинале)"""
        welcome_text = (
                "Добро пожаловать в эмулятор командной строки с VFS\n"
                "Доступные команды: ls, cd, pwd, cat, echo, mkdir, touch, exit, uname\n"
                "Виртуальная файловая система содержит:\n"
                "  /home/user/documents/ - файлы документов\n"
                "  /home/user/pictures/ - изображения\n"
                "  /etc/ - конфигурационные файлы\n"
                "  /var/log/ - логи\n"
                "Для выхода введите 'exit'\n"
                + "-" * 50
        )
        print(welcome_text)

    def run(self):
        """Основной метод запуска"""
        if self.script_mode:
            return self.run_script_mode()
        else:
            self.run_interactive_mode()
            return True