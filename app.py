import streamlit as st
import pandas as pd
import random

st.title("🧠 英文單字選擇題練習")

uploaded_file = st.file_uploader("請上傳題庫 Excel 檔（需有 'English' 和 'Chinese' 欄位）", type=["xlsx"])

# 沒上傳就先不繼續
if not uploaded_file:
    st.info("請先上傳題庫檔案才能開始～")
    st.stop()

# 讀檔 & 初始化
df = pd.read_excel(uploaded_file)

# 初始化 session state
if "filename" not in st.session_state or st.session_state.filename != uploaded_file.name:
    st.session_state.filename = uploaded_file.name
    st.session_state.used_indices = []
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.current_index = None
    st.session_state.next_clicked = True
    st.session_state.wrong_answers = []
    st.session_state.mode = "normal"

# 題庫來源
source_df = (
    pd.DataFrame(st.session_state.wrong_answers, columns=["English", "Chinese"])
    if st.session_state.mode == "review"
    else df
)
source_indices = list(range(len(source_df)))

# 換題
if st.session_state.next_clicked:
    remaining = list(set(source_indices) - set(st.session_state.used_indices))
    if not remaining:
        st.success("🎉 測驗完成ㄌ！")
        percent = round((st.session_state.score / len(source_indices)) * 100, 2)
        st.info(f"得分：{percent} / 100")
        if st.session_state.mode == "normal" and st.session_state.wrong_answers:
            st.warning("你這輪錯的單字：")
            for en, zh in st.session_state.wrong_answers:
                st.write(f"- **{zh}** ➜ {en}")
            st.session_state.mode = "review"
        else:
            st.success("🎊 錯題也複習完ㄌ，太棒ㄌ～")
            st.session_state.mode = "normal"
            st.session_state.wrong_answers = []

        st.session_state.used_indices = []
        st.session_state.score = 0
        st.session_state.total = 0

    # 出題
    remaining = list(set(source_indices) - set(st.session_state.used_indices))
    if remaining:
        st.session_state.current_index = random.choice(remaining)
        st.session_state.used_indices.append(st.session_state.current_index)
        st.session_state.next_clicked = False

# 顯示題目
if st.session_state.current_index is not None:
    word = source_df.iloc[st.session_state.current_index]
    correct_english = word["English"]
    chinese = word["Chinese"]

    options = [correct_english]
    while len(options) < 4:
        choice = random.choice(df["English"].tolist())
        if choice not in options:
            options.append(choice)
    random.shuffle(options)

    current = len(st.session_state.used_indices)
    total_q = len(source_indices)
    st.progress(current / total_q, text=f"第 {current} / {total_q} 題")
    st.markdown(f"**目前得分（滿分100）：{round((st.session_state.score / total_q) * 100, 2)}**")

    st.subheader(f"中文：**{chinese}**")
    answer = st.radio("請選出對應英文單字：", options)

    if st.button("提交答案"):
        st.session_state.total += 1
        if answer == correct_english:
            st.session_state.score += 1
            st.success("🎯 答對ㄌ！")
        else:
            if st.session_state.mode == "normal":
                st.session_state.wrong_answers.append((correct_english, chinese))
            st.error(f"答錯ㄌ，正確答案是：{correct_english}")
        if st.button("下一題"):
            st.session_state.next_clicked = True
