import streamlit as st
import pandas as pd
import numpy as np 
import streamlit_authenticator as stauth
from functions_instruments import *
import datetime as dt

#import gspread
#from google.oauth2.service_account import Credentials
#from functions_instruments import *

def get_data(what="record"):
    
    df_list = get_data_google_sheets(st.secrets['gspread_key'], [0,1])
    
    if (what=="record"): 
        key = 0
    else: 
        key = 1
    
    return generate_record_raw(df_list[key])   
#
df = get_data()
today = dt.date.today()
#
#import app_0
#import app_1
#import app_2

#PAGES = {
#     "Overview"    : app_0,
#     "Stocks Stats": app_1,
#     "Price Taker" : app_2
#}

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
    st.title("Editorial Cat's Works")
    
    date_range = [df.head(1)['대금 수령일'].item(), df.tail(1)['대금 수령일'].item()]
    
    date_start = st.date_input("From", date_range[0])
    date_end   = st.date_input("To",   date_range[1])
    
    st.dataframe(filter_date(start_date, end_date, df))
    
    #st.write('Your From is:', date_start)
    #st.write('Your To is:', date_end)
   
    
elif st.session_state['authentication_status']==False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status']==None:
    st.warning('Please enter your username and password')