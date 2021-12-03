import streamlit as st
import pandas as pd
import numpy as np 
import streamlit_authenticator as stauth
from functions_instruments import *
import datetime as dt
from SessionState import get


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
session_state = get(password='')

def main(): 
    st.sidebar.write('Welcome *%s*' % (name))
    st.sidebar.write(f'Stats of {today}')
    st.title("Editorial Cat's Work Stats")
    
    date_range = [df.head(1)['대금 수령일'].item(), df.tail(1)['대금 수령일'].item()]
    
    date_0 = st.sidebar.date_input("From", date_range[0])
    date_1 = st.sidebar.date_input("To",   date_range[1])
    group_by = st.sidebar.radio("Group by", ('all', '발주처', '방영 채널'))
    show_df = st.sidebar.radio("Show table", ('No', 'Yes'))
    
    df1 = filter_date(date_0, date_1, df)
    df2 = summarise_by_month(df1, group_by=[group_by])
    
    style = {
            '단가 평균': '{:,.2f}',
            '번역료': '{:,.0f}',
            '수령액': '{:,.0f}', 
            '발주처': '', 
            '방영 채널': ''            
        }
    
    #if group_by=="all": 
    #    df3 = summarise_by_month(df1, group_by='all')
    #else: 
    #    group_by_2 = ['발주처', '방영 채널']
    #    group_by_2.remove(group_by)
    #    df3 = df2.drop(group_by_2, axis=1)
                                 
    #st.dataframe(df2.style.format(style))
    st.plotly_chart(draw_hbar(df2, group_by), use_container_width=True)
    st.write("***")
    if (show_df=="Yes"): 
        st.subheader("Check the number")
        st.dataframe(df2.style.format(style)) 
    
#    
if session_state.password != st.secrets['m_pw']:
    pwd_placeholder = st.empty()
    pwd = pwd_placeholder.text_input("Password:", value="", type="password")
    session_state.password = pwd
    if session_state.password == st.secrets['m_pw']:
        pwd_placeholder.empty()
        main()
    else:
        st.error("the password you entered is incorrect")
else:
    main()
