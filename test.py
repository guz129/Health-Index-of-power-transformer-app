import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.patheffects as path_effects

#จาก UI ที่ให้มาช่วยปรับปรุงเพื่อให้รันข้อมูลในไฟล์นี้ให้ UI สามารถเเสดงผลได้หน่อยได้ไหม
st.set_page_config(page_title ="⚡ Health Index of Power Transformer", layout="wide")
#st.title("⚡ Health Index of Power Transformer")
st.markdown("<h1 style='text-align: center;'>⚡ Health Index of Power Transformer</h1>", unsafe_allow_html=True)

# Upload section
uploaded_file = st.file_uploader("กรุณาอัพโหลดไฟล์ excel สกุล .xlsx", type=["xlsx"])

def convert_thai_date(date_str):
    try:
        if pd.isna(date_str):
            return pd.NaT
        date_str = str(date_str).strip()
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year_thai = map(int, parts)
            year = year_thai - 543
            return pd.Timestamp(f"{year:04d}-{month:02d}-{day:02d}")
        else:
            return pd.to_datetime(date_str, errors='coerce')
    except:
        return pd.NaT

if uploaded_file:
    df = pd.read_excel(uploaded_file)



    df['OIL DATE'] = df['OIL DATE'].apply(
    lambda x: f"{x.day:02d}/{x.month:02d}/{x.year:04d}" if pd.notnull(x) else "ไม่พบวันที่"
)  
    #df['OIL DATE'] = pd.to_datetime(df['OIL DATE'], errors='coerce')

    if df['OIL DATE'].dtype == object  or pd.api.types.is_string_dtype(df['OIL DATE']):
       df['OIL DATE'] = df['OIL DATE'].apply(convert_thai_date)

    # Select Transformer ID to view
    trans_ids = df['Trans ID'].unique()
    selected_id = st.selectbox("Select Transformer ID", trans_ids)

    available_dates = df[df['Trans ID'] == selected_id]['OIL DATE'].dropna().sort_values().unique()
    available_dates_str = [d.strftime("%d/%m/%Y") for d in available_dates]
    selected_date = st.selectbox("Select OIL DATE", available_dates_str)
    # แปลงกลับเป็น datetime สำหรับกรองข้อมูล
    selected_datefix = pd.to_datetime(selected_date, format="%d/%m/%Y")
    filtered_df = df[(df['Trans ID'] == selected_id) & (df['OIL DATE'] == selected_datefix)]
    if not filtered_df.empty:
       latest = filtered_df.iloc[-1]

      #--oil_dates = df['OIL DATE'].unique()
      #--selected_date = st.selectbox("Select OIL DATE", oil_dates)
      #--oil_df = df[df['OIL DATE'] == selected_date].sort_values("OIL DATE")
      #--latest = oil_df.iloc[-1]
      
                                                                       
    # ------------- Layout -------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.text_input("Transformer ID", value=latest['Trans ID'], disabled=True)
    with col2:
        st.text_input("Location", value="Thanon Tok", disabled=True)
    with col3:
        st.text_input("Age (Years)", value=int(latest['Age']), disabled=True)
    with col4:
        st.text_input("Max Load", value=float(latest['Max Load']), disabled=True)

    # Section: Transformer Info
    with st.container():
        st.markdown("### 🔶 Transformer Info")
        st.write(f"**ID:** {latest['Trans ID']}")
        st.write(f"**Location:** Thanon Tok")
        st.write(f"**Oil Date:** {latest['OIL DATE'].strftime('%d/%m/%Y') if pd.notnull(latest['OIL DATE']) else 'N/A'}")

    df['OIL DATE'] = pd.to_datetime(df['OIL DATE'])
    df_grouped = df.drop_duplicates(subset=['CH4','C2H2','C2H4', 'OIL DATE']).sort_values('OIL DATE')
    
    x_labels = df_grouped['OIL DATE'].dt.strftime('%d/%m/%Y') 
    x_pos = list(range(len(df_grouped)) )

    grouped = (
    df.sort_values('OIL DATE')
    .drop_duplicates(subset=['OIL DATE'])
)
    
    st.markdown("### 📈 DGA Trend")
       # สร้างกราฟ Plotly
    fig = go.Figure() 
    fig.add_trace(go.Scatter(
    x=x_pos,
    y=df_grouped['CH4'],
    mode='lines+markers',
    name='CH4',
    line=dict(color='red'),
    marker=dict(size=8),
    hovertemplate='วันที่: %{x|%d/%m/%Y}<br>CH4: %{y:.2f} ppm<extra></extra>'
))

    fig.add_trace(go.Scatter(
    x=x_pos,
    y=df_grouped['C2H2'],
    mode='lines+markers',
    name='C2H2',
    line=dict(color='purple'),
    marker=dict(size=8),
    hovertemplate='วันที่: %{x|%d/%m/%Y}<br>C2H2: %{y:.2f} ppm<extra></extra>'
))

    fig.add_trace(go.Scatter(
    x=x_pos,
    y=df_grouped['C2H4'],
    mode='lines+markers',
    name='C2H4',
    line=dict(color='green'),
    marker=dict(size=8),
    hovertemplate='วันที่: %{x|%d/%m/%Y}<br>C2H4: %{y:.2f} ppm<extra></extra>'
))

