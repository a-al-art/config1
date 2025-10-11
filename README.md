# Эмулятор командной строки с виртуальной файловой системой

## Общее описание

Эмулятор командной строки с поддержкой виртуальной файловой системы (VFS), имитирующий работу в UNIX-подобной операционной системе. Проект реализован на Python и предоставляет интерактивный интерфейс для выполнения команд в изолированной среде.

**Основные возможности:**
- Полноценная виртуальная файловая система в памяти
- Поддержка основных команд UNIX
- Работа в интерактивном и скриптовом режимах
- Настраиваемая конфигурация через параметры командной строки
- Обработка ошибок и валидация входных данных

## Функции и настройки

### Основные компоненты

#### 1. ShellEmulator
Основной класс эмулятора, управляющий взаимодействием с пользователем.

**Поддерживаемые команды:**
- `ls` - список файлов и директорий
- `cd` - смена текущей директории
- `pwd` - вывод текущего пути
- `cat` - вывод содержимого файлов
- `echo` - вывод текста
- `uname` - информация о системе
- `mv` - перемещение/переименование файлов и директорий
- `exit` - выход из эмулятора

#### 2. VirtualFileSystem
Класс для работы с виртуальной файловой системой.

**Функции:**
- `__init__(vfs_path)` - загрузка VFS из CSV-файла
- `load_vfs(vfs_path)` - загрузка структуры VFS
- `resolve_path(current_path, target_path)` - разрешение относительных и абсолютных путей
- `get_file_content(current_path, file_path)` - получение содержимого файла
- `get_motd()` - получение сообщения дня (MOTD)
- `move_node(current_path, source_path, dest_path)` - перемещение узлов в VFS

### Формат VFS

VFS загружается из CSV-файла со следующими колонками:
- `path` - полный путь к узлу
- `type` - тип узла (`file` или `directory`)
- `content` - текстовое содержимое (для файлов)
- `content_b64` - содержимое в base64 (для бинарных файлов)

### Настройки эмулятора

**Параметры командной строки:**
- Интерактивный режим: `python main.py`
- Режим скрипта: `python main.py <путь_к_VFS> <путь_к_скрипту>`

**Пример:**
```bash
python main.py utils/vfs_structure.csv tests/test_script_stage5.txt
```

# Сборка проекта и запуск тестов

## Требования
- Python 3.6+
- Стандартные библиотеки Python (csv, os, sys, shlex, socket, getpass, platform, base64)
## Структура VFS по умолчанию

Проект включает пример VFS с следующей структурой:

- `/home/user/documents/` - текстовые файлы
- `/home/user/pictures/` - изображения (включая бинарные данные)
- `/etc/` - конфигурационные файлы
- `/var/log/` - файлы логов
- `/motd` - сообщение дня

Эмулятор предоставляет полнофункциональную среду для тестирования и изучения работы командной строки UNIX в изолированной среде.
## Пример использования
```commandline
Welcome to the Virtual System!
Добро пожаловать в эмулятор командной строки с VFS
Доступные команды: ls, cd, pwd, cat, echo, mkdir, touch, exit, uname, mv
Виртуальная файловая система содержит:
  /home/user/documents/ - файлы документов
  /home/user/pictures/ - изображения
  /etc/ - конфигурационные файлы
  /var/log/ - логи
Для выхода введите 'exit'
--------------------------------------------------
artam@Artbook-16s:~$ ls
documents/
pictures/
readme.md

artam@Artbook-16s:~$ pwd
/home/user

artam@Artbook-16s:~$ cd /home/user/documents

artam@Artbook-16s:~/documents$ pwd
/home/user/documents

artam@Artbook-16s:~/documents$ cd /home/user

artam@Artbook-16s:~$ pwd
/home/user

artam@Artbook-16s:~$ cd /home/user/pictures

artam@Artbook-16s:~/pictures$ cat img1.jpg
кот

artam@Artbook-16s:~/pictures$ cd /home/user/documents

artam@Artbook-16s:~/documents$ cat file2.txt
Test text

artam@Artbook-16s:~/documents$ uname -a
Windows Artbook-16s 11 10.0.26100 AMD64

artam@Artbook-16s:~/documents$ pwd
/home/user/documents

artam@Artbook-16s:~/documents$ uname -s 
Windows

artam@Artbook-16s:~/documents$ echo Hello
Hello
```
