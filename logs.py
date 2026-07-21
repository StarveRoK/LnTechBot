import logging
import sys
import asyncio

from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Literal, Optional

from aiogram.client.session import aiohttp

from config import PRODUCTION, ADMIN_TOKEN
from zoneinfo import ZoneInfo

# Префикс, чтобы на сайте разработчика отличать алерты этого бота от других проектов,
# использующих тот же tg-send эндпоинт.
NOTIFY_PREFIX = "[LnTechBot]"


class LogLevel(str, Enum):
    """Уровни логирования"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Logger:
    def __init__(
            self,
            name: str = "app",
            log_dir: str = "app",
            level: LogLevel = LogLevel.INFO if PRODUCTION else LogLevel.DEBUG,
            console_output: bool = True,
            file_output: bool = True,
            time_precision: Literal["daily", "hourly", "minutely", "per_second", "per_run"] = "daily",
            max_log_files: int = 200,  # Новый параметр: максимальное количество файлов логов
            log_retention_days: Optional[int] = None  # Опционально: удалять логи старше N дней
    ):
        self.name = name
        self.log_dir = Path(__file__).parent / "logs" / log_dir
        self.error_log_dir = Path(__file__).parent / "logs" / "error"
        self.level = level
        self.time_precision = time_precision
        self.max_log_files = max_log_files
        self.log_retention_days = log_retention_days

        # Создаем папку для логов
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.error_log_dir.mkdir(parents=True, exist_ok=True)

        # Очищаем старые логи если превышен лимит
        self._cleanup_old_logs()

        # Получаем или создаем логгер с уникальным именем
        logger_name = f"{name}" if name else "custom_root"
        self._logger = logging.getLogger(logger_name)

        # ОЧЕНЬ ВАЖНО: Отключаем передачу выше
        self._logger.propagate = False

        # Очищаем существующие хендлеры
        self._logger.handlers.clear()

        # Устанавливаем уровень
        self._logger.setLevel(level.value)

        # Форматтер
        formatter = logging.Formatter(
            '%(levelname)s: %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Хендлер для консоли
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

        # Хендлер для файла
        if file_output:
            log_file = self._get_log_filename(logger_name)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

            error_log_file = self._get_log_filename(logger_name, self.error_log_dir, True)
            error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
            error_file_handler.setFormatter(formatter)
            error_file_handler.setLevel(logging.ERROR)
            self._logger.addHandler(error_file_handler)

    def _cleanup_old_logs(self):
        self._cleanup_directory(self.log_dir)
        self._cleanup_directory(self.error_log_dir)

    def _cleanup_directory(self, directory: Path):
        try:
            log_files = list(directory.glob("*.log"))
            if not log_files:
                return

            if self.log_retention_days is not None:
                cutoff_time = datetime.now(ZoneInfo("Europe/Moscow")).timestamp() - (
                            self.log_retention_days * 24 * 3600)
                for log_file in log_files[:]:
                    try:
                        if log_file.stat().st_mtime < cutoff_time:
                            log_file.unlink()
                            log_files.remove(log_file)
                    except (OSError, FileNotFoundError):
                        continue

            if len(log_files) > self.max_log_files:
                log_files.sort(key=lambda x: x.stat().st_mtime)
                files_to_delete = len(log_files) - self.max_log_files
                for i in range(files_to_delete):
                    try:
                        log_files[i].unlink()
                    except (OSError, FileNotFoundError):
                        continue

        except Exception as e:
            print(f"Ошибка при очистке логов в {directory}: {e}")

    def get_log_files_info(self):
        return {
            "main": self._get_dir_info(self.log_dir),
            "errors": self._get_dir_info(self.error_log_dir)
        }

    def _get_dir_info(self, directory: Path) -> dict:

        try:
            log_files = list(directory.glob("*.log"))  # ← было self.log_dir
            if not log_files:
                return {"total_files": 0, "files": []}

            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            files_info = []
            for log_file in log_files:
                try:
                    stat = log_file.stat()
                    files_info.append({
                        "name": log_file.name,
                        "size_kb": round(stat.st_size / 1024, 2),
                        "created": datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                except OSError:
                    continue

            return {
                "total_files": len(files_info),
                "max_files": self.max_log_files,
                "retention_days": self.log_retention_days,
                "files": files_info[:10]
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_log_filename(self, logger_name: str, directory: Path = None, is_error: bool = False) -> Path:

        """Генерирует имя файла лога в зависимости от настроек точности времени"""
        directory = directory or self.log_dir
        now = datetime.now(ZoneInfo("Europe/Moscow"))

        if is_error:
            time_format = now.strftime('%Y%m%d')
            return directory / f"error_{time_format}.log"

        # Счетчик для уникальности файлов при time_precision="per_run"
        if not hasattr(self, '_run_counter'):
            self._run_counter = 0

        if self.time_precision == "daily":
            # Формат: YYYYMMDD
            time_format = now.strftime('%Y%m%d')
        elif self.time_precision == "hourly":
            # Формат: YYYYMMDD_HH
            time_format = now.strftime('%Y%m%d_%H')
        elif self.time_precision == "minutely":
            # Формат: YYYYMMDD_HHMM
            time_format = now.strftime('%Y%m%d_%H%M')
        elif self.time_precision == "per_second":
            # Формат: YYYYMMDD_HHMMSS
            time_format = now.strftime('%Y%m%d_%H%M%S')
        elif self.time_precision == "per_run":
            # Уникальный файл для каждого запуска
            self._run_counter += 1
            time_format = now.strftime('%Y%m%d_%H%M%S') + f"_{self._run_counter:03d}"
        else:
            # По умолчанию - daily
            time_format = now.strftime('%Y%m%d')

        return directory / f"{logger_name}_{time_format}.log"

    async def _send_msg_developer(self, text):
        """ Отправляем запрос в проект - поддержку """

        url = 'https://alex-starver.ru/api/v1/tg-send'

        # Добавляем заголовок с Bearer token
        headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }

        data = {
            'text': f"{NOTIFY_PREFIX} {text}"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=10) as response:
                    response_data = await response.json()

                    if response.status != 200:
                        # self._logger напрямую, а не log.error(): иначе неуспешная отправка
                        # сама рекурсивно планирует ещё одну отправку на каждый вызов.
                        self._logger.error(
                            f"не удалось отправить разработчику сообщение: "
                            f"{response.status} - {response_data.get('detail', 'Неизвестная ошибка')}"
                        )
                    return None

        except asyncio.TimeoutError:
            self._logger.warning("Таймаут при отправке в чат разработчику")
            return None

        except Exception as e:
            self._logger.warning(f"Ошибка сети при отправке в чат разработчику: {e}")
            return None

    def debug(self, message: str, **kwargs):
        """Логирование на уровне DEBUG"""
        extra_info = self._format_extra_info(kwargs)
        full_message = f"{message}{extra_info}"
        self._logger.debug(full_message)

    def info(self, message: str, **kwargs):
        """Логирование на уровне INFO"""
        extra_info = self._format_extra_info(kwargs)
        full_message = f"{message}{extra_info}"
        self._logger.info(full_message)

    def warning(self, message: str, **kwargs):
        """Логирование на уровне WARNING"""
        extra_info = self._format_extra_info(kwargs)
        full_message = f"{message}{extra_info}"
        self._logger.warning(full_message)

    def error(self, message: str, **kwargs):
        """Логирование на уровне ERROR"""
        extra_info = self._format_extra_info(kwargs)
        full_message = f"{message}{extra_info}"
        asyncio.create_task(self._send_msg_developer(full_message))
        self._logger.error(full_message)

    def critical(self, message: str, **kwargs):
        """Логирование на уровне CRITICAL"""
        extra_info = self._format_extra_info(kwargs)
        full_message = f"{message}{extra_info}"
        asyncio.create_task(self._send_msg_developer(full_message))
        self._logger.critical(full_message)

    def exception(self, message: str, exc_info: Exception = None, **kwargs):
        """Логирование исключений с traceback"""
        extra_info = self._format_extra_info(kwargs)
        full_message = f"{message}{extra_info}"
        self._logger.exception(full_message, exc_info=exc_info)

    def _format_extra_info(self, kwargs: dict) -> str:
        """Форматирование дополнительной информации"""
        if not kwargs:
            return ""

        extra_parts = []
        for key, value in kwargs.items():
            if value is not None:
                extra_parts.append(f"{key}={value}")

        if extra_parts:
            return f" [{' '.join(extra_parts)}]"
        return ""


log = Logger(name="LnTechBot", log_dir="app")
