import streamlit as st

from servicos.busca_servico import onde_assistir
from servicos.favoritos_servico import listar_favoritos, remover_favorito


def renderizar() -> None:
    st.header("Minhas listas")
    usuario_id = st.session_state["usuario_id"][0]

    st.subheader("Favoritos")
    filmes = listar_favoritos(usuario_id)

    if not filmes:
        st.info(
            "Você ainda não tem favoritos. Busque um filme e clique em "
            "**Favoritar** para vê-lo aqui."
        )
    else:
        quantidade = len(filmes)
        sufixo = "s" if quantidade > 1 else ""
        st.caption(f"{quantidade} filme{sufixo} favorito{sufixo}.")

        for filme in filmes:
            with st.container(border=True):
                titulo = f"{filme.titulo} ({filme.ano})" if filme.ano else filme.titulo
                st.subheader(titulo)

                if filme.generos:
                    st.write("**Gêneros:** " + ", ".join(filme.generos))

                streamings = onde_assistir(filme.id)
                if streamings:
                    st.write("**Onde assistir:** " + ", ".join(streamings))
                else:
                    st.write("**Onde assistir:** não disponível nos streamings cadastrados")

                if st.button(
                    "Remover dos favoritos",
                    key=f"lista_remover_fav_{filme.id}",
                    icon=":material/delete:",
                ):
                    remover_favorito(usuario_id, filme.id)
                    st.rerun()

    # TODO (Sprint 3, H4.3): lista da watchlist.
