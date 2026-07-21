# text.py
from app import description


# Текст для подробного описания сервера
def text(choose, string_):
    s = description.servers[choose]
    answer = string_ + \
             f"\nЦена: {int(s['price'])}р\n\n" \
             f"ОС: Windows (по запросу любую ОС)\n" \
             f"Ядра: {s['cores']} Ядра\n" \
             f"ОЗУ: {s['ram_gb']} ГБ\n" \
             f"Интернет: 1 Гб/с\n" \
             f"SSD: {s['ssd_gb']} Гб\n" \
             f"Локация: {s['flag']}"
    return answer


# Текст для подробного описания сервера на сайте p2p
def text_to_p2pkassa(choose):
    s = description.servers[choose]
    answer = f"ОС: Windows; " \
             f"Ядер: {s['cores']} (Ядра); \n" \
             f"ОЗУ: {s['ram_gb']} ГБ; \n" \
             f"Интернет: 1 Гб/с; \n" \
             f"SSD: {s['ssd_gb']} Гб; \n" \
             f"Локация: {description.location.get(s['flag'])}"
    return answer


# Текст для краткого описания сервера
def buy_server(choose):
    s = description.servers[choose]
    answer = f"{s['flag']}{s['cores']} Ядра | " \
             f"{s['ram_gb']} озу | {s['ssd_gb']} ssd | {int(s['price'])}P"
    return answer
