"""Identidade visual: nome, logo, tokens de cor e o CSS comum a todas as telas.

Segue o guia em docs/DESIGN.md. Os tokens aparecem aqui como variáveis CSS
(--qs-*) e no tema em .streamlit/config.toml; mudar uma cor exige mexer nos dois
e conferir o contraste (seção 2.4 do guia).
"""

from html import escape
from pathlib import Path

import streamlit as st

NOME_APP = "Streaming Recommendation"
SLOGAN = "Descubra qual streaming combina com seus favoritos."

CAMINHO_LOGO = Path(__file__).resolve().parent.parent / "assets" / "logo.svg"

# Etiqueta de cada streaming: (fundo, texto, borda). Pares validados para WCAG AA.
ESTILOS_STREAMINGS = {
    "Netflix": ("#B20710", "#FFFFFF", "#FF8A82"),
    "Prime Video": ("#00A8E1", "#0B0B0D", None),
    "Max": ("#002BE7", "#FFFFFF", None),
    "Globoplay": ("#FB4E22", "#0B0B0D", None),
    "Disney+": ("#113CCF", "#FFFFFF", None),
    "Apple TV+": ("#6E6E73", "#FFFFFF", "#A3A3A8"),
    "Paramount+": ("#0064FF", "#FFFFFF", None),
}
ESTILO_STREAMING_PADRAO = ("#4A4A52", "#FFFFFF", None)

_CSS = """
<style>
:root {
    --qs-background: #0B0B0D;
    --qs-surface: #18181C;
    --qs-surface-raised: #202025;
    --qs-border: #2A2A30;
    --qs-text-primary: #F5F5F1;
    --qs-text-secondary: #A3A3A8;
    --qs-text-tertiary: #96969B;
    --qs-accent: #E50914;
    --qs-accent-hover: #C8101A;
    --qs-gradient: linear-gradient(90deg, #E50914, #FF4B3E);
    --qs-genre-bg: #26262B;
    --qs-genre-text: #DCDCE0;
    --qs-focus-ring: #FF8A82;
}

/* Barra de busca (4.1): pílula, foco visível. Escopada pelo container key="qs-search". */
.st-key-qs-search [data-baseweb="input"] {
    border-radius: 999px;
    padding: 0.35rem 0.75rem;
    background: var(--qs-surface);
}
.st-key-qs-search [data-baseweb="input"]:hover { border-color: #3A3A42; }
.st-key-qs-search [data-baseweb="input"]:focus-within {
    border-color: var(--qs-focus-ring);
    box-shadow: 0 0 0 3px rgba(255, 138, 130, 0.22), 0 0 24px rgba(229, 9, 20, 0.18);
}
.st-key-qs-search input { font-size: 1.05rem; }

/* Marca (cabeçalho) */
.qs-brand { text-align: center; padding: 3rem 0 1.5rem; }
.qs-brand-mark { width: 64px; height: 64px; display: inline-block; }
.qs-brand-mark svg { width: 100%; height: 100%; }
.qs-brand-title {
    font-size: 2.5rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15;
    color: var(--qs-text-primary); margin-top: 0.5rem;
}
.qs-brand-tagline { color: var(--qs-text-secondary); font-size: 1rem; margin-top: 0.5rem; }

.qs-brand.compacto {
    display: flex; align-items: center; gap: 0.75rem; text-align: left; padding: 0.5rem 0 1rem;
}
.qs-brand.compacto .qs-brand-mark { width: 36px; height: 36px; }
.qs-brand.compacto .qs-brand-title { font-size: 1.4rem; margin-top: 0; }

/* Títulos de página e seção */
.qs-page-title { font-size: 1.85rem; font-weight: 700; margin: 0; color: var(--qs-text-primary); }
.qs-page-subtitle { color: var(--qs-text-secondary); margin: 0.25rem 0 0.5rem; }
.qs-section { margin-top: 2rem; }
.qs-section-title { font-size: 1.35rem; font-weight: 700; margin: 0 0 0.75rem; color: var(--qs-text-primary); }
.qs-results-caption { color: var(--qs-text-secondary); font-size: 0.9rem; margin: 0.25rem 0; }

/* Cards (4.3): elevação sutil, sem hover porque só o botão é acionável. */
[class*="st-key-qs-card-"] { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18); }
.qs-filme-titulo { font-size: 1.1rem; font-weight: 600; margin: 0; color: var(--qs-text-primary); }
.qs-filme-ano { color: var(--qs-text-secondary); font-weight: 400; }
.qs-rotulo { color: var(--qs-text-tertiary); font-size: 0.8rem; margin: 0.75rem 0 0.35rem; }
.qs-meta { color: var(--qs-text-tertiary); font-size: 0.85rem; }

/* Chips (4.2): informativos, não clicáveis. */
.qs-chips { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.qs-chip {
    display: inline-flex; align-items: center; min-height: 28px; box-sizing: border-box;
    padding: 0 0.75rem; border-radius: 999px; border: 1px solid transparent;
    font-size: 0.82rem; font-weight: 600; white-space: nowrap;
}
.qs-chip--genre { background: var(--qs-genre-bg); color: var(--qs-genre-text); font-weight: 500; }

/* "Como funciona" */
.qs-passo { text-align: center; padding: 0.5rem; }
.qs-passo-num {
    display: inline-flex; align-items: center; justify-content: center;
    width: 2.25rem; height: 2.25rem; border-radius: 50%;
    background: var(--qs-surface-raised); border: 1px solid var(--qs-border);
    color: var(--qs-text-primary); font-weight: 700;
}
.qs-passo-titulo { font-size: 1.05rem; font-weight: 600; margin: 0.6rem 0 0.25rem; color: var(--qs-text-primary); }
.qs-passo p { color: var(--qs-text-secondary); font-size: 0.92rem; margin: 0; }

/* Estado vazio (4.5) */
.qs-empty { text-align: center; padding: 1.5rem 1rem 0.5rem; }
.qs-empty-icon { font-family: "Material Symbols Rounded"; font-size: 2.5rem; color: var(--qs-text-secondary); }
.qs-empty-title { font-size: 1.15rem; font-weight: 600; margin: 0.25rem 0; color: var(--qs-text-primary); }
.qs-empty p { color: var(--qs-text-secondary); margin: 0; }

/* Item do ranking (4.7) e planos (4.8) */
.qs-rank-head { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.qs-rank-pos {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 2.5rem; height: 2.5rem; border-radius: 0.5rem;
    background: var(--qs-surface-raised); border: 1px solid var(--qs-border);
    font-weight: 700; color: var(--qs-text-primary);
}
.qs-rank-nome { font-size: 1.15rem; font-weight: 600; color: var(--qs-text-primary); flex: 1; }
.qs-afinidade { display: flex; flex-direction: column; align-items: flex-end; line-height: 1.2; }
.qs-afinidade strong { font-size: 1.35rem; color: var(--qs-text-primary); }
.qs-afinidade span { font-size: 0.78rem; color: var(--qs-text-tertiary); }
.qs-rank-favs { color: var(--qs-text-secondary); font-size: 0.92rem; margin: 0.6rem 0 0; }
.qs-planos { list-style: none; padding: 0; margin: 0; }
.qs-plano {
    display: flex; align-items: baseline; gap: 0.75rem; flex-wrap: wrap;
    padding: 0.5rem 0; border-top: 1px solid var(--qs-border);
}
.qs-plano:first-child { border-top: none; padding-top: 0; }
.qs-plano-nome { color: var(--qs-text-primary); flex: 1; min-width: 8rem; }
.qs-price { font-weight: 700; color: var(--qs-text-primary); }
.qs-price-period { font-weight: 400; color: var(--qs-text-secondary); font-size: 0.85rem; }
.qs-price-meta { color: var(--qs-text-tertiary); font-size: 0.8rem; }

.qs-rodape { text-align: center; color: var(--qs-text-tertiary); font-size: 0.8rem; margin-top: 3rem; }

/* Celular (2.2): marca e títulos menores. */
@media (max-width: 640px) {
    .qs-brand { padding: 1.5rem 0 1rem; }
    .qs-brand-title { font-size: 2rem; }
    .qs-page-title { font-size: 1.6rem; }
}
</style>
"""


