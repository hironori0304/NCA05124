import streamlit as st
import pandas as pd
import base64
from datetime import datetime

# ページのタイトルを設定
st.title('栄養価計算アプリ')

# セッション状態を管理するための初期化
if 'result_df' not in st.session_state:
    st.session_state['result_df'] = pd.DataFrame(columns=['食品名', '重量（g）', 'エネルギー（kcal）', 'たんぱく質（g）', '脂質（g）', '炭水化物（g）', '食塩（g）', '単価（円）'])
    st.session_state['reset_clicked'] = False  # 初期状態ではリセットボタンがクリックされていない状態とします


# ウィジェットを配置
uploaded_file = st.file_uploader('食品データベースをアップロード', type='csv')
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='shift_jis')
    selected_food = st.selectbox('食品を選択', df['食品名'].unique())

    # 重量の入力ウィジェットを配置
    weight = st.number_input('重量（g）', min_value=0.0, format='%0.1f')

    if st.button('登録') and weight > 0:
        # 選択した食品の情報を取得
        selected_food_info = df[df['食品名'] == selected_food].iloc[0]
        
        # 栄養価の計算
        energy = selected_food_info['エネルギー'] * weight / 100
        protein = selected_food_info['たんぱく質'] * weight / 100
        fat = selected_food_info['脂質'] * weight / 100
        carbs = selected_food_info['炭水化物'] * weight / 100
        salt = selected_food_info['食塩'] * weight / 100
        price = selected_food_info['単価'] * weight / 100

        # 登録したデータをDataFrameに追加
        new_row = pd.DataFrame({
            '食品名': [selected_food],
            '重量（g）': [weight],
            'エネルギー（kcal）': [energy],
            'たんぱく質（g）': [protein],
            '脂質（g）': [fat],
            '炭水化物（g）': [carbs],
            '食塩（g）': [salt],
            '単価（円）': [price]
        })
        st.session_state['result_df'] = pd.concat([st.session_state['result_df'], new_row], ignore_index=True)
        
# 登録した表を表示
st.subheader('登録済みデータ')
if 'result_df' in st.session_state:
    # 行を選択するためのチェックボックスを追加
    rows_to_delete = st.session_state['result_df'].index.tolist()
    checked_rows = st.checkbox("全て選択")
    if checked_rows:
        rows_to_delete = st.session_state['result_df'].index.tolist()
    else:
        rows_to_delete = st.multiselect('削除する行を選択', st.session_state['result_df'].index.tolist())

    # チェックされた行を削除
    if st.button('選択した行を削除'):
        st.session_state['result_df'] = st.session_state['result_df'].drop(rows_to_delete)
        st.success('選択した行が削除されました。')
    
    # 登録したデータを表示（小数点第1位まで）
    st.dataframe(st.session_state['result_df'].round(1))

    # 登録したデータのCSVファイルをダウンロードするリンクを生成
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    registered_csv = st.session_state['result_df'].round(1).to_csv(index=False, encoding='shift_jis')  # Shift-JISでエンコード
    b64_registered = base64.b64encode(registered_csv.encode('shift_jis')).decode()
    registered_filename = f'registered_food_list_{current_time}.csv'
    href_registered= f'<a href="data:file/csv;base64,{b64_registered}" download="{registered_filename}">登録したデータのCSVファイルをダウンロード</a>'
    st.markdown(href_registered, unsafe_allow_html=True)

 # 合計を計算
    if 'result_df' in st.session_state:
        total_energy = st.session_state['result_df']['エネルギー（kcal）'].sum()
        total_protein = st.session_state['result_df']['たんぱく質（g）'].sum()
        total_fat = st.session_state['result_df']['脂質（g）'].sum()
        total_carbs = st.session_state['result_df']['炭水化物（g）'].sum()
        total_salt = st.session_state['result_df']['食塩（g）'].sum()
        total_price = st.session_state['result_df']['単価（円）'].sum()

        # 合計を表で表示
        st.write('### 合計')
        total_row = pd.DataFrame({
            '食品名': ['合計'],
            '重量（g）': ['none'],
            'エネルギー（kcal）': [total_energy],
            'たんぱく質（g）': [total_protein],
            '脂質（g）': [total_fat],
            '炭水化物（g）': [total_carbs],
            '食塩（g）': [total_salt],
            '単価（円）': [total_price]
        })

        # 登録データと合計を組み合わせた表を作成
        combined_table = pd.concat([st.session_state['result_df'], total_row])
        st.dataframe(combined_table)

        # 登録データと合計を組み合わせたCSVファイルをダウンロードするリンクを生成
        combined_csv = combined_table.round(1).to_csv(index=False, encoding='shift_jis')  # Shift-JISでエンコード
        b64_combined = base64.b64encode(combined_csv.encode('shift_jis')).decode()
        combined_filename = f'combined_food_list_{current_time}.csv'
        href_combined = f'<a href="data:file/csv;base64,{b64_combined}" download="{combined_filename}">登録データと合計のCSVファイルをダウンロード</a>'
        st.markdown(href_combined, unsafe_allow_html=True)
        
 