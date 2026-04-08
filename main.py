import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime

# ၁။ Google Sheet ချိတ်ဆက်မှု
try:
    if "gcp_service_account" in st.secrets:
        info = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(info)
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
    else:
        st.error("Secrets config missing!")
        st.stop()
except Exception as e:
    st.error(f"Connection Error: {e}")
    st.stop()

# ပုံ ထဲက သင့်ရဲ့ ID အမှန်
SPREADSHEET_ID = "1Lnh_L7v7Vds-6WRosRIKXzNSoqANLjgAKRc5VvAIpFs"

st.sidebar.title("🏥 ရုံးလုပ်ငန်းသုံး App")
menu = st.sidebar.radio("သွားလိုသည့် အပိုင်းကို ရွေးပါ", ["ရုံးတက် ရုံးဆင်း မှတ်တမ်း", "ခွင့်တိုင်ကြားခြင်း", "Admin Panel"])

# ၂။ ဝန်ထမ်းစာရင်းကို Sheet1 မှ ယူခြင်း
try:
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A2:A").execute()
    values = result.get('values', [])
    employee_list = [row[0] for row in values if row]
except:
    employee_list = []

# --- ၃။ ရုံးတက် ရုံးဆင်း ---
if menu == "ရုံးတက် ရုံးဆင်း မှတ်တမ်း":
    st.header("📸 ဝန်ထမ်း ရုံးတက်/ထွက်")
    if employee_list:
        name = st.selectbox("ဝန်ထမ်းအမည် ရွေးချယ်ပါ", employee_list)
        status = st.radio("အခြေအနေ", ["ရုံးတက်", "ရုံးဆင်း"])
        if st.button("မှတ်တမ်းတင်မည်"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, range="Attendance!A:C",
                valueInputOption="USER_ENTERED", body={'values': [[name, status, now]]}
            ).execute()
            st.success(f"{name} အတွက် {status} မှတ်တမ်းတင်ပြီးပါပြီ။")
    else:
        st.warning("ဝန်ထမ်းစာရင်း မရှိသေးပါ။ Admin ထဲမှာ အရင်ထည့်ပါ။")

# --- ၄။ ခွင့်တိုင်ကြားခြင်း ---
elif menu == "ခွင့်တိုင်ကြားခြင်း":
    st.header("📝 ခွင့်တိုင်ကြားရန်")
    if employee_list:
        name = st.selectbox("အမည်", employee_list)
        l_type = st.selectbox("ခွင့်အမျိုးအစား", ["ရှောင်တခင်ခွင့်", "ဆေးခွင့်", "လုပ်သက်ခွင့်"])
        reason = st.text_area("အကြောင်းပြချက်")
        if st.button("ခွင့်တင်မည်"):
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, range="Leave_Requests!A:D",
                valueInputOption="USER_ENTERED", body={'values': [[name, l_type, reason, date]]}
            ).execute()
            st.success("ခွင့်တင်ပြီးပါပြီ။")

# --- ၅။ Admin Panel ---
elif menu == "Admin Panel":
    st.header("🔐 စီမံခန့်ခွဲသူ")
    pw = st.text_input("Admin Password ရိုက်ပါ", type="password")
    
    if pw == "1234":
        st.success("Admin Login အောင်မြင်ပါသည်။")
        admin_task = st.radio("ဘာလုပ်ဆောင်လိုပါသလဲ", ["ဝန်ထမ်းအသစ်ထည့်ရန်", "စည်းကမ်းချက်ပြင်ရန်"])
        
        if admin_task == "ဝန်ထမ်းအသစ်ထည့်ရန်":
            st.subheader("👤 ဝန်ထမ်းအသစ်ထည့်ခြင်း")
            new_name = st.text_input("ဝန်ထမ်းအမည်သစ်")
            if st.button("သိမ်းမည်"):
                if new_name:
                    sheet.values().append(
                        spreadsheetId=SPREADSHEET_ID, range="Sheet1!A:A",
                        valueInputOption="USER_ENTERED", body={'values': [[new_name]]}
                    ).execute()
                    st.success(f"{new_name} ကို ထည့်ပြီးပါပြီ။")
        
        elif admin_task == "စည်းကမ်းချက်ပြင်ရန်":
            st.subheader("📜 စည်းကမ်းချက်များ")
            try:
                curr = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
                curr_rules = curr.get('values', [[""]])[0][0]
            except: curr_rules = ""
            
            new_rules = st.text_area("စည်းကမ်းချက်ပြင်ဆင်ရန်", value=curr_rules, height=200)
            if st.button("Update Rules"):
                sheet.values().update(
                    spreadsheetId=SPREADSHEET_ID, range="Settings!A1",
                    valueInputOption="USER_ENTERED", body={'values': [[new_rules]]}
                ).execute()
                st.success("စည်းကမ်းချက်များ ပြင်ဆင်ပြီးပါပြီ။")