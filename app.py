import streamlit as st
import json
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.grid import grid
from functions import (
    option_menu, 
    image_border_radius,
    create_scrollable_section)

st.set_page_config(
    page_title = "COELHO Finance",
    layout = "wide",
    initial_sidebar_state = "collapsed"
)

option_menu()

layout = grid([1, 0.2, 2], vertical_align = True)
first_column = layout.container()
layout.container()
second_column = layout.container()
image_border_radius("assets/coelho_finance_logo.png", 20, 100, 100, first_column)
first_column.caption("Author: Rafael Silva Coelho")

UNIMARKET = first_column.button(
    label = "$$\\textbf{UNIMARKET}$$",
    use_container_width = True)
UNISTATS = first_column.button(
    label = "$$\\textbf{UNISTATS}$$",
    use_container_width = True)
MULTIMARKET = first_column.button(
    "$$\\textbf{MULTIMARKET}$$",
    use_container_width = True)
ABOUT_US = first_column.button(
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

first_column.info("""
This tool provides information for general purposes and should not be taken as investment advice. 
It doesn't account for individual financial circumstances or goals. 
\nUsers should make investment decisions based on their own financial needs and risk tolerance, 
and consult with a professional advisor. Past performance of securities or strategies 
doesn't guarantee future results. The tool's creators are not responsible for any 
financial decisions or losses resulting from its use.""")

second_column.latex("\\Huge{\\textbf{COELHO Finance}}")
header = """
<h2 style='text-align: center'>A new powerful tool to help 
you make informed investment decisions, track your investments 
and identify opportunities.</h2><br>
"""
unimarket_content = """
<i><h1>UNIMARKET</h1></i>
<h3>Analyze individual stocks</h3>
<div style='font-size:20px'>
COELHO Finance provides comprehensive analysis of individual stocks and indexes 
from 40+ countries, including financial statements, price charts, analyst ratings 
and several business indicators about each stock price. 
This information can help you identify undervalued stocks with the potential for growth.
</div>"""
unistats_content = """
<i><h1>UNISTATS</h1></i>
<h3>Get statistical informations</h3>
<div style='font-size:20px'>
COELHO Finance brings to you statistical models as outlier detections,
moving averages, forecast models, anomaly detection, volatility models 
and Monte Carlo simulations.
</div>"""
multimarket_content = """
<i><h1>MULTIMARKET</h1></i>
<h3>Compare stocks</h3>
<div style='font-size:20px'>
COELHO Finance allows you to compare the performance of two or more stocks or indexes, 
so you can see which stocks or indexes are outperforming the market. 
These informations can help you make informed decisions about which stocks to buy and sell.
</div>"""
final_content = """
<div style='font-size:20px'><h3><b>
COELHO Finance is under constant development and is going to have more tools in the near future, 
such as AI-based tools that will help you to take the best decisions in the financial market.
</b></h3></div>"""


# Combine all content
combined_content = "<hr>".join([
    header,
    unimarket_content,
    unistats_content,
    multimarket_content,
    final_content
    ])
# Create scrollable section
scrollable_section = create_scrollable_section(combined_content, height="750px")
# Display the scrollable section
second_column.markdown(scrollable_section, unsafe_allow_html=True)

with st.expander(
    label = "COELHO Finance",
    expanded = True
):
    cols1 = grid(5)
    cols2 = grid(5)
    for i in range(1, 6):
        cols1.image(f"assets/coelhofinance{i:0>2}.png")
    for i in range(6, 11):
        cols2.image(f"assets/coelhofinance{i:0>2}.png")
st.divider()