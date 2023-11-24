import streamlit as st
from streamlit_extras.grid import grid
from streamlit_card import card
from streamlit_extras.switch_page_button import switch_page
from functions import option_menu, image_border_radius

st.set_page_config(
    page_title = "COELHO Finance - About Us",
    layout = "wide"
)

option_menu()

st.title("$$\\large{\\textbf{About Us}}$$")

grid_ = grid(4, vertical_align = True)
UNIMARKET = grid_.button(
    label = "$$\\textbf{UNIMARKET}$$",
    use_container_width = True)
UNISTATS = grid_.button(
    label = "$$\\textbf{UNISTATS}$$",
    use_container_width = True)
MULTIMARKET = grid_.button(
    "$$\\textbf{MULTIMARKET}$$",
    use_container_width = True)
ABOUT_US = grid_.button(
    "$$\\textbf{About Us}$$",
    use_container_width = True)
if UNIMARKET:
    switch_page("UNIMARKET")
if UNISTATS:
    switch_page("UNISTATS")
if MULTIMARKET:
    switch_page("MULTIMARKET")  
if ABOUT_US:
    switch_page("About Us")
st.divider()

with st.expander(
    label = "Author",
    expanded = True
):
    st.write("$$\\underline{\\Large{\\textbf{Author}}}$$")
    grid1 = grid([1, 2], vertical_align = True)
    image_border_radius("assets/rafael_coelho_1.jpeg", 20, grid1)
    container1 = grid1.container()
    container1.markdown("""<div style='font-size:25px; text-align: center'>
    Rafael Coelho is a Brazilian Mathematics student 
    who is passionated for Data Science and Artificial Intelligence
    and works in both areas for over three years, with solid knowledge in
    technologic areas such as Machine Learning, Deep Learning, Data Science,
    Computer Vision, Reinforcement Learning, NLP and others.<br>
    Recently, he worked in one of the Big Four companies for over a year.</div>
    """, unsafe_allow_html = True)
    test = container1.columns(3)
    with test[0]:
        st.markdown("""
    <div>
    <h1>
    <a 
        style='text-align:center;'
        href='https://rafaelcoelho.streamlit.app/'>
    Portfolio
    </a>
    </h1>
    </div>""", unsafe_allow_html = True)
    with test[1]:
        st.markdown("""
    <div>
    <h1>
    <a 
        style='text-align:center;'
        href='https://www.linkedin.com/in/rafaelcoelho1409/'>
    LinkedIn
    </a>
    </h1>
    </div>""", unsafe_allow_html = True)
    with test[2]:
        st.markdown("""
    <div>
    <h1>
    <a
        style='text-align:center;'
        href='https://github.com/rafaelcoelho1409/'>
    GitHub
    </a>
    </h1>
    </div>""", unsafe_allow_html = True)


st.divider()
st.markdown("""<div style='font-size:25px'>
<h3>NEXT STEPS</h3>
<b>- Advanced Statistics</b><br>
<b>- Machine Learning predictions:</b> predictions to help you to predict if stock prices and indexes
will go up or down""", unsafe_allow_html = True)
