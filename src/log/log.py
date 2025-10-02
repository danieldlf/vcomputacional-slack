import logging
import sys
from pathlib import Path

class Logger:
    _instance = None

    def __new__(cls, logfile: str = "app.log"):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)

            # cria diretório se não existir
            Path(logfile).parent.mkdir(parents=True, exist_ok=True)

            # configura logger
            logger = logging.getLogger("AmaranteLogger")
            logger.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # handler para arquivo
            file_handler = logging.FileHandler(logfile)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)

            # handler para terminal
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            # evita duplicar handlers
            if not logger.handlers:
                logger.addHandler(file_handler)
                logger.addHandler(console_handler)

            cls._instance.logger = logger

        return cls._instance

    def get_logger(self):
        return self._instance.logger