# เส้นแนว limit
    fig.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="MAX 50 ppm", annotation_position="top right")
    fig.add_hline(y=120, line_dash="dash", line_color="red", annotation_text="MAX 120 ppm", annotation_position="top right")
    fig.add_hline(y=35, line_dash="dash", line_color="purple", annotation_text="MAX 35 ppm", annotation_position="top right")

    fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=x_pos,
        ticktext=x_labels,
        title='OIL DATE',
        showgrid=True,
        gridcolor='lightgray'
    ),
    yaxis_title="Concentration (ppm)",
    hovermode="x unified",
    legend=dict(title="Gas Type"),
    margin=dict(l=20, r=20, t=50, b=50)
)   
    # เปิดเส้นบรรทัดแนวนอนและแนวตั้ง
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
    """
    <div style='text-align:left; margin-top: -10px;'>
        <p><b>🚫 ZONE</b></p>
    </div>
    """, 
    unsafe_allow_html=True
)
    recommendations = []
    if latest['CH4'] > 120:
        recommendations.append("Overheating ระดับต่ำ(T1)")
    if latest['C2H2'] > 35:
        recommendations.append("Arcing (D2)")
    if latest['C2H4'] > 50:
       recommendations.append("Overheating ระดับสูง (T2–T3)")
    # แสดงผลลัพธ์
    if recommendations:
       for rec in recommendations:
           st.write("-", rec)
    else:
        st.write("- ไม่พบอาการผิดปกติ")
    def normalize(val, min_val, max_val, reverse=False):
        norm = (val - min_val) / (max_val - min_val)
        norm = max(0, min(norm, 1))
        return 1 - norm if reverse else norm
    latest['Total_HC'] = latest[['H2','CO','C2H2','C2H4','C2H6','CH4']].sum()
    latest['C2H4_ratio'] = latest['C2H4'] / latest['C2H6']
    latest['C2H2_ratio'] = latest['C2H2'] / latest['C2H4']
    latest['CH4_ratio']  = latest['CH4'] / latest['H2']
    def diagnose_iec(row):
       r1 = row['CH4_ratio']
       r2 = row['C2H2_ratio']
       r3 = row['C2H4_ratio']
 # กำหนดเงื่อนไขจาก IEC Table
       if r1 < 0.1 and r2 > 0 and r3 < 0.2:
          return 0.75,{}     # Partial Discharge (PD)
       elif 0.1 <= r1 <= 0.5 and r2 > 1 and r3 > 1:
          return 0.6,{}     # Discharge of low energy (Sparking)
       elif 0.1 <= r1 <= 1 and 0.6 <= r2 <= 2.5 and r3 > 2:
          return 0.3,{}     # Discharge of high energy (Arcing)
       elif r1 > 1 and r2 > 0 and r3 < 1:
          return 0.6,{}     # Thermal fault <300°C
       elif r1 > 1 and r2 < 0.1 and 1 <= r3 <= 4:
          return 0.4,{}     # Thermal fault 300–700°C
       elif r1 > 1 and r2 < 0.2 and r3 > 4:
          return 0.2,{}     # Thermal fault >700°C
       else:
          
           weights = {
            'Age_Score': 1/6,
        'Load_Score': 1/6,
        'Oil_Score': 1/6,
        'tdcg_score': 1/6,
         'iec': 0,         # ตัดคะแนนนี้ออก
         'ieee_score': 1/6,
        'duval_score': 1/6
        }
       return 0,weights
    def duval_1(row):
        total = row['CH4'] + row['C2H2'] + row['C2H4']
        ch4 = row['CH4'] / total * 100
        c2h2 = row['C2H2'] / total * 100
        c2h4 = row['C2H4'] / total * 100
        #ch4 = row['%CH4']
        #c2h2 = row['%C2H2']
        #c2h4 = row['%C2H4']
        if 0 <= ch4 <= 87 and c2h2 >= 45 and c2h4 >= 10:
           return 0.6,{}#"D1 (Sparking)"
        elif 0 <= ch4 <= 65 and 13 <= c2h2 <= 77 and c2h4 >= 23 :
           return 0.3,{}  #"D2 (Arcing)"
        elif  ch4 <= 47  and 0 <= c2h2 <= 15 and c2h4 >= 50:
           return 0.2,{} #"T3 ;T>700°C"
        elif ch4 > 77 and c2h2 < 4 and c2h4 <= 20:
           return 0.6,{}  #"T1 ;T<300°C"
        elif 27 <= ch4 <= 50 and  c2h2 < 4  and 20 <= c2h4 <= 50:
           return 0.4 ,{} #"T2 ;T=300-700°C"
        elif ch4 >= 98 and 45 <= c2h2 <= 50 and 0 <= c2h4 <= 2:
           return 0.75,{} #"PD"
        elif ch4 <= 97  and 4 <= c2h2 <= 100 and c2h4 >= 2:
            return 0.45,{} #"DT"
        else:
            st.error("ไม่สามารถคำนวณ Health Score ของหม้อแปลงเครื่องนี้ได้ชัดเจนเพราะ ppm ของสาร 'CH4','C2H2','C2H4' บางตัวอยู่นอกเงื้อนไขตามทฤษฎีที่จะเป็นไปได้") 
            weights = {
                'Age_Score': 1/6,
                'Load_Score': 1/6,
                'Oil_Score': 1/6,
                'tdcg_score': 1/6,
                'iec_score': 1/6,
                'ieee_score': 1/6,
                'duval_score': 0
            }
           
            return 0, weights

    def ieee_key(row):
        gases = {
        'H2': row.get('H2', 0),
        'CH4': row.get('CH4', 0),
        'C2H2': row.get('C2H2', 0),
        'C2H4': row.get('C2H4', 0),
        'C2H6': row.get('C2H6', 0),
        'CO': row.get('CO', 0),
    }

    # ตรวจว่าไม่มีค่าว่าง
        if any(g is None for g in gases.values()):
           st.error("ไม่สามารถคำนวณ Health Score ของหม้อแปลงเครื่องนี้ได้ชัดเจนเพราะไม่พบคอลัมน์ H2, CH4, C2H2, C2H4, C2H6, หรือ CO")
           weights = {
            'Age_Score': 1/6,
            'Load_Score': 1/6,
            'Oil_Score': 1/6,
            'tdcg_score': 1/6,
            'iec_score': 1/6,
            'ieee_score': 0,
            'duval_score': 1/6
        }
           return 0, weights

    # หาค่ามากที่สุด
        key_gas = max(gases, key=gases.get)
 
        score_map = {
        'H2': 0.7,       # Partial Discharge
        'CH4': 0.95,     # Overheating <150°C
        'C2H6': 0.9,     # Overheating 150–300°C
        'C2H4': 0.8,     # Overheating 300–700°C
        'C2H2': 0.45,    # Arcing >700°C
        'CO': 0.7        # Paper insulation aging
    }

        score = score_map.get(key_gas, 0)
        return score, {}

    weights = {   # ✅ กำหนดก่อนเรียกใช้ update
        'Age_Score': 1/7,
        'Load_Score': 1/7,
        'Oil_Score': 1/7,
        'tdcg_score': 1/7,
        'iec_score': 1/7,
        'ieee_score': 1/7,
        'duval_score': 1/7
    }

    duval_score, duval_adjust = duval_1(latest)
    weights.update(duval_adjust)

    ieee_score, ieee_adjust = ieee_key(latest)
    weights.update(ieee_adjust)

    iec_score, iec_adjust = diagnose_iec(latest)
    weights.update(iec_adjust)

    tdcg_score = float(normalize(latest['Total_HC'],0,4630, reverse=True))
    oil_score = normalize(latest['Oil Quality'],0,100,reverse=True) #moisture ppm
    age_score = normalize(latest['Age'], 0, 40, reverse=True)
    load_score = normalize(latest['Max Load'], 0.5, 1.2, reverse=True)
    
    health_index = 100 * ( weights['Age_Score'] * age_score + weights['Load_Score'] * oil_score + weights['Oil_Score'] * load_score + weights['tdcg_score'] * tdcg_score + weights['iec_score'] * iec_score + weights['duval_score'] * duval_score + weights['ieee_score'] * ieee_score)
    if health_index >= 80:
        status = "Good"
        risk = "Low Risk"
    elif health_index >= 60:
        status = "Fair"
        risk = "Medium Risk"
    elif health_index >= 40:
        status = "Attention"
        risk = "High Risk"
    else:
        status = "Critical"
        risk = "Critical Risk"

    st.markdown(
    """
    <h3 style='margin-top: 23px;'>🟢 Health Score</h3>
    """,
    unsafe_allow_html=True
)
    st.metric(label="Health Index", value=f"{health_index:.0f}", delta=health_index - 75)
    st.write(f"**Status:** {status}")
    st.write(f"**Risk:** {risk}")

    def detect_fault(row):
       if row['Total_HC'] > 720:
        return 'Alert'
       elif row['Total_HC'] > 1920:
        return 'Check'
       elif row['Total_HC'] > 4630:
        return 'STOP!'
       else:
        return 'Safe'
    tdcg_detect =  detect_fault(latest)
    st.write(f"**TDCG test:** {tdcg_detect}")

    def diagnose_iec(row):
       r1 = row['CH4_ratio']
       r2 = row['C2H2_ratio']
       r3 = row['C2H4_ratio']
 # กำหนดเงื่อนไขจาก IEC Table
       if r1 < 0.1 and r2 > 0 and r3 < 0.2:
        return 'PD'     # Partial Discharge (PD)
       elif 0.1 <= r1 <= 0.5 and r2 > 1 and r3 > 1:
        return 'D1 (Sparking)'     # Discharge of low energy (Sparking)
       elif 0.1 <= r1 <= 1 and 0.6 <= r2 <= 2.5 and r3 > 2:
        return 'D2 (Arcing)'     # Discharge of high energy (Arcing)
       elif r1 > 1 and r2 > 0 and r3 < 1:
        return 'T1 ;T<300°C'     # Thermal fault <300°C
       elif r1 > 1 and r2 < 0.1 and 1 <= r3 <= 4:
        return 'T2 ;T=300–700°C'     # Thermal fault 300–700°C
       elif r1 > 1 and r2 < 0.2 and r3 > 4:
        return 'T3 ;T>700°C'     # Thermal fault >700°C
       else:
        return 'Unknown' # -> ถ้าเป็นต้องพิจารณาร่วมกับวิธีอื่น
    iec_result = diagnose_iec(latest)
    st.write(f"**IEC Gas Ratio test:** {iec_result}")

    def ieee_key(row):
      gases = {
        'H2': row.get('H2', 0),
        'CH4': row.get('CH4', 0),
        'C2H2': row.get('C2H2', 0),
        'C2H4': row.get('C2H4', 0),
        'C2H6': row.get('C2H6', 0),
        'CO': row.get('CO', 0),
    }

      key_gas = max(gases, key=gases.get)

      diagnosis_map = {
        'H2': 'Partial Discharge (PD)',
        'CH4': 'Overheating <150°C',
        'C2H6': 'Overheating 150–300°C',
        'C2H4': 'Overheating 300–700°C',
        'C2H2': 'Arcing >700°C',
        'CO': 'Paper insulation aging'
    }

      return diagnosis_map.get(key_gas, 'Unknown')
    ieee_result = ieee_key(latest)
    st.write(f"**IEEE Key Gas Method test:** {ieee_result}")

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    if {'ch4', 'c2h2', 'c2h4'}.issubset(df.columns):

        # ลูปรายแถวเพื่อคำนวณเปอร์เซ็นต์ก๊าซ
        triangle_data = []
        for i, row in df.iterrows():
            total = row['ch4'] + row['c2h2'] + row['c2h4']
            if total > 0:
                ch4_pct = 100 * row['ch4'] / total
                c2h2_pct = 100 * row['c2h2'] / total
                c2h4_pct = 100 * row['c2h4'] / total
                triangle_data.append({
                    'CH₄': ch4_pct,
                    'C₂H₂': c2h2_pct,
                    'C₂H₄': c2h4_pct,
                    'Trans ID TX': df.loc[i, 'Trans ID TX'] if 'Trans ID' in df.columns else f'Trans ID TX{i+1:02d}'
                })

        triangle_df = pd.DataFrame(triangle_data)

        # แสดงกราฟสามเหลี่ยม
        st.markdown("### 🔺 Duval Triangle 1")
        fig = px.scatter_ternary(
            
            triangle_df,
            a='CH₄',
            b='C₂H₂',
            c='C₂H₄',
            #a='C₂H₂',
            #b='C₂H₄',
            #c='CH₄',
            color='Trans ID TX',
            size_max=10
            
        )
        fig.update_traces(marker=dict(size=10))
        
        # ลบเส้น scale
        fig.update_layout(
        ternary=dict(
        aaxis=dict(showgrid=False),
        baxis=dict(showgrid=False),
        caxis=dict(showgrid=False)
    )
)
         # เส้นตัวอย่าง: จากจุด (a1, b1, c1) ไป (a2, b2, c2)
        fig.add_trace(go.Scatterternary(
         a=[0, 165],  # CH4
         b=[70, 30],  # C2H2
         c=[20, 60],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#D1
        fig.add_trace(go.Scatterternary(
         a=[165, 735],  # CH4
         b=[30, 100],  # C2H2
         c=[60, 5],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#D1
        fig.add_trace(go.Scatterternary(
         a=[0, 38],  # CH4
         b=[32.5, 29],  # C2H2
         c=[80, 40],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#D2
        fig.add_trace(go.Scatterternary(
         a=[38, 50],  # CH4
         b=[29, 13],  # C2H2
         c=[40, 38],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#D2
        fig.add_trace(go.Scatterternary(
         a=[50, 87],  # CH4
         b=[13, 15.5],  # C2H2
         c=[38, 30],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#D2
        fig.add_trace(go.Scatterternary(
         a=[0, 35],  # CH4
         b=[16.2, 15],  # C2H2
         c=[90, 50],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#T3
        fig.add_trace(go.Scatterternary(
         a=[35, 50],  # CH4
         b=[15, 0],  # C2H2
         c=[50, 50],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#T3
        fig.add_trace(go.Scatterternary(
         a=[47, 75],  # CH4
         b=[4, 4],  # C2H2
         c=[50, 20],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#T2
        fig.add_trace(go.Scatterternary(
         a=[75, 80],  # CH4
         b=[4, 0],  # C2H2
         c=[20, 20],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#T2
        fig.add_trace(go.Scatterternary(
         a=[75, 97],  # CH4
         b=[4, 4],  # C2H2
         c=[20, 0],  # C2H4
         mode='lines',
         line=dict(color='black', width=1),
         showlegend=False 
    ))#T1
        fig.add_trace(go.Scatterternary(
         a=[98, 98],  # CH4
         b=[2, 0],  # C2H2
         c=[0, 2],  # C2H4
         mode='lines',
         line=dict(color='green', width=1),
         showlegend=False 
))#PD
# ✅ เพิ่มตัวอักษร "DT"
        fig.add_trace(go.Scatterternary(
           a=[20],  # ค่าของ CH4
           b=[25],  # ค่าของ C2H2
           c=[70],  # ค่าของ C2H4
           mode='text',
           text=["DT"],  # ข้อความที่จะแสดง
           textfont=dict(color='black', size=11),
           showlegend=False
    ))
        fig.add_trace(go.Scatterternary(
           a=[20],  # ค่าของ CH4
           b=[47],  # ค่าของ C2H2
           c=[40],  # ค่าของ C2H4
           mode='text',
           text=["D2"],  # ข้อความที่จะแสดง
           textfont=dict(color='black', size=11),
           showlegend=False
    ))
        fig.add_trace(go.Scatterternary(
           a=[20],  # ค่าของ CH4
           b=[75],  # ค่าของ C2H2
           c=[10],  # ค่าของ C2H4
           mode='text',
           text=["D1"],  # ข้อความที่จะแสดง
           textfont=dict(color='black', size=11),
           showlegend=False
    ))
        fig.add_trace(go.Scatterternary(
           a=[20],  # ค่าของ CH4
           b=[10],  # ค่าของ C2H2
           c=[80],  # ค่าของ C2H4
           mode='text',
           text=["T3"],  # ข้อความที่จะแสดง
           textfont=dict(color='black', size=11),
           showlegend=False
    ))
        fig.add_trace(go.Scatterternary(
           a=[60],  # ค่าของ CH4
           b=[2.175],  # ค่าของ C2H2
           c=[40],  # ค่าของ C2H4
           mode='text',
           text=["T2"],  # ข้อความที่จะแสดง
           textfont=dict(color='black', size=11),
           showlegend=False
    ))
        fig.add_trace(go.Scatterternary(
           a=[85],  # ค่าของ CH4
           b=[2.05],  # ค่าของ C2H2
           c=[10],  # ค่าของ C2H4
           mode='text',
           text=["T1"],  # ข้อความที่จะแสดง
           textfont=dict(color='black', size=11),
           showlegend=False
    ))
        fig.add_trace(go.Scatterternary(
           a=[55],  # ค่าของ CH4
           b=[1],  # ค่าของ C2H2
           c=[1],  # ค่าของ C2H4
           mode='text',
           text=["PD"],  # ข้อความที่จะแสดง
           textfont=dict(color='green', size=7),
           showlegend=False
    ))  
        st.plotly_chart(fig)
        st.markdown(
    """
    <div style='text-align:center; margin-top: -65px;'>
        <p>📑 Rererence : IEC 60599</p>
    </div>
    """, 
    unsafe_allow_html=True
)
    else:
        st.error("ไม่พบคอลัมน์ CH₄, C₂H₂, หรือ C₂H₄ ในไฟล์ Excel กรุณาตรวจสอบชื่อคอลัมน์")
   
    def calc_health_index(row):
        def normalize(val, min_val, max_val, reverse=False):
          norm = (val - min_val) / (max_val - min_val)
          norm = max(0, min(norm, 1))
          return 1 - norm if reverse else norm

        def diagnose_iec(row):
            # Define the standard adjustment for when IEC fails & weight needs redistribution
            # This is the same adjustment logic used by your global diagnose_iec's 'else'
            failed_iec_adjustment = {
                'Age_Score': 1/6,
                'Load_Score': 1/6,
                'Oil_Score': 1/6,
                'tdcg_score': 1/6,
                'iec_score': 0,  # Critically sets the IEC weight factor to 0
                'ieee_score': 1/6,
                'duval_score': 1/6
            }

            # Check for h2=0 (using lowercase as 'row' comes from df.apply after column name changes)
            # Also check other critical denominators to prevent division by zero if they are used.
            if row.get('h2', 0) == 0:
                return 0, failed_iec_adjustment # Return 0 score and the weight adjustment

            # Handle other potential division by zero for ratio calculations robustly
            # Example: if c2h4 is a denominator for r2 and is 0, but c2h2 is not 0
            if row.get('c2h4', 0) == 0 and row.get('c2h2', 0) != 0:
                return 0, failed_iec_adjustment
            # Example: if c2h6 is a denominator for r3 and is 0, but c2h4 is not 0
            if row.get('c2h6', 0) == 0 and row.get('c2h4', 0) != 0:
                return 0, failed_iec_adjustment

            # Calculate ratios (ensure denominators are not zero or handle it)
            # These 'get' calls with a default are for safety, but the checks above should handle critical zeros.
            r1 = row.get('ch4',0) / row.get('h2',1) # h2 is confirmed non-zero if we reach here
            
            c2h4_val = row.get('c2h4', 0)
            c2h6_val = row.get('c2h6', 0)

            r2 = row.get('c2h2',0) / c2h4_val if c2h4_val != 0 else (float('inf') if row.get('c2h2',0) !=0 else 0)
            r3 = c2h4_val / c2h6_val if c2h6_val != 0 else (float('inf') if c2h4_val !=0 else 0)
            
            # Original IEC conditions (scores are for Health Index contribution)
            if r1 < 0.1 and r2 > 0 and r3 < 0.2:
                return 0.75, {}  # PD
            elif 0.1 <= r1 <= 0.5 and r2 > 1 and r3 > 1:
                return 0.6, {}   # Discharge of low energy (Sparking)
            elif 0.1 <= r1 <= 1 and 0.6 <= r2 <= 2.5 and r3 > 2:
                return 0.3, {}   # Discharge of high energy (Arcing)
            elif r1 > 1 and r2 > 0 and r3 < 1:
                return 0.6, {}   # Thermal fault <300°C
            elif r1 > 1 and r2 < 0.1 and 1 <= r3 <= 4:
                return 0.4, {}   # Thermal fault 300–700°C
            elif r1 > 1 and r2 < 0.2 and r3 > 4:
                return 0.2, {}   # Thermal fault >700°C
            else:
                # No specific fault type, or ratios fall into undefined/problematic areas
                return 0, failed_iec_adjustment
        
        # ... (duval_1 and ieee_key functions as they are, assuming they return score, {} or score, weight_adjust_dict) ...
        def duval_1(row):
            total = row['ch4'] + row['c2h2'] + row['c2h4']
            if total == 0: # If all Duval gases are zero, normal condition
                return 1.0, {} # Return a perfect score (1.0) and no weight adjustment

            ch4_pct = row['ch4'] / total * 100
            c2h2_pct = row['c2h2'] / total * 100
            c2h4_pct = row['c2h4'] / total * 100

            if 0 <= ch4_pct <= 87 and c2h2_pct >= 45 and c2h4_pct >= 10: return 0.6,{}
            elif 0 <= ch4_pct <= 65 and 13 <= c2h2_pct <= 77 and c2h4_pct >= 23 : return 0.3,{}
            elif ch4_pct <= 47 and 0 <= c2h2_pct <= 15 and c2h4_pct >= 50: return 0.2,{}
            elif ch4_pct > 77 and c2h2_pct < 4 and c2h4_pct <= 20: return 0.6,{}
            elif 27 <= ch4_pct <= 50 and  c2h2_pct < 4  and 20 <= c2h4_pct <= 50: return 0.4 ,{}
            elif ch4_pct >= 98 and 45 <= c2h2_pct <= 50 and 0 <= c2h4_pct <= 2: return 0.75,{}
            elif ch4_pct <= 97 and 4 <= c2h2_pct <= 100 and c2h4_pct >= 2: return 0.45,{}
            else: # Out of Duval standard zones, implies problematic or mixed faults not clearly classifiable by Duval alone
                weights_adj = { # This is the adjustment dict
                    'Age_Score': 1/6, 'Load_Score': 1/6, 'Oil_Score': 1/6,
                    'tdcg_score': 1/6, 'iec_score': 1/6, # Assuming IEC is still 1/6 if Duval fails
                    'ieee_score': 1/6, 'duval_score': 0 # Duval weight becomes 0
                }
                return 0, weights_adj # Score 0 for Duval, and adjust weights

        def ieee_key(row):
            gases = {
                'h2': row.get('h2', 0), 'ch4': row.get('ch4', 0),
                'c2h2': row.get('c2h2', 0), 'c2h4': row.get('c2h4', 0),
                'c2h6': row.get('c2h6', 0), 'co': row.get('co', 0),
            }
            if any(g is None for g in gases.values()): # Should not happen with .get(key,0)
                # This path means a column was entirely missing and .get returned None
                weights_adj = {
                    'Age_Score': 1/6, 'Load_Score': 1/6, 'Oil_Score': 1/6,
                    'tdcg_score': 1/6, 'iec_score': 1/6, 
                    'ieee_score': 0, # IEEE weight becomes 0
                    'duval_score': 1/6
                }
                return 0, weights_adj

            if all(g == 0 for g in gases.values()): # If all gases are zero, it's a healthy sign for this method
                return 1.0, {} # Perfect score, no weight adjustment

            key_gas = max(gases, key=gases.get)
            score_map = {
                'h2': 0.7, 'ch4': 0.95, 'c2h6': 0.9,
                'c2h4': 0.8, 'c2h2': 0.45, 'co': 0.7
            }
            return score_map.get(key_gas, 0), {}
        
         # ล้างชื่อคอลัมน์
        weights = {   # ✅ กำหนดก่อนเรียกใช้ update
        'Age_Score': 1/7,
        'Load_Score': 1/7,
        'Oil_Score': 1/7,
        'tdcg_score': 1/7,
        'iec_score': 1/7,
        'ieee_score': 1/7,
        'duval_score': 1/7
    }

        duval_score, duval_adjust = duval_1(row)
        weights.update(duval_adjust)

        ieee_score, ieee_adjust = ieee_key(row)
        weights.update(ieee_adjust)

        iec_score, iec_adjust = diagnose_iec(row)
        weights.update(iec_adjust)

        total_hc = row[['h2','co','c2h2','c2h4','c2h6','ch4']].sum()
        tdcg_score = normalize(total_hc, 0, 4630, reverse=True)
        age_score = normalize(row['age'], 0, 40, reverse=True)
        load_score = normalize(row['max_load'], 0.5, 1.2, reverse=True)
        oil_score = normalize(row['oil_quality'],0,100,reverse=True)
        hi = 100 * (
        weights['Age_Score'] * age_score +
        weights['Load_Score'] * load_score +
        weights['Oil_Score'] * oil_score +
        weights['tdcg_score'] * tdcg_score +
        weights['iec_score'] * iec_score +
        weights['duval_score'] * duval_score +
        weights['ieee_score'] * ieee_score
    )
        return hi
    
# เพิ่มคอลัมน์ health_index ให้ df ทั้งหมด
    df['health_index'] = df.apply(calc_health_index, axis=1)
    df['oil_date'] = pd.to_datetime(df['oil_date'])
    unique_health_df = df.drop_duplicates(subset=['health_index', 'oil_date']).sort_values('oil_date')
   
    x_labels = unique_health_df['trans_id'].tolist()
    grouped = (
    df.sort_values('oil_date')
    .drop_duplicates(subset=['trans_id', 'oil_date'])
)

    st.markdown("### 💊  Health Treand")
    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = range(len(unique_health_df))
    ax.bar(x_pos, unique_health_df['health_index'], color='red')
    for i, value in enumerate(unique_health_df['health_index']):
        text = ax.text(i, value - 1, f"{value:.1f}%", ha='center', va='top', fontsize=20,weight='bold', color = '#FFD700')
    # ใส่เอฟเฟกต์ขอบดำรอบตัวอักษร
        text.set_path_effects([
    path_effects.Stroke(linewidth=2, foreground='black'),  # ขอบดำ
    path_effects.Normal()  # ตัวอักษรปกติด้านใน
])
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=90)
    #fig.autofmt_xdate()
    ax.set_ylabel("Health Score")
    ax.set_xlabel("Transformer ID")
#ax.legend(title="Transformer ID", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    fig.tight_layout()
    st.pyplot(fig)
    
    # Section: Recommendation
    st.markdown("### 📘 Recommendation")
    recommendations = []
    if health_index < 75:
        recommendations.append("⚡ Schedule DGA retest within 3 months")
    if latest['Max Load'] > 0.9:
        recommendations.append("⚠️ Reduce load below 90%")
    if latest['Oil Quality'] > 80:
        recommendations.append("🛢️ Oil filtration recommended")
    if health_index >= 75:
        recommendations.append(" None ") 
    for rec in recommendations:
        st.write("-", rec)

else:
    st.info("Please upload a .xlsx file with columns: OIL DATE, H2, CO, C2H2, C2H4, C2H6, CH4, CO2, Trans ID, Age, Max Load, Oil Quality")
#streamlit run test.py
