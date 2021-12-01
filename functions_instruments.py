import streamlit as st
import pandas as pd
import numpy as np 
import streamlit_authenticator as stauth

import gspread
from google.oauth2.service_account import Credentials

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
#    
def prepare_df(cols: list, df) -> pd.DataFrame:
    return df[cols]
#    
def view_port(df: pd.DataFrame, include_zero:bool=False, detail:bool=False, include_won:bool=False):
    
    col_drop_1 = ['매수액', '매도액', '매수-매도', 'TD-1 평가액', 'TD-1W 평가액', 'TD-4W 평가액', 'TD-8W 평가액']    
    
    df = df.reset_index(drop=True) 
    
    if (detail==False): 
        df.drop(col_drop_1, axis=1, inplace=True)
    
    if (include_zero==False): 
        df = df.query(
            "`현재 보유량` > 0"
        )
        df = df.copy().drop(['Consoliated Profit'], axis=1)

    if(include_won==False): 
        df = df.query(
            "`종목` != '원화'"
        )
    
    df = df.sort_values(by = ['Share', 'TD Profit Rate'], ascending=False)
    
    return df.set_index(['종목'])
#
def view_stats(cols:list, df): 

    df = df.reset_index()
    list_1 = cols + ['TD 평가액', '거래액']
    df = df[list_1].groupby(cols).sum()
    df1 = df.assign(**{
            '이익': df['TD 평가액'] - df['거래액'], 
            '이익률': (df['TD 평가액'] - df['거래액']) / df['거래액'],  
            '자산 비중': df['TD 평가액']/sum(df['TD 평가액'])
               })
    df1 = df1.sort_values(['자산 비중'], ascending=False)
    df1_style = df1.style.format({
        'TD 평가액': '{:,.0f}',
        '거래액': '{:,.0f}',
        '이익': '{:,.0f}',
        '이익률': '{:.2%}', 
        '자산 비중': '{:.2%}'
    })
    
    return df1_style
#
def view_price(df: pd.DataFrame, include_zero:bool=False, detail:bool=False, include_won:bool=False):
    
    col_drop_1 = ['TD-1 주가', 'TD-1W 주가', 'TD-4W 평균', 'TD-8W 평균']    
    
    df = df.reset_index(drop=True) 
    
    if (detail==False): 
        df.drop(col_drop_1, axis=1, inplace=True)
    
    if (include_zero==False): 
        df = df.query(
            "`현재 보유량` > 0"
        )
        df = df.copy().drop(['Consoliated Profit'], axis=1)

    if(include_won==False): 
        df = df.query(
            "`종목` != '원화'"
        )
    
    df = df.sort_values(by = ['지역', '종목'], ascending=True)
    df = df.set_index(['종목'])
    
    arange = ['TD 주가', '98.5%', '97%', '95%', '93%', '90%', '85%', '52W High', '52W Low', '종목명', 'TD 평가액', 'TD Profit Rate']
    
    df = df[arange]
    df_style = df.style.format({
        'TD 평가액': '{:,.0f}',
        'TD Profit Rate': '{:.2%}'
    })
    
    return df
#
def view_performance(cols, df):
    df1 = df.groupby(cols).sum()
    df1 = df1.assign(**{
        "TD-1 평가액 차":  df1['TD 평가액'] -  df1['TD-1 평가액'], 
        "TD-1W 평가액 차": df1['TD 평가액'] - df1['TD-1W 평가액'],
        "TD-4W 평가액 차": df1['TD 평가액'] - df1['TD-4W 평가액'],
        "TD-8W 평가액 차": df1['TD 평가액'] - df1['TD-8W 평가액']
        })
    df1 = df1.query("`TD 평가액` > 0")
    df1 = df1.sort_values(['TD-1 평가액 차'], ascending=True)
    df1 = df1.query("{0} not in ['현금', '원화', 'cash']".format(cols[0]))
    df1 = df1.sort_values(by=['TD 평가액'], ascending=False)
    format_num = ["{:,.2f}" for k in range(len(df1.columns))]
    style_1 = dict(zip(df1.columns, format_num))
    
    return df1