import streamlit as st
import pandas as pd
import numpy as np 
import streamlit_authenticator as stauth

import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
import plotly.express as px

# Functions in Loading data from Google Spreadsheet

def gss_to_df(gc, tab_index):
# Prompts for all spreadsheet values
    values = gc.get_worksheet(tab_index).get_all_values()
    
    # Turns the return into a dataframe
    df = pd.DataFrame(values)
    df.columns = df.iloc[0]
    df.drop(df.index[0], inplace=True)      
    return df

#@st.cache(ttl=60*1)
def get_data_google_sheets(sample_spreadsheet_id, tab_index):
    
    # Link to authenticate 
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]
   
    info = { "type" : "service_account",
             "auth_uri" : "https://accounts.google.com/o/oauth2/auth",
             "token_uri" : "https://oauth2.googleapis.com/token",
             "auth_provider_x509_cert_url" : "https://www.googleapis.com/oauth2/v1/certs",
             "project_id" : st.secrets["project_id"],
             "private_key_id" : st.secrets["private_key_id"],
             "private_key" : st.secrets["private_key"],
             "client_email" : st.secrets["client_email"],
             "client_id" : st.secrets["client_id"],
             "client_x509_cert_uri" : st.secrets["client_x509_cert_uri"],
    }
    
    credentials = Credentials.from_service_account_info(
        info,
        scopes=scopes
    )
    
    # Request authorization and open the selected spreadsheet
    gc = gspread.authorize(credentials).open_by_key(sample_spreadsheet_id)
    df_list = [gss_to_df(gc, k) for k in tab_index]
        
    return df_list

# 
def turn_str_num(col: str) -> float: 
    "turn a str column with comma numeric to float"
    col = col.str.replace("₩", '')
    col = col.str.replace(',', '')
    col = col.str.replace(' ', '')      
    #
    #return col
    return pd.to_numeric(col, errors='coerce')
#
def generate_record_raw(df):
    cols_remove = []
    cols_numeric = ['단가', '번역료', '수령액']
    cols_date = ['마감일', '대금 수령일']
    cols_use = ['발주처', '방영 채널', '작품명 / 시즌', 'Ep', 'RT', '영상 종류', '작업 종류', '마감일',
       '대금 수령일', '단가', '번역료', '수령액', '비고']
    # Cols to be handled 
    df = df.copy()
    df.drop(cols_remove, axis=1, inplace=True)
    df[cols_numeric] = df[cols_numeric].apply(turn_str_num, axis=1)
    df[cols_date] = df[cols_date].apply(pd.to_datetime, axis=1)
    #
    return df[cols_use]

def filter_date(start, end, df, by='`대금 수령일`'):
    return df.query("{0} >= @start & {0} <= @end".format(by)) 

def summarise_by_month(df, time_by='대금 수령일', group_by='all'): 
#    
    df.index = pd.to_datetime(df[time_by],format='%m/%d/%y %I:%M%p')

    def get_metrics(grp_obj):
        mean_danga = grp_obj['단가'].mean()
        sum_bunyuk = grp_obj['번역료'].sum()
        sum_suryung = grp_obj['수령액'].sum()
        return pd.DataFrame({
            "단가 평균": mean_danga, 
            "번역료": sum_bunyuk, 
            "수령액": sum_suryung
            })
    if group_by==["all"]:
        df = df.groupby(pd.Grouper(freq='M')).pipe(get_metrics)
        cols_arange = ['년도-월','단가 평균', '번역료', '수령액']   
    else: 
        groups = group_by + [pd.Grouper(freq='M')]
        df = df.groupby(groups).pipe(get_metrics)
        cols_arange = ['년도-월'] + group_by + ['단가 평균', '번역료', '수령액']   
    
    df = df.reset_index()
    df['년도-월'] = df['대금 수령일'].dt.strftime('%Y-%m')
    df.reset_index(inplace=True)
    df.drop(columns = ['대금 수령일'], inplace=True)        
 
    return df[cols_arange]

def draw_hbar(df, color_by):
    if color_by==["all"]: 
        fig = px.bar(df, y="년도-월", x="수령액", title=f"Monthly Recieved by {color_by}", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')
    else:
        fig = px.bar(df, y="년도-월", x="수령액", color=color_by, title=f"Monthly Recieved by {color_by}[0]", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')
    return fig
