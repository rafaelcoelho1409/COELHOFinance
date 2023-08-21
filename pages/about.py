import streamlit as st
from streamlit_extras.grid import grid
import webbrowser

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
    linkedin = row1.button(
        label = "LinkedIn",
        use_container_width = True
    )
    github = row1.button(
        label = "GitHub",
        use_container_width = True
    )
    if linkedin:
        webbrowser.open_new_tab("https://www.linkedin.com/in/rafaelcoelho1409/")
    if github:
        webbrowser.open_new_tab("https://www.github.com/rafaelcoelho1409/")

