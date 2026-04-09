import streamlit as st
import pandas as pd

st.title("MY WEB APPLICATION")
st.text("Yeh, this is really my first app",text_alignment="right")

data = st.slider("Select a specific value", 0,30,15)

st.write("The selected value is:",data)

st.header("I am a header!")

st.subheader("I am a subheader!")

st.write("I am a text!")

st.header("I am :green[green]")

st.header("I am **bold**")

st.write("My age is:",40)

my_list = ["Phyton", "C++", "Java"]
st.write("My list is:", my_list)

my_dict = {"First Lang":"Phyton","Second Lang":"C++","Third Lang":"Java",}
st.write("My dictionary is:",my_dict)

my_new_dict = {"Item 1":[1, 2, 3],"Item 2":["A", "B", "C"]}
df = pd.DataFrame(my_new_dict)
st.write("This is a data frame",df)

my_sports = ["Soccer","Tennis","Basketball"]
if st.button("Sports",type="primary"):
    st.write(my_sports)

check_out = st.checkbox("Che squadra ha la tifoseria migliore del mondo?")

if check_out:
    st.write("Interista chiacchierone")
else:
    st.write("Milan")

# Radio button
fav_sport = st.radio("What is your favourite sport?",my_sports)

if fav_sport == "Soccer":
    st.write("Interista Puzzone")
else:
    st.write("Milan Domina")

# Selectbox
my_sports_tup = ("Soccer","Tennis","Basketball")
chk_selection = st.selectbox("Which sport?",my_sports_tup)

st.write("You like " + chk_selection)
st.write("You like ", chk_selection)

# Multiselect
players_gol_dict = {"Marchesi Davide":"100","Ronaldo":"10","Messi":"20"}
name_players = {"Marchesi Davide","Ronaldo","Messi"}
select_players = st.multiselect("Select Player:",name_players)

for player in select_players:
    st.write(f"{player} realized {players_gol_dict[player]} goals")


# Range slider
age_range = st.slider("Select the age range", 18, 99, (32,40))
st.write("The range of ages is:",age_range)

# Text input
my_name = st.text_input("Enter your name:","Fofana")
st.write("My name is:",my_name)

# Numerical input
my_age = st.number_input("What is your age?",min_value=18,max_value=99,value=50,step=1)
st.write(f"Your age is:{my_age}")

# Form
with st.form("Please fill the form"):
    age_range_form = st.slider("Select the age range", 18, 99, (32,40))
    my_name_form = st.text_input("Enter your name:","Fofana")    
    my_age_form = st.number_input("What is your age?",min_value=18,max_value=99,value=50,step=1)
    summetted = st.form_submit_button()

if summetted:
    st.success(f"Your name is {my_name_form} and you are {my_age_form} years old")