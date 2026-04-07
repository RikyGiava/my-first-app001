import streamlit as st
st.title("MY WEB APPLICATION")
st.text("Yeh, this is really my first app",text_alignment="right")

data = st.slider("Select a specific value", 0,30,15)

st.write("The selected value is:",data)
