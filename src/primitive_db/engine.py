import prompt


def welcome():
    print("Первая попытка запустить проект!")
    print()
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")

    while True:
        command = prompt.string("Введите команду: ")

        if command == "exit":
            break

        if command == "help":
            print()
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
