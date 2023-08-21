import streamlit as st
from streamlit_extras.grid import grid
from functions import option_menu

st.set_page_config(
    page_title = "COELHO Finance - About Us",
    layout = "wide"
)

option_menu()

st.title("About")

with st.expander(
    label = "Author",
    expanded = True
):
    row1 = grid([1, 5], 2, vertical_align = True)
    row1.image(
        "assets/rafael_coelho_photo.jpeg",
        width = 200
    )
    row1.markdown("""<div style='font-size:25px'>
    <h3>Author</h3>
    Rafael Coelho is a Brazilian Mathematics student 
    who is passionated for Data Science and Artificial Intelligence
    and works in both areas for over three years, with solid knowledge in
    technologic areas such as Machine Learning, Deep Learning, Data Science,
    Computer Vision, Reinforcement Learning, NLP and others.<br>
    Actually, he works in one of the Big Four companies for over a year.""", unsafe_allow_html = True)
    row1.markdown(
        """
        <div style='text-align:center; font-size:30px'>
        <a 
            href='https://www.linkedin.com/in/rafaelcoelho1409/'>
                LinkedIn
        </a>
        </div>
        """,
        unsafe_allow_html = True
    )
    row1.markdown(
        """
        <div style='text-align:center; font-size:30px'>
        <a 
            href='https://github.com/rafaelcoelho1409/'>
                GitHub
        </a>
        </div>
        """,
        unsafe_allow_html = True
    )

