#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Executa tarefas administrativas do Django definindo o módulo de configurações padrão e executando comandos da linha de comando.
    Lança um ImportError com uma mensagem útil se o Django não estiver instalado ou disponível no ambiente.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Tem certeza de que ele está instalado e "
            "disponível na variável de ambiente PYTHONPATH? Você esqueceu de ativar um ambiente virtual?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
