import time 
import datetime
import os
from mcstatus import JavaServer
from plyer import notification
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

def notify(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5  # Уведомление будет отображаться 5 секунд
    )

def get_config_path():
    return os.path.join(os.path.expanduser("~"), "Documents", "teastats", "server.conf")

def load_servers():
    config_path = get_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    if not os.path.exists(config_path):
        return []
    with open(config_path, "r") as file:
        return [line.strip() for line in file.readlines()]

def save_server(server_address):
    config_path = get_config_path()
    with open(config_path, "a") as file:
        file.write(server_address + "\n")

def select_server():
    servers = load_servers()
    if not servers:
        print(Fore.RED + "Нет сохраненных серверов. Добавьте новый.")
        return add_server()
    
    print(Fore.GREEN + "Выберите действие:")
    print("1) Запустить последнюю сессию")
    print("2) Список моих добавленных серверов")
    print("3) Добавить новый сервер")
    choice = input("Введите номер (1-3): ")
    
    if choice == "1":
        return servers[-1]
    elif choice == "2":
        for i, server in enumerate(servers, start=1):
            print(f"{Fore.CYAN}{i}) {server}")
        index = int(input("Введите номер сервера: ")) - 1
        if 0 <= index < len(servers):
            return servers[index]
        else:
            print(Fore.RED + "Неверный выбор. Запущена последняя сессия.")
            return servers[-1]
    elif choice == "3":
        return add_server()
    else:
        print(Fore.RED + "Неверный ввод. Запущена последняя сессия.")
        return servers[-1]

def add_server():
    server_address = input("Введите IP и порт (например, 127.0.0.1:25565): ")
    save_server(server_address)
    print(Fore.GREEN + "Сервер добавлен.")
    return server_address

def get_ping_interval():
    print(Fore.GREEN + "Выберите интервал пинга:")
    print("1. 5 секунд")
    print("2. 15 секунд")
    print("3. 30 секунд")
    print("4. Указать свое время")
    choice = input("Введите номер (1-4): ")
    
    if choice == "1":
        return 5
    elif choice == "2":
        return 15
    elif choice == "3":
        return 30
    elif choice == "4":
        return int(input("Введите время в секундах: "))
    else:
        print(Fore.RED + "Неверный ввод, установлен интервал 5 секунд по умолчанию.")
        return 5

def check_server(server_address: str, ping_interval: int):
    offline_time = 0  # Счетчик времени недоступности сервера
    server_available = False  # Флаг для отслеживания состояния сервера

    while True:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        try:
            server = JavaServer.lookup(server_address)
            status = server.status()
            print(f"[{Fore.YELLOW}{current_time}{Style.RESET_ALL}] Пинг: {Fore.BLUE}{status.latency:.2f} мс {Style.RESET_ALL}| Игроков онлайн: {Fore.GREEN}{status.players.online}")

            if not server_available:  # Если сервер был недоступен, но теперь доступен
                notify("Сервер запущен", f"Сервер {server_address} снова в сети!")
                print(Fore.GREEN + "Связь установлена!")
                server_available = True  # Обновляем флаг
                offline_time = 0  # Сбрасываем счетчик недоступности
            
        except Exception as e:
            print(f"[{Fore.YELLOW}{current_time}{Style.RESET_ALL}] Сервер недоступен или произошла ошибка: {Fore.RED}{str(e)}")
            offline_time += ping_interval  # Увеличиваем счетчик недоступности
            if offline_time >= 300:  # Если сервер недоступен 5 минут
                server_available = False  # Сбрасываем флаг доступности
        
        time.sleep(ping_interval)  # Задержка перед следующим пингом

if __name__ == "__main__":
    server_address = select_server()
    ping_interval = get_ping_interval()
    check_server(server_address, ping_interval)
