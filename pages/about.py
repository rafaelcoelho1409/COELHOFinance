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
    st.markdown("""<div style='font-size:25px'>
    Rafael Coelho is a Brazilian Mathematics student 
    who is passionated for Data Science and Artificial Intelligence
    and works in both areas for over three years, with solid knowledge in
    technologic areas such as Machine Learning, Deep Learning, Data Science,
    Computer Vision, Reinforcement Learning, NLP and others.<br>
    Actually, he works in one of the Big Four companies for over a year.""", unsafe_allow_html = True)
    cols = st.columns(3)
    with cols[0]:
        st.image(
            "assets/rafael_coelho_photo.jpeg",
            width = 300)
    with cols[1]:
        card(
            title = "LinkedIn",
            text = "",
            url = "https://www.linkedin.com/in/rafaelcoelho1409/"
        )
    with cols[2]:
        card(
            title = "GitHub",
            text = "",
            url = "https://github.com/rafaelcoelho1409/"
        )

st.divider()
st.markdown("""<div style='font-size:25px'>
<h3>NEXT STEPS</h3>
<b>- Advanced Statistics</b><br>
<b>- Authentication system to avoid too many requests to Yahoo Finance APIs</b><br>
<b>- Anomaly detection:</b> Anomaly detection to detect unusual 
financial market movement (we are intending to
create an alarm tool to allow you to configure a personal alert about these movements)<br>
<b>- Machine Learning predictions:</b> predictions to help you to predict if stock prices and indexes
will go up or down""", unsafe_allow_html = True)

