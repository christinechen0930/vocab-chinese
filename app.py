import streamlit as st
import pandas as pd
import random

st.title("🧠 英文單字選擇題練習網站")

# 上傳 Excel 題庫
uploaded_file = st.file_uploader("請上傳題庫 Excel 檔（需包含 'English' 和 'Chinese' 欄位）", type=["xlsx"])

# 如果有上傳檔案，讀取並初始化
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "filename" not in st.session_state or st.session_state.filename != uploaded_file.name:
        st.session_state.filename = uploaded_file.name
        st.session_state.used_indices = []
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.current_index = None
        st.session_state.show_answer = False
        st.session_state.next_clicked = True
        st.session_state.wrong_answers = []
        st.session_state.mode = "normal"
        st.session_state.selected_option = None

    # 題目來源
    if st.session_state.mode == "normal":
        source_df = df
        source_indices = list(range(len(df)))
    else:
        source_df = pd.DataFrame(st.session_state.wrong_answers, columns=["English", "Chinese"])
        source_indices = list(range(len(source_df)))

    # 換題
    if st.session_state.next_clicked:
        remaining = list(set(source_indices) - set(st.session_state.used_indices))
        if not remaining:
            st.success("🎉 這輪測驗完成ㄌ～")
            percentage = round((st.session_state.score / len(source_indices)) * 100, 2)
            st.info(f"💯 得分：{percentage} / 100")

            if st.session_state.mode == "normal" and st.session_state.wrong_answers:
                st.warning("以下是你這輪錯的單字：")
                for en, zh in st.session_state.wrong_answers:
                    st.write(f"- **{en}** ➜ {zh}")
                st.session_state.mode = "review"
            elif st.session_state.mode == "review":
                st.success("🎊 錯題也複習完ㄌ！好棒棒～～")
                st.session_state.mode = "normal"
                st.session_state.wrong_answers = []

            st.session_state.used_indices = []
            st.session_state.score = 0
            st.session_state.total = 0

        # 出下一題
        remaining = list(set(source_indices) - set(st.session_state.used_indices))
        if remaining:
            st.session_state.current_index = random.choice(remaining)
            st.session_state.used_indices.append(st.session_state.current_index)
            st.session_state.show_answer = False
            st.session_state.next_clicked = False
            st.session_state.selected_option = None

    # 顯示題目
    if st.session_state.current_index is not None:
        word = source_df.iloc[st.session_state.current_index]
        english_word = word['English']
        correct_chinese = word['Chinese']

        # 產生四個選項（包含正確答案）
        all_chinese = list(df['Chinese'].unique())
        options = [correct_chinese]
        while len(options) < 4:
            distractor = random.choice(all_chinese)
            if distractor not in options:
                options.append(distractor)
        random.shuffle(options)

        current = len(st.session_state.used_indices)
        total_q = len(source_indices)
        st.progress(current / total_q, text=f"第 {current} / {total_q} 題")

        st.markdown(f"**目前得分（滿分100）：{round((st.session_state.score / total_q) * 100, 2)}**")
        st.subheader(f"英文單字：**{english_word}**")

        # 選擇題
        st.session_state.selected_option = st.radio("請選擇正確的中文意思：", options, index=None)

        if st.button("提交答案") and not st.session_state.show_answer:
            st.session_state.total += 1
            st.session_state.show_answer = True
            if st.session_state.selected_option == correct_chinese:
                st.session_state.score += 1
                st.success("答對ㄌ！")
            else:
                if st.session_state.mode == "normal":
                    st.session_state.wrong_answers.append((english_word, correct_chinese))
                st.error(f"答錯ㄌ，正確答案是：{correct_chinese}")

        if st.session_state.show_answer:
            if st.button("下一題"):
                st.session_state.next_clicked = True
else:
    st.info("請先上傳一個 Excel 題庫檔才能開始測驗喔～")
