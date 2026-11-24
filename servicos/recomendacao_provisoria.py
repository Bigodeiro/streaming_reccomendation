"""Compatibilidade: a ponte provisória virou o serviço definitivo.

Use `servicos.recomendacao_servico`. Este módulo continua exportando as mesmas
funções para não quebrar quem ainda importa o caminho antigo.
"""

from servicos.recomendacao_servico import (  # noqa: F401
    MIN_FAVORITOS,
    planos_do_streaming,
    recomendar,
)

__all__ = ["MIN_FAVORITOS", "planos_do_streaming", "recomendar"]
