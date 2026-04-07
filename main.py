import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# ၁။ Google Sheet ချိတ်ဆက်မှု
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
else:
    st.error("Secrets configuration missing!")
    st.stop()

SPREADSHEET_ID = "1Lnh_L7v7VDs-6WRosR1KXzNSoqANLjgAKRc5VvAIpFs"

# Sidebar Menu
st.sidebar.title("⏰ ဝန်ထမ်း ရုံးတက်/ရုံးဆင်း App")
menu = st.sidebar.radio("သွားလိုသည့် အပိုင်းကို ရွေးပါ", ["ရုံးတက် ရုံးဆင်း မှတ်တမ်း", "စီမံခန့်ခွဲမှု (Admin)"])

if menu == "ရုံးတက် ရုံးဆင်း မှတ်တမ်း":
    st.header("📷 ဝန်ထမ်းရုံးတက်/ထွက် မှတ်တမ်း")
    
    try:
        # ဝန်ထမ်းစာရင်းကို Employees sheet မှ ယူခြင်း
        emp_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Employees!A:B").execute()
        values = emp_data.get('values', [])
        if not values:
            st.warning("ဝန်ထမ်းစာရင်း မရှိသေးပါ။")
        else:
            employee_list = [row[0] for row in values[1:]] # First row is header
            selected_emp = st.selectbox("ဝန်ထမ်းအမည် ရွေးချယ်ပါ", employee_list)
            status = st.radio("အခြေအနေ", ["ရုံးတက်", "ရုံးဆင်း"])
            
            if st.button("မှတ်တမ်းတင်မည်"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = [[selected_emp, status, now]]
                sheet.values().append(
                    spreadsheetId=SPREADSHEET_ID,
                    range="Attendance!A:C",
                    valueInputOption="USER_ENTERED",
                    body={'values': new_row}
                ).execute()
                st.success(f"{selected_emp} အတွက် {status} မှတ်တမ်း တင်ပြီးပါပြီ။")
    except Exception as e:
        st.error(f"Error: {e}")

elif menu == "စီမံခန့်ခွဲမှု (Admin)":
    password = st.sidebar.text_input("Admin Password", type="password")
    if password == "1234":  # စကားဝှက်ကို ဒီမှာ ပြောင်းနိုင်ပါတယ်
        tab1, tab2 = st.tabs(["ဝန်ထမ်းအသစ်ထည့်ရန်", "စည်းကမ်းချက်များ"])
        
        with tab1:
            new_name = st.text_input("ဝန်ထမ်းအမည်")
            if st.button("ဝန်ထမ်းအသစ် သိမ်းမည်"):
                if new_name:
                    sheet.values().append(
                        spreadsheetId=SPREADSHEET_ID,
                        range="Employees!A:A",
                        valueInputOption="USER_ENTERED",
                        body={'values': [[new_name]]}
                    ).execute()
                    st.success(f"{new_name} ကို ထည့်သွင်းပြီးပါပြီ။")
        
        with tab2:
            st.subheader("⚙️ စည်းကမ်းချက်များ ပြင်ဆင်ရန်")
            try:
                curr_sett = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
                curr_rules = curr_sett.get('values', [[""]])[0][0]
            except:
                curr_rules = ""
            
            new_rules = st.text_area("စည်းကမ်းချက်များ", value=curr_rules, height=200)
            if st.button("Update Rules"):
                sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range="Settings!A1",
                    valueInputOption="USER_ENTERED",
                    body={'values': [[new_rules]]}
                ).execute()
                st.success("စည်းကမ်းချက်များ ပြင်ဆင်ပြီးပါပြီ။")
    elif password != "":
        st.sidebar.error("Password မှားယွင်းနေပါသည်။")