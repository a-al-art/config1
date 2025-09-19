import os
import shlex
import platform


def main():
    while True:
        # формирование username@hostname:~$
        username = os.getlogin()
        hostname = platform.node()
        current_dir = "~" # заглушка
        prompt = f"{username}@{hostname}:{current_dir}$ "

        # ждем ввод пользователя
        user_input = input(prompt).strip()

        # парсим ввод с учетом кавычек
        try:
            parts = shlex.split(user_input)
        except ValueError as e:
            print(f"Ошибка парсинга: {e}")
            continue

        if not parts:
            continue

        command = parts[0]
        args = parts[1:]

        # обработка команд
        if command == "exit":
            # проверка аргументов для exit
            if len(args) > 0:
                print(f"exit: неверные аргументы - команда не принимает аргументов")
                continue
            break

        elif command == "ls":
            # if len(args) > 1:
            #     print(f"ls: неверные аргументы - слишком много параметров: {args}")
            #     continue
            print(f"ls: аргументы {args}")

        elif command == "cd":
            # if len(args) > 1:
            #     print(f"cd: неверные аргументы - слишком много путей: {args}")
            #     continue
            if len(args) == 0:
                print("cd: переход в домашнюю директорию")
                continue
            print(f"cd: аргументы {args}")

        else:
            print(f"Неизвестная команда: {command}")

if __name__ == "__main__":
    main()