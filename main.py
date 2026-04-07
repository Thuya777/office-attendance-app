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

# ပုံ ထဲက သင့်ရဲ့ ID ကို ထည့်ပေးထားပါတယ်
SPREADSHEET_ID = "1Lnh_L7v7Vds-6WRosRIKXzNSoqANLjgAKRc5VvAIpFs" 

st.sidebar.title("⏰ ဝန်ထမ်း ရုံးတက်/ရုံးဆင်း App")
menu = st.sidebar.radio("သွားလိုသည့် အပိုင်းကို ရွေးပါ", ["ရုံးတက် ရုံးဆင်း မှတ်တမ်း", "ခွင့်တိုင်ရန်", "စီမံခန့်ခွဲမှု (Admin)"])

# ၂။ ဝန်ထမ်းစာရင်းကို Sheet1 မှ ယူခြင်း
try:
    emp_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A:A").execute()
    employee_list = [row[0] for row in emp_data.get('values', [])[1:]] 
except Exception as e:
    employee_list = []

if menu == "ရုံးတက် ရုံးဆင်း မှတ်တမ်း":
    st.header("📷 ရုံးတက်/ထွက် မှတ်တမ်းတင်ရန်")
    if employee_list:
        selected_emp = st.selectbox("ဝန်ထမ်းအမည် ရွေးချယ်ပါ", employee_list)
        status = st.radio("အခြေအနေ", ["ရုံးတက်", "ရုံးဆင်း"])
        if st.button("မှတ်တမ်းတင်မည်"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, range="Attendance!A:C",
                valueInputOption="USER_ENTERED", body={'values': [[selected_emp, status, now]]}
            ).execute()
            st.success("မှတ်တမ်းတင်ပြီးပါပြီ။")
    else:
        st.warning("Sheet1 (Column A) မှာ ဝန်ထမ်းအမည်တွေ ရှိမရှိ စစ်ပေးပါ။")

elif menu == "ခွင့်တိုင်ရန်":
    st.header("📝 ခွင့်တိုင်ကြားစာ")
    if employee_list:
        emp_name = st.selectbox("ဝန်ထမ်းအမည်", employee_list)
        leave_type = st.selectbox("ခွင့်အမျိုးအစား", ["ရှောင်တခင်ခွင့်", "ဆေးခွင့်", "လုပ်သက်ခွင့်"])
        reason = st.text_area("အကြောင်းပြချက်")
        if st.button("ခွင့်တင်မည်"):
            date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, range="Leave_Requests!A:D",
                valueInputOption="USER_ENTERED", body={'values': [[emp_name, leave_type, reason, date_now]]}
            ).execute()
            st.success("ခွင့်တင်ခြင်း အောင်မြင်ပါသည်။")

elif menu == "စီမံခန့်ခွဲမှု (Admin)":
    pw = st.sidebar.text_input("Password", type="password")
    if pw == "1234":
        st.subheader("⚙️ စည်းကမ်းချက်များ ပြင်ဆင်ရန်")
        try:
            curr = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
            curr_rules = curr.get('values', [[""]])[0][0]
        except: curr_rules = ""
        
        new_rules = st.text_area("စည်းကမ်းချက်များ", value=curr_rules, height=200)
        if st.button("Update"):
            sheet.values().update(
                spreadsheetId=SPREADSHEET_ID, range="Settings!A1",
                valueInputOption="USER_ENTERED", body={'values': [[new_rules]]}
            ).execute()
            st.success("ပြင်ဆင်ပြီးပါပြီ။")