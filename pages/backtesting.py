import streamlit as st 
from streamlit_extras.grid import grid
from functions import (
    option_menu,
    image_border_radius,
    page_buttons
)

PAGE_TITLE = "COELHO Finance | Backtesting"
st.set_page_config(
    page_title = PAGE_TITLE,
    layout = "wide",
    initial_sidebar_state = "collapsed"
)

option_menu()

grid_title = grid([5, 1], vertical_align = True)
container1 = grid_title.container()
container1.title("$$\\large{\\textbf{COELHO Finance | Backtesting}}$$")
container1.caption("Author: Rafael Silva Coelho")
image_border_radius("./assets/coelho_finance_logo.png", 15, 60, 60, grid_title)

page_buttons()

st.write("$$\\textbf{Under Construction}$$")