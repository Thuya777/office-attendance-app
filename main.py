import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from PIL import Image as Image

# ၁။ Google Sheet ချိတ်ဆက်မှု
if "gcp_service_account" in st.secrets:
    info = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(info)
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

SPREADSHEET_ID = "1Lnh_L7v7vDs-6WRosRlKXzNSoqANljgAKRc5VvAIpFs" # သင့် ID ကို ပြန်စစ်ပါ

# Sidebar Menu
st.sidebar.title("⏱️ ဝန်ထမ်း ရုံးတက်/ရုံးဆင်း App")
menu = st.sidebar.radio("သွားလိုသည့် အပိုင်းကို ရွေးပါ", ["ရုံးတက် ရုံးဆင်း မှတ်တမ်း", "ခွင့်တိုင်ကြားခြင်း", "Admin Panel (စီမံခန့်ခွဲသူ)"])

# --- ၁။ ရှိမရှိ စစ်ဆေးခြင်း အပိုင်း ---
if menu == "ရုံးတက် ရုံးဆင်း မှတ်တမ်း":
    st.header("📸 ဝန်ထမ်းရုံးတက်/ထွက် မှတ်တမ်း")
    # Google Sheet ထဲမှ ဝန်ထမ်းစာရင်းကို ဖတ်ယူခြင်း
    try:
        employee_data = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Sheet1!A1:B100').execute()
        employees = employee_data.get('values', [])
        
        if employees:
            # နာမည်များကို List အနေဖြင့် ထုတ်ယူခြင်း
            employee_names = [emp[0] for emp in employees]
            selected_employee = st.selectbox("ဝန်ထမ်းအမည် ရွေးချယ်ပါ", employee_names)
            
            # ရွေးချယ်ထားသော ဝန်ထမ်း၏ Photo ID ကို ရှာဖွေခြင်း
            photo_id = ""
            for emp in employees:
                if emp[0] == selected_employee:
                    photo_id = emp[1]
                    break
            
            if photo_id:
                # ဓာတ်ပုံပြသခြင်း
                image_url = f"https://drive.google.com/uc?id={photo_id}"
                st.image(image_url, caption=f"{selected_employee} ၏ ဓာတ်ပုံ", width=200)
            
            if st.button("Check-in / Check-out"):
                st.success(f"{selected_employee} မှတ်တမ်းတင်ပြီးပါပြီ။")
        else:
            st.warning("ဝန်ထမ်းစာရင်း မရှိသေးပါ။ Admin Panel တွင် အရင်ထည့်သွင်းပါ။")
            
    except Exception as e:
        st.error(f"အချက်အလက်ဖတ်ယူရာတွင် အမှားရှိနေပါသည် - {e}")
# --- ၂။ ခွင့်တိုင်ကြားခြင်း အပိုင်း ---
elif menu == "ခွင့်တိုင်ကြားခြင်း":
    st.header("📝 ခွင့်တိုင်ကြားရန်")
    
    # ၁။ Admin Panel က စည်းကမ်းချက် (5:00) ကို အရင်ပြခြင်း
    office_rules = "5:00" 
    st.info(f"📌 ခွင့်ဆိုင်ရာ စည်းကမ်းချက်များ: {office_rules}")
    
    # ၂။ အတည်ပြုချက်ယူရန် Checkbox
    agreed = st.checkbox("စည်းကမ်းချက်များကို ဖတ်ရှုနားလည်ပြီးပါပြီ")
    
    # ၃။ အမှန်ခြစ်မှသာ အောက်က Form ပေါ်လာမည်
    if agreed:
        st.success("အတည်ပြုပြီးပါပြီ။ အောက်တွင် အချက်အလက်ဖြည့်ပါ။")
        name = st.text_input("အမည်")
        l_type = st.selectbox("ခွင့်အမျိုးအစား", ["ရှောင်တခင်ခွင့်", "ဆေးခွင့်", "လုပ်သက်ခွင့်"])
        reason = st.text_area("အကြောင်းပြချက်")
        
        if st.button("ခွင့်တင်မည်"):
            date = datetime.now().strftime("%Y-%m-%d")
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID, 
                range="Leave_Requests!A:D",
                valueInputOption="USER_ENTERED", 
                body={'values': [[name, l_type, reason, date]]}
            ).execute()
            st.success("ခွင့်တိုင်ကြားမှု အောင်မြင်ပါသည်။")

# --- ၃။ Admin Panel (လုံခြုံရေး Password ပါဝင်သည်) ---
elif menu == "Admin Panel (စီမံခန့်ခွဲသူ)":
    st.header("🔐 Admin Panel")
    password = st.text_input("Admin Password ရိုက်ထည့်ပါ", type="password")

    # Password သတ်မှတ်ချက်
    correct_password = "741985"

    if password == correct_password:
        tab1, tab2 = st.tabs(["ဝန်ထမ်းအသစ်/ဓာတ်ပုံပြင်ရန်", "စည်းကမ်းချက်ပြင်ရန်"])
        
        with tab1:
            st.subheader("👤 ဝန်ထမ်းစီမံခြင်း")
            new_name = st.text_input("ဝန်ထမ်းအမည်သစ်")
            new_photo_id = st.text_input("Google Drive Photo ID (အရှည်ကြီး)")
            
            if st.button("ဝန်ထမ်းအသစ် သိမ်းမည်"):
                if new_name and new_photo_id:
                    sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Employees!A:B", 
                                        valueInputOption="USER_ENTERED", body={'values': [[new_name, new_photo_id]]}).execute()
                    st.success(f"'{new_name}' ကို ထည့်သွင်းပြီးပါပြီ။")
                else:
                    st.error("အချက်အလက် အကုန်ဖြည့်ပါ။")

        with tab2:
            st.subheader("⚙️ စည်းကမ်းချက်များ ပြင်ဆင်ရန်")
            try:
                current_sett = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Settings!A1").execute()
                current_rules = current_sett.get('values', [[""]])[0][0]
            except:
                current_rules = ""
                
            new_rules = st.text_area("ပြင်ဆင်ရန်", value=current_rules, height=200)
            if st.button("Update Rules"):
                sheet.values().update(spreadsheetId=SPREADSHEET_ID, range="Settings!A1", 
                                    valueInputOption="USER_ENTERED", body={'values': [[new_rules]]}).execute()
                st.success("စည်းကမ်းချက်များ ပြင်ဆင်ပြီးပါပြီ။")
    
    elif password != "":
        st.error("Password မှားယွင်းနေပါသည်။")