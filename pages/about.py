import streamlit as st
from streamlit_extras.grid import grid
from streamlit_card import card
from functions import option_menu

st.set_page_config(
    page_title = "COELHO Finance - About Us",
    layout = "wide"
)

option_menu()

st.title("About Us")

with st.expander(
    label = "Author",
    expanded = True
):
    st.write("$$\\underline{\\Large{\\textbf{Author}}}$$")
    grid1 = grid([1, 4], vertical_align = True)
    grid1.image("assets/rafael_coelho_1.jpeg")
    grid1.markdown("""<div style='font-size:25px'>
    Rafael Coelho is a Brazilian Mathematics student 
    who is passionated for Data Science and Artificial Intelligence
    and works in both areas for over three years, with solid knowledge in
    technologic areas such as Machine Learning, Deep Learning, Data Science,
    Computer Vision, Reinforcement Learning, NLP and others.<br>
    Actually, he works in one of the Big Four companies for over a year.</div>
    <div>
    <h1>
    <a 
        style='text-align:center;'
        href='https://www.linkedin.com/in/rafaelcoelho1409/'>
    LinkedIn
    </a>
    </h1>
    </div>
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