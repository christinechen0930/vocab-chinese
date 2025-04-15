import streamlit as st
import pandas as pd
import random

st.title("🧠 英文單字選擇題練習")

uploaded_file = st.file_uploader("請上傳題庫 Excel 檔（需包含 'English' 和 'Chinese' 欄位）", type=["xlsx"])

if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# 換檔案就重置
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

# 題庫選擇
if st.session_state.mode == "normal":
    source_df = df
else:
    source_df = pd.DataFrame(st.session_state.wrong_answers, columns=["English", "Chinese"])

source_indices = list(range(len(source_df)))

# 出新題目
if st.session_state.next_clicked:
    remaining = list(set(source_indices) - set(st.session_state.used_indices))
    if not remaining:
        st.success("🎉 測驗完成ㄌ～")
        percentage = round((st.session_state.score / len(source_indices)) * 100, 2)
        st.info(f"💯 得分：{percentage} / 100")

        if st.session_state.mode == "normal" and st.session_state.wrong_answers:
            st.warning("以下是你這輪錯的單字：")
            for en, zh in st.session_state.wrong_answers:
                st.write(f"- **{en}** ➜ {zh}")
            st.session_state.mode = "review"
        elif st.session_state.mode == "review":
            st.success("🎊 錯題也複習完ㄌ！你超棒ㄉ 😆")
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

# 顯示選擇題
if st.session_state.current_index is not None:
    word = source_df.iloc[st.session_state.current_index]
    english_word = word['English']
    correct_chinese = word['Chinese']

    # 選項亂數生成（含正確答案 + 3 個錯的）
    all_chinese = df['Chinese'].tolist()
    other_choices = list(set(all_chinese) - {correct_chinese})
    wrong_choices = random.sample(other_choices, k=3) if len(other_choices) >= 3 else other_choices
    options = wrong_choices + [correct_chinese]
    random.shuffle(options)

    # 顯示題目
    current = len(st.session_state.used_indices)
    total_q = len(source_indices)
    st.progress(current / total_q, text=f"第 {current} / {total_q} 題")

    st.markdown(f"**目前得分（滿分100）：{round((st.session_state.score / total_q) * 100, 2)}**")
    st.subheader(f"請選出 **{english_word}** 的中文意思：")

    st.session_state.selected_option = st.radio("選擇答案：", options, index=0, key=f"option_{st.session_state.current_index}")

    if st.button("提交答案") and not st.session_state.show_answer:
        st.session_state.total += 1
        st.session_state.show_answer = True
        if st.session_state.selected_option == correct_chinese:
            st.session_state.score += 1
            st.success("答對ㄌ～太強啦！🥇")
        else:
            if st.session_state.mode == "normal":
                st.session_state.wrong_answers.append((english_word, correct_chinese))
            st.error(f"答錯ㄌ，正確答案是：{correct_chinese}")

    if st.session_state.show_answer:
        if st.button("下一題"):
            st.session_state.next_clicked = True
