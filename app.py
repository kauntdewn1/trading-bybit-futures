#!/usr/bin/env python3
"""
App principal para deploy - Bybit Futures Trading Dashboard
"""
import streamlit as st
from futures_dashboard import *

if __name__ == "__main__":
    st.set_page_config(
        page_title="Bybit Futures Trading Dashboard",
        page_icon="🥷",
        layout="wide"
    )
    
    # Executa o dashboard
    main()
