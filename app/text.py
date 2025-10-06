from app import description, keyboard


# Текст для подробного описания сервера
def text(choose, string_):
    answer = string_ + \
             f"\nЦена: {description.servers.get(choose)[3]}р\n\n" \
             f"ОС: Windows (по запросу любую ОС)\n" \
             f"Ядра: {description.servers.get(choose)[1]} Ядра х 2.5-4.0 GHz\n" \
             f"ОЗУ: {description.servers.get(choose)[2]} ГБ\n" \
             f"Интернет: 1 Гб/с\n" \
             f"SSD: 128 Гб\n" \
             f"Локация: {description.servers.get(choose)[0]}"
    return answer


# Текст для подробного описания сервера на сайте p2p
def text_to_p2pkassa(choose):
    answer = f"ОС: Windows; " \
             f"Ядер: {description.servers.get(choose)[1]} (Ядра х 2.5-4.0 GHz); \n" \
             f"ОЗУ: {description.servers.get(choose)[2]} ГБ; \n" \
             f"Интернет: 1 Гб/с; \n" \
             f"SSD: 128 Гб; \n" \
             f"Локация: {description.location.get(description.servers.get(choose)[0])}"
    return answer


# Текст для краткого описания сервера
def buy_server(choose):
    answer = f"{keyboard.s_d.get(choose)[0]}{keyboard.s_d.get(choose)[1]} Ядра (2.5-4.0 GHz) | " \
             f"{keyboard.s_d.get(choose)[2]} озу | 128 ssd | {keyboard.s_d.get(choose)[3]}P"
    return answer
