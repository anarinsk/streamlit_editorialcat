## Import packages 

import streamlit as st
import pandas as pd
import numpy as np 
from functions_instruments import *
import datetime as dt

## Set credentials
secrets = {
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "client_x509_cert_uri": st.secrets["client_x509_cert_uri"],
    "spread_key": st.secrets["spread_key"],
    "m_pw": st.secrets["m_pw"]
    }

## Functions for streamlit 
@st.cache(allow_output_mutation=True)
def get_data(what="raw"):
    
    df_list = get_data_google_sheets([0,1], secrets)

    if (what=="raw"): 
        key = 0
    else: 
        key = 1
    
    #return df_list[0]
    return generate_record_raw(df_list[key])   

## Loading data 
df = get_data()
## Cut date by 대금 수령일 
date_max_by_paying = df.query("`수령액`>0")['대금 수령일'].max(); df = df.query("`대금 수령일`<=@date_max_by_paying")
today = dt.date.today()

## Main dashboard 
def main(): 
    st.sidebar.subheader('Welcome mel!')
    st.sidebar.write(f'Stats of {today}')

    st.header("🐾🐾🐾Editorial Cat's Dashboard🐈🐈🐈")

    st.subheader("Key work stats")

    total_earning, diff_year_amt, diff_year_pct, latest_month_amt, month_before_amt, diff_month_pct, best_month, best_month_amt = extract_metrics(df)
    month_latest = max(df['대금 수령일']).strftime("%Y-%m")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Earning", f"{total_earning/10**6: ,.2f} M", f"{diff_year_amt/10**6: ,.2f} M ({diff_year_pct*100: .1f}%)")
    col2.metric(f"Latest Monthly ({month_latest})", f"{latest_month_amt: ,.0f}", f"{latest_month_amt - month_before_amt: ,.0f} ({diff_month_pct*100: ,.1f}%)")
    col3.metric(f"The highest monthly is {best_month}", f"{best_month_amt: ,.0f}")
    
    st.markdown("--------")

    st.subheader("Spreadsheet")
    
    date_range = [min(df['대금 수령일']), max(df['대금 수령일'])]
    
    date_0 = st.sidebar.date_input("From (default: earliest)", date_range[0])
    date_1 = st.sidebar.date_input("To (default: latest)",   date_range[1])
    group_by_df = st.sidebar.multiselect(
     'Data by',
     ['발주처', '방영 채널', '작업 종류', '영상 종류'],
     [])
    period_by = st.sidebar.radio("Period by", ('Month', 'Year', 'All'))
    #show_df = st.sidebar.radio("Show table", ('No', 'Yes'))
    
    period_by_2 = {'Month': 'M', 'Year': 'Y', 'All': 'All'}
    df1 = filter_date(date_0, date_1, df)
    df2 = summarise_by_v2(df1, period_by=period_by_2[period_by], group_by=group_by_df)    

    style = {
            '대금 수령일': lambda t: t.strftime("%m/%d/%Y"),
            '단가 평균': '{:,.1f}',
            '번역료': '{:,.0f}',
            '수령액': '{:,.0f}', 
            '발주처': '', 
            '방영 채널': ''            
        }
    
    #st.write(df2.style.format(style))
    st.dataframe(df2.style.format(style), width=1800)

    st.markdown("--------")
    
    st.subheader("Chart")

    container = st.container()
    container.plotly_chart(gen_chart(df2, period_by=period_by_2[period_by], group_by=group_by_df), use_container_width=True) 

## Process credentials
if check_password(secrets):
    main()