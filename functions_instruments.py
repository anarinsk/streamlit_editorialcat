import streamlit as st
import pandas as pd
import numpy as np 
import gspread
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
import plotly.express as px

# Password without SSO 
def check_password(secrets):
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == secrets["m_pw"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Functions in Loading data from Google Spreadsheet

def gss_to_df(gc, tab_index):
# Prompts for all spreadsheet values
    values = gc.get_worksheet(tab_index).get_all_values()
    
    # Turns the return into a dataframe
    df = pd.DataFrame(values)
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    return df

#@st.cache(ttl=60*1)
def get_data_google_sheets(tab_index, secrets):
    
    # Link to authenticate 
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
        ]
   
    info = { "type" : "service_account",
             "auth_uri" : "https://accounts.google.com/o/oauth2/auth",
             "token_uri" : "https://oauth2.googleapis.com/token",
             "auth_provider_x509_cert_url" : "https://www.googleapis.com/oauth2/v1/certs",
             "project_id" : secrets["project_id"],
             "private_key_id" : secrets["private_key_id"],
             "private_key" : secrets["private_key"],
             "client_email" :secrets["client_email"],
             "client_id" : secrets["client_id"],
             "client_x509_cert_uri" : secrets["client_x509_cert_uri"],
             "spread_key": secrets["spread_key"]
    }
    
    credentials = Credentials.from_service_account_info(
        info,
        scopes=scopes
    )
    
    # Request authorization and open the selected spreadsheet
    gc = gspread.authorize(credentials).open_by_key(info['spread_key'])
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
    cols_numeric = ['단가', '번역료', '수령액', 'RT', 'RTM', 'CPE', 'CPER', '환율']
    cols_date = ['마감일', '대금 수령일']
    cols_use = ['발주처', '방영 채널', '작품명 / 시즌', 'Ep', 'RT', 'RTM', 'CPE', 'CPER', '환율', 
                '영상 종류', '작업 종류', '마감일',
                '대금 수령일', '단가', '번역료', '수령액', '비고', 'new_unit_price']
    # Cols to be handled 
    tdf = df.copy()
    tdf = tdf.drop(columns=cols_remove)
    tdf[cols_numeric] = tdf[cols_numeric].apply(turn_str_num, axis=1)
    tdf[cols_date] = tdf[cols_date].apply(pd.to_datetime, axis=1)
    tdf = tdf.assign(
        new_unit_price = np.where(tdf['단가']!=tdf['단가'], tdf['환율']*(tdf['RTM'] + np.nan_to_num(tdf['CPE']*tdf['CPER'])/tdf['RT']), tdf['단가'])
        )
    #
    return tdf[cols_use]

def filter_date(start, end, df, by='`대금 수령일`'):
    return df.query(f"{by} >= @start & {by} <= @end") 

def get_metrics(grp_obj):
    mean_danga = grp_obj['new_unit_price'].mean()
    sum_bunyuk = grp_obj['번역료'].sum()
    sum_suryung = grp_obj['수령액'].sum()
    result = pd.DataFrame({
        "단가 평균": mean_danga, 
        "번역료": sum_bunyuk, 
        "수령액": sum_suryung
        })
    return result

def generate_groupby_df_period(df, group_by, period_by):
    group_by_2 = [pd.Grouper(freq=period_by)] + group_by 
    df = df.groupby(group_by_2).pipe(get_metrics)
    df = df.reset_index()
    df = df.sort_values(by='time', ascending=False)
    if period_by == "M":
        df.time = df.time.dt.strftime('%Y-%m')
        df.set_index(['time']+group_by, inplace=True)
        cols_arange = ['단가 평균', '번역료', '수령액']           
    elif period_by == "Y": 
        df.time = df.time.dt.strftime('%Y')
        df = df.set_index(['time']+group_by)
        cols_arange = ['단가 평균', '번역료', '수령액']   
    #
    return  df[cols_arange]

def generate_groupby_df_all(df, group_by):
    if group_by == []: 
        df['fake'] = 1
        df = df.groupby(['fake']).pipe(get_metrics) 
        df = df.reset_index()
        #df = df.pipe(get_metrics)
    else: 
        df = df.groupby(group_by).pipe(get_metrics) 
    cols_arange = ['단가 평균', '번역료', '수령액']   
    return  df[cols_arange].sort_values(by=cols_arange[2], ascending=False)

def summarise_by_v2(df, time_by='대금 수령일', period_by='M', group_by=[]): 
#    
    df = df.rename(columns={'대금 수령일':'time'})
    df.index = pd.to_datetime(df['time'],format='%m/%d/%y %I:%M%p')    
    
    if period_by!="All": 
        groupby_cols = group_by
        return generate_groupby_df_period(df, groupby_cols, period_by)
    else: 
        groupby_cols = group_by
        return generate_groupby_df_all(df, groupby_cols)

def extract_metrics(df):

    ydf = summarise_by_v2(df, time_by='대금 수령일', period_by='Y', group_by=[]).reset_index()
    mdf = summarise_by_v2(df, time_by='대금 수령일', period_by='M', group_by=[]).reset_index()
    mdf_best = mdf.sort_values(by='수령액', ascending=False).head(5)
    
    year_amt = ydf['수령액'].to_list()
    total_earning = sum(year_amt)
    latest_year = year_amt[0]
    last_year = year_amt[1]
    diff_year_amt = latest_year - last_year
    diff_year_pct = diff_year_amt/last_year

    month_amt = mdf['수령액'].to_list()
    latest_month_amt = month_amt[0]
    month_before_amt = month_amt[1]
    diff_month_pct = (latest_month_amt - month_before_amt)/month_before_amt
    best_month = mdf_best['time'].values[0]
    best_month_amt = mdf_best['수령액'].values[0]
    
    return total_earning, diff_year_amt, diff_year_pct, latest_month_amt, month_before_amt, diff_month_pct, best_month, best_month_amt

def format_all_yaxis(fig, font_size, tick_font_size=11.2): 
    return fig.update_layout(font=dict(size=font_size), yaxis=dict(showticklabels=True, title_text='', tickangle=18, tickfont_size=tick_font_size, ticksuffix=' ', categoryorder='total ascending')) 

def gen_chart(df, period_by, group_by):
    
    df = df.reset_index()    
    font_size = 15
    
    if  (group_by == []) & (period_by == 'All'):
        df = df.sort_values(by='수령액', ascending=True)
        x_value = df["수령액"].values[0]
        fig = px.bar(y=[0], x=[x_value], title=f"Total earned", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')
        return fig.update_layout(font=dict(size=font_size), yaxis=dict(visible=False), xaxis=dict(title='수령액')).update_traces(width=0.5)
    #    
    elif (len(group_by) == 1) & (period_by == 'All'):
        df = df.sort_values(by='수령액', ascending=True)
        y_var = group_by[0]
        fig = px.bar(df, y=y_var, x="수령액", title=f"Total earned by {y_var}", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')
        return format_all_yaxis(fig, font_size)
    #
    elif (len(group_by) > 1) & (period_by == 'All'):
        y_var = group_by[0]
        color_var = group_by[1]
        fig = px.bar(df, y=y_var, x="수령액", color=color_var, title=f"Total earned by {y_var} and {color_var}", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')   
        return format_all_yaxis(fig, font_size)
    #    
    elif (group_by == []) & (period_by != 'All'):
        df = df.sort_values(by='time', ascending=True)
        fig = px.bar(df, y='time', x="수령액", title=f"Timely earned", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')
        return fig.update_layout(font=dict(size=font_size)) 
    #
    else:
        df = df.sort_values(by='time', ascending=True) 
        color_var = group_by[0]
        fig = px.bar(df, y='time', x="수령액", color=color_var, title=f"Timely earned by {color_var}", color_discrete_sequence=px.colors.qualitative.Antique, orientation='h')
        return fig.update_layout(font=dict(size=font_size)) 