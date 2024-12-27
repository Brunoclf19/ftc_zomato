import streamlit as st
from PIL import Image

# Configurar título da página
st.set_page_config(
    page_title="Fome Zero", 
    page_icon="🍽️", 
    layout="wide"
    )

image = Image.open('logo-inicio.jpg')
st.sidebar.image(image, width=300)

# Título e subtítulo
st.title("🍽️ Fome Zero")
st.subheader("Explore dados sobre restaurantes ao redor do mundo de forma interativa e intuitiva!")

# Descrição geral
st.markdown("""
Este dashboard foi desenvolvido para proporcionar insights valiosos sobre restaurantes, países, cidades e tipos de culinária. 
Você poderá explorar:
- Informações gerais sobre restaurantes cadastrados.
- Análises detalhadas por país, cidade e tipos de culinária.
- Comparações específicas, como preços médios e avaliações.

**Como usar:**
1. Use o menu lateral para selecionar uma categoria de análise.
2. Ajuste os filtros para personalizar sua visualização.
3. Navegue pelos gráficos e tabelas para obter insights detalhados.
""")

# Guia de navegação
st.markdown("### 🧭 Guia de Navegação")
st.markdown("""
- **Geral:** Resumo de todos os dados disponíveis.
- **País:** Detalhamento de restaurantes e cidades por país.
- **Cidade:** Análises específicas de cidades com restaurantes registrados.
- **Restaurantes:** Informações detalhadas sobre estabelecimentos.
- **Tipos de Culinária:** Comparações e rankings por tipo de culinária.
""")

# Créditos e Contato
st.markdown("### 👩‍💻 Sobre o criador")
st.markdown("""
Este dashboard foi desenvolvido por Bruno Freitas, um cientista de dados apaixonado por explorar e compartilhar insights valiosos.

**📧 Entre em contato:** 
- [LinkedIn](https://www.linkedin.com/in/bruno-freitas-mat-est/)  
- [E-mail](https://mailto:brunoclf19@gmail.com)
""")

# Rodapé
st.markdown("___")
st.caption("Dashboard desenvolvido com ❤️ usando Python e Streamlit.")
