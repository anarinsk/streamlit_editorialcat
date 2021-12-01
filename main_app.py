import streamlit as st
import pandas as pd
import numpy as np 
import streamlit_authenticator as stauth
from functions_instruments import *
from datetime import date 

#import gspread
#from google.oauth2.service_account import Credentials
#from functions_instruments import *

def get_data(what="record"):
    
    df_list = get_data_google_sheets(st.secrets['gspread_key'], [4,5])
    
    if (what=="record"): 
        key = 0
    else: 
        key = 0
    
    return generate_record_raw(df_list[key])   
#
df_record = get_data("record")
today = date.today()
#
import app_0
import app_1
import app_2

PAGES = {
     "Overview"    : app_0,
     "Stocks Stats": app_1,
     "Price Taker" : app_2
}

# Login 
names = [st.secrets['a_name'], st.secrets['m_name']]
usernames = [st.secrets['a_id'], st.secrets['m_id']]
hashed_passwords = [st.secrets['a_pw'], st.secrets['m_pw']]
#
authenticator = stauth.authenticate(names,usernames,hashed_passwords,
                                    'cookie', '1slghnlm;sf', cookie_expiry_days=30)
#
name, authentication_status = authenticator.login('Login','main')

#st.write(st.session_state)

if st.session_state['authentication_status']:
    st.write('Welcome *%s*' % (name))
    st.write(f'Stats of {today}')
    #st.sidebar.title('Navigation')
    #selection = st.sidebar.selectbox("Go to", list(PAGES.keys()))
    #page = PAGES[selection]
    #page.app(df_snapshot)
    st.write(df_record)
    
elif st.session_state['authentication_status']==False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status']==None:
    st.warning('Please enter your username and password')