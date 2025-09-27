import sys
import os
from ShellEmulator import ShellEmulator


def main():
    # Обработка параметров командной строки
    if len(sys.argv) not in [1, 3]:
        print("Использование:")
        print("  Интерактивный режим: python main.py")
        print("  Режим скрипта: python main.py <путь_к_VFS> <путь_к_скрипту>")
        print("Пример: python main.py utils/vfs_structure.csv scripts/test_script.txt")
        sys.exit(1)

    # Режим работы
    if len(sys.argv) == 1:
        # Интерактивный режим
        vfs_path = "utils/vfs_structure.csv"  # путь по умолчанию (CSV)
        script_path = None
    else:
        # Режим скрипта
        vfs_path = sys.argv[1]
        script_path = sys.argv[2]

    # Проверка существования файла VFS
    if not os.path.exists(vfs_path):
        print(f"Ошибка: файл VFS '{vfs_path}' не существует")
        sys.exit(1)

    # Проверка существования скрипта (если указан)
    if script_path and not os.path.exists(script_path):
        print(f"Ошибка: файл скрипта '{script_path}' не существует")
        sys.exit(1)

    # Отладочный вывод параметров (только в режиме скрипта)
    if script_path:
        print("-" * 50)
        print("Конфигурация эмулятора")
        print("-" * 50)
        print(f"Путь к VFS: {vfs_path}")
        print(f"Путь к стартовому скрипту: {script_path}")
        print("-" * 50)
        print()

    try:
        shell = ShellEmulator(vfs_path, script_path)
        success = shell.run()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