def aplicar_estilo() -> None:
    """Injeta o CSS da identidade visual. Chamar uma vez por execução, no app.py."""
    st.html(_CSS)


def logo_svg() -> str:
    """Conteúdo do SVG da logo, para desenhar inline no HTML."""
    return CAMINHO_LOGO.read_text(encoding="utf-8")


def cabecalho(compacto: bool = False) -> None:
    """Marca: grande e centralizada na Home vazia, compacta nas demais situações."""
    classe = "qs-brand compacto" if compacto else "qs-brand"
    slogan = "" if compacto else f'<div class="qs-brand-tagline">{escape(SLOGAN)}</div>'
    st.html(
        f'<div class="{classe}"><span class="qs-brand-mark" aria-hidden="true">{logo_svg()}</span>'
        f'<div><div class="qs-brand-title">{escape(NOME_APP)}</div>{slogan}</div></div>'
    )


def titulo_pagina(titulo: str, subtitulo: str = "") -> None:
    sub = f'<p class="qs-page-subtitle">{escape(subtitulo)}</p>' if subtitulo else ""
    st.html(f'<h1 class="qs-page-title">{escape(titulo)}</h1>{sub}')


def estado_vazio(icone: str, titulo: str, texto: str) -> None:
    """Ícone (nome do Material Symbol, ex. 'favorite'), título e explicação. A ação fica com quem chama."""
    st.html(
        f'<div class="qs-empty"><div class="qs-empty-icon" aria-hidden="true">{escape(icone)}</div>'
        f'<p class="qs-empty-title">{escape(titulo)}</p><p>{escape(texto)}</p></div>'
    )


def chips_streamings(nomes: list[str]) -> str:
    """HTML das etiquetas coloridas com o nome de cada streaming."""
    partes = []
    for nome in nomes:
        fundo, texto, borda = ESTILOS_STREAMINGS.get(nome, ESTILO_STREAMING_PADRAO)
        estilo = f"background:{fundo};color:{texto}" + (f";border-color:{borda}" if borda else "")
        partes.append(f'<span class="qs-chip qs-chip--stream" style="{estilo}">{escape(nome)}</span>')
    return "".join(partes)


def chips_generos(generos: list[str]) -> str:
    return "".join(f'<span class="qs-chip qs-chip--genre">{escape(g)}</span>' for g in generos)


def rodape() -> None:
    nome_usuario = st.session_state.get("usuario_id", (None, ""))[1]
    perfil = f" · Perfil de demonstração: {escape(nome_usuario)}" if nome_usuario else ""
    st.html(f'<div class="qs-rodape">{escape(NOME_APP)} — Engenharia de Software II{perfil}</div>')
