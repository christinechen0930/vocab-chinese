import streamlit as st
import pandas as pd
import random

st.title("🧠 英文單字練習網站")

# 上傳 Excel 題庫
uploaded_file = st.file_uploader("請上傳題庫 Excel 檔（需包含 'English' 和 'Chinese' 欄位）", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "filename" not in st.session_state or st.session_state.filename != uploaded_file.name:
        # 換檔案會重置狀態
        st.session_state.filename = uploaded_file.name
        st.session_state.used_indices = []
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.current_index = None
        st.session_state.show_answer = False
        st.session_state.next_clicked = True
        st.session_state.wrong_answers = []
        st.session_state.mode = "normal"

    # 設定目前題目來源
    if st.session_state.mode == "normal":
        source_df = df
        source_indices = list(range(len(df)))
    else:
        source_df = pd.DataFrame(st.session_state.wrong_answers, columns=["English", "Chinese"])
        source_indices = list(range(len(source_df)))

    # 換題邏輯
    if st.session_state.next_clicked:
        remaining = list(set(source_indices) - set(st.session_state.used_indices))
        if not remaining:
            st.success("🎉 這輪測驗完成囉～")
            percentage = round((st.session_state.score / len(source_indices)) * 100, 2)
            st.info(f"💯 得分：{percentage} / 100")

            if st.session_state.mode == "normal" and st.session_state.wrong_answers:
                st.warning("以下是你這輪錯的單字：")
                for en, zh in st.session_state.wrong_answers:
                    st.write(f"- **{en}** ➜ {zh}")
                st.session_state.mode = "review"
            elif st.session_state.mode == "review":
                st.success("🎊 錯題也複習完囉！好棒棒～～")
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

    # 顯示題目
    if st.session_state.current_index is not None:
        word = source_df.iloc[st.session_state.current_index]
        english_word = word['English']
        chinese_word = word['Chinese']

        # 生成選項
        options = [chinese_word]
        while len(options) < 4:
            option = random.choice(df['Chinese'])
            if option not in options:
                options.append(option)
        random.shuffle(options)

        current = len(st.session_state.used_indices)
        total_q = len(source_indices)
        st.progress(current / total_q, text=f"第 {current} / {total_q} 題")

        st.markdown(f"**目前得分（滿分100）：{round((st.session_state.score / total_q) * 100, 2)}**")
        st.subheader(f"英文：**{english_word}**")

        selected_option = st.radio("請選擇正確的中文意思：", options)

        if st.button("提交答案") and not st.session_state.show_answer:
            st.session_state.total += 1
            st.session_state.show_answer = True
            if selected_option == chinese_word:
                st.session_state.score += 1
                st.success("答對囉！")
            else:
                if st.session_state.mode == "normal":
                    st.session_state.wrong_answers.append((english_word, chinese_word))
                st.error(f"答錯了，正確答案是：{chinese_word}")

        if st.session_state.show_answer:
            if st.button("下一題"):
                st.session_state.next_clicked = True
else:
    st.info("請先上傳一個 Excel 題庫檔才能開始測驗喔～")
