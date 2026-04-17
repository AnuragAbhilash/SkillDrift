# app.py
import streamlit as st

st.title("SkillDrift")
name = st.text_input("Enter your name")

if name:
    st.write("Hello", name)