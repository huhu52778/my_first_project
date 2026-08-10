import streamlit as st
import json
import os
from datetime import datetime

# ---------- 初始化用户状态 ----------
if "username" not in st.session_state:
    st.session_state.username = ""

def get_data_file():
    """根据用户名返回对应的数据文件名"""
    if st.session_state.username:
        return f"daily_money_{st.session_state.username}.json"
    return None  # 未登录时返回 None

def load_data():
    file = get_data_file()
    if file and os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"transactions": []}

def save_data(data):
    file = get_data_file()
    if file:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

st.set_page_config(page_title="💰 收支管家", layout="centered")
st.title("💰 每日收支管家")

# ---------- 侧边栏：用户登录 ----------
with st.sidebar:
    st.header("👤 我的账本")
    input_name = st.text_input("输入你的名字（登录）", value=st.session_state.username, placeholder="例如：张三")
    if st.button("登录 / 切换用户"):
        if input_name.strip():
            st.session_state.username = input_name.strip()
            st.success(f"✅ 当前用户：{st.session_state.username}")
            st.rerun()
        else:
            st.warning("⚠️ 请输入名字")
    
    if st.session_state.username:
        st.info(f"📖 正在使用：{st.session_state.username} 的账本")
    else:
        st.warning("👆 请先输入名字登录")
        st.stop()  # 未登录时阻止下方操作

    st.divider()
    st.header("➕ 新增记录")
    t_type = st.radio("类型", ["收入", "支出"])
    amount = st.number_input("金额（元）", min_value=0.01, step=0.01, format="%.2f")
    category = st.text_input("分类（可选）", placeholder="如：餐饮、工资")
    note = st.text_input("备注（可选）")
    date = st.date_input("日期", value=datetime.now())
    
    if st.button("提交记录"):
        data = load_data()
        data["transactions"].append({
            "date": date.strftime("%Y-%m-%d"),
            "type": "income" if t_type == "收入" else "expense",
            "amount": float(amount),
            "category": category,
            "note": note,
            "record_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_data(data)
        st.success("✅ 记录已保存！")
        st.rerun()

# ---------- 主界面 ----------
data = load_data()

tab1, tab2, tab3 = st.tabs(["📊 今日概览", "📆 每日汇总", "📈 历史总览"])

with tab1:
    today = get_today()
    day_txs = [t for t in data["transactions"] if t["date"] == today]
    income = sum(t["amount"] for t in day_txs if t["type"] == "income")
    expense = sum(t["amount"] for t in day_txs if t["type"] == "expense")
    balance = income - expense

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 收入", f"{income:.2f} 元")
    col2.metric("💸 支出", f"{expense:.2f} 元")
    col3.metric("📊 结余", f"{balance:.2f} 元")

    if day_txs:
        st.write("**明细**")
        for t in day_txs:
            tag = "➕" if t["type"] == "income" else "➖"
            cat = f"[{t['category']}]" if t.get('category') else ""
            note = f"({t['note']})" if t.get('note') else ""
            st.write(f"{tag} {t['amount']:.2f} 元 {cat} {note}")
    else:
        st.info("今天暂无记录")

with tab2:
    days = {}
    for t in data["transactions"]:
        d = t["date"]
        if d not in days:
            days[d] = {"income": 0, "expense": 0}
        if t["type"] == "income":
            days[d]["income"] += t["amount"]
        else:
            days[d]["expense"] += t["amount"]
    if days:
        for d in sorted(days.keys(), reverse=True):
            info = days[d]
            bal = info["income"] - info["expense"]
            st.write(f"**{d}**  |  收入 {info['income']:.2f}  |  支出 {info['expense']:.2f}  |  结余 {bal:.2f}")
    else:
        st.info("暂无记录")

with tab3:
    total_income = sum(t["amount"] for t in data["transactions"] if t["type"] == "income")
    total_expense = sum(t["amount"] for t in data["transactions"] if t["type"] == "expense")
    total_balance = total_income - total_expense
    st.metric("累计总收入", f"{total_income:.2f} 元")
    st.metric("累计总支出", f"{total_expense:.2f} 元")
    st.metric("当前总余额", f"{total_balance:.2f} 元")
    
    st.divider()
    st.subheader("🗑️ 删除指定记录")
    transactions = data["transactions"]
    if not transactions:
        st.info("暂无记录可删除")
    else:
        for i in range(len(transactions) - 1, -1, -1):
            t = transactions[i]
            col1, col2 = st.columns([4, 1])
            with col1:
                tag = "💰" if t["type"] == "income" else "💸"
                cat = f"[{t.get('category', '')}]" if t.get('category') else ""
                note = f"({t.get('note', '')})" if t.get('note') else ""
                st.write(f"{tag} {t['date']} {t['amount']:.2f} 元 {cat} {note}")
            with col2:
                if st.button("❌ 删除", key=f"del_{i}"):
                    data["transactions"].pop(i)
                    save_data(data)
                    st.success("✅ 已删除该记录！")
                    st.rerun()
