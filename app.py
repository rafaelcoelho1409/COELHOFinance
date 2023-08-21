import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import show_pages, Page, Section, add_indentation
from streamlit_extras.grid import grid
from functions import option_menu

st.set_page_config(
    page_title = "COELHO Finance",
    layout = "wide"
)

option_menu()

grid1 = grid([1, 5], vertical_align = True)
grid1.image(
    "assets/coelho_finance_logo.png",
)
grid1.markdown(
    """<h2 style='text-align: center'>A new powerful tool to help 
    you make informed investment decisions, track your investments 
    and identify opportunities.</h2><br>""",
    unsafe_allow_html = True
)

with st.expander(
    "Tools", 
    expanded = True):
    st.markdown(
    """<h4 style='text-align: center; font-size:40px'>
    Get to know our financial analysis tools</h4><br>""",
    unsafe_allow_html = True
)
    grid2 = grid(2, 4, vertical_align = True)
    grid2.markdown(f"<div style='text-align:center'><h4>Stock Exchange</h4></div>", unsafe_allow_html = True)
    grid2.markdown(f"<div style='text-align:center'><h4>Market Index</h4></div>", unsafe_allow_html = True)
    UNISTOCK = grid2.button(
        label = "UNISTOCK",
        use_container_width = True)
    MULTISTOCK = grid2.button(
        "MULTISTOCK",
        use_container_width = True)
    UNINDEX = grid2.button(
        label = "UNINDEX",
        use_container_width = True)
    MULTINDEX = grid2.button(
        "MULTINDEX",
        use_container_width = True)
    if UNISTOCK:
        switch_page("UNISTOCK")
    if MULTISTOCK:
        switch_page("MULTISTOCK")
    if UNINDEX:
        switch_page("UNINDEX")
    if MULTINDEX:
        switch_page("MULTINDEX")

st.markdown("""<div style='text-align: center; font-size:25px'>
COELHO Finance is a powerful financial analysis platform 
that helps investors make informed decisions about their investments. 
With COELHO Finance, you can:<br><br></div>""", unsafe_allow_html = True)

with st.expander(
    label = "About tools",
    expanded = True):
    st.markdown("""<div style='font-size:25px'>
        <b>- Analyze individual stocks</b><br>
        With UNISTOCK and UNINDEX tools, COELHO Finance provides 
        comprehensive analysis of individual stocks and indexes from 40+ countries, including 
        financial statements, price charts, analyst ratings and several business indicators about each stock price. 
        This information can help you identify undervalued stocks with the potential for growth.<br><br>""", unsafe_allow_html = True)
    st.markdown("""<div style='font-size:25px'>
        <b>- Compare stocks</b><br>
        With MULTISTOCK and MULTINDEX tools, COELHO Finance allows you to compare 
        the performance of two or more stocks or indexes, so you can see 
        which stocks or indexes are outperforming the market. These informations 
        can help you make informed decisions about which stocks to buy and sell.<br></div>""", unsafe_allow_html = True)
st.markdown("""<div style='text-align: center; font-size:25px'>
COELHO Finance is an essential platform for any investor 
who wants to make informed decisions about their investments. 
With COELHO Finance, you can have the confidence to 
take control of your finances and achieve your investment goals.<br><br>
<b>COELHO Finance is under constant development and is going to have
more tools in the near future, such as AI-based tools that 
will help you to take the best decisions in the financial market.<b><br><br>
</div>""", unsafe_allow_html = True)
st.divider()