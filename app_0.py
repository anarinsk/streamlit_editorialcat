#import streamlit as st
from functions_instruments import * 

# Loadin data 
# use `pd.read_pickle` to develop this app 

#df = get_data_google_sheets(st.secrets['gspread_key'], 5)
#df = pd.read_pickle("snapshot.pkl")
#today = date.today()

# Load basic df 
#df = generate_df(df)

def feed_metric(col_group, col_ref_dff, row, df, df_all=False): 
    
    col_ref = ["TD 평가액"]
    
    df = view_performance(col_group, df)
    #df = df.sort_values(col_ref, ascending=False)
    df = df.reset_index()
        
    #col_ref_dff = ["TD-1 평가액 차"]
    
    a =  df[col_group].values[row][0]
    b =  '{:,.2f}'.format(df[col_ref].values[row][0])
    c =  '{:,.2f}'.format(df[col_ref_dff].values[row][0])
    
    keys = ['label', 'value', 'delta']
    values = [a, b, c]
        
    if df_all: 
        return df
    else: 
        return dict(zip(keys, values))

def row_metrics(col_group, col_ref_dff, df): 
    
    df = view_performance(col_group, df)
    nrow = len(df.index)
    cols = st.columns(nrow)
    
    for i in range(nrow): 
        cols[i].metric(**feed_metric(col_group, col_ref_dff, i, df), delta_color="normal")    
        
    #return nrow        

def app(df):
    st.title("Anarink's Portfolio Summary!")   
    # load use df 
    cols_use = ['종목', '지역', '자산유형', '종목유형1',
                'TD 평가액', 'TD-1 평가액', 'TD-1W 평가액', 'TD-4W 평가액', 'TD-8W 평가액']
    df = df[cols_use]
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    #st.dataframe(df)
    radio_group = st.radio("Choose your reference time",('TD-1', 'TD-1W',  'TD-4W',  'TD-8W'))
    #
    st.subheader("By region")
    row_metrics(['지역'], [radio_group + " 평가액 차"], df)   
    st.subheader("By asset type")
    row_metrics(['자산유형'], [radio_group + " 평가액 차"], df) 
    st.dataframe(view_performance(['지역'], df))   
#app()