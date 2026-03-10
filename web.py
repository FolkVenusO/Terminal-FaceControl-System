import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="База гостей", page_icon="🗄️")

st.title("Добро пожаловать в клуб Эпштейна")
st.write("Здесь все гости который прошли, через проверки.")

def check_password():
    def password_entered():
        if st.session_state["password"] == '4321':
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.title("Вход в админ-панель")
    st.text_input("Введите пароль", type="password", on_change=password_entered, key="password")

    if st.session_state.get("password_correct") == False:
        st.error("Неверный пароль")

    return False

def get_all_guests():
    connection = sqlite3.connect('guests.db')
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id, name, age, height, visit_time FROM guests")
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []

    connection.close()
    return rows


def delete_guest(guest_id):
    connection = sqlite3.connect('guests.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
    connection.commit()
    connection.close()

if check_password():
    guests_list = get_all_guests()

    if not guests_list:
        st.warning("В базе пока нет ни одного гостя. 🤷‍♂️")
    else:
        st.success(f"Всего гостей в базе: {len(guests_list)}")
        table_data = []
        for row in guests_list:
            guest_name = {
                "ID": row[0],
                "Имя": row[1],
                "Возраст": row[2],
                "Рост": row[3],
                "Время": row[4],
            }
            table_data.append(guest_name)

    st.sidebar.title("📊 Статистика клуба")

    if guests_list:
        df = pd.DataFrame(table_data)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        total_guests = len(guests_list)
        avg_age = sum(row[2] for row in guests_list) / total_guests
        avg_height = sum(row[3] for row in guests_list) / total_guests

        st.sidebar.metric(label="Всего гостей", value=total_guests)
        st.sidebar.metric(label="Средний возраст", value=f"{avg_age:.1f} лет")
        st.sidebar.metric(label="Средний рост", value=f"{avg_height:.1f} см")
        col1, col2= st.columns(2)

        col1.subheader("Полный список")

        search_query = col1.text_input("Поиск по имени:")

        if search_query:
            filtered_data = [guest for guest in table_data if search_query.lower() in guest["Имя"].lower()]
        else:
            filtered_data = table_data

        col1.dataframe(filtered_data)

        col2.subheader("Быстрые действия")
        if col2.button("🎉 Праздновать успех!"):
            st.balloons()
        if col2.button("Почесать голову"):
            st.snow()

        col2.write("---")
        col2.subheader("🗑️ Удаление")

        id_to_delete = col2.number_input("Введите ID гостя для удаления:", min_value=1, step=1)

        if col2.button("❌ Выгнать из клуба"):
            delete_guest(id_to_delete)
            st.success(f"Гость с номером {id_to_delete} удален из базы!")
            st.rerun()

        col2.write("---")
        col2.subheader("📊 Отчеты")

        col2.download_button(
            label="📥 Скачать базу в Excel",
            data=buffer.getvalue(),
            file_name="guests_report.xlsx",
            mime="application/vnd.ms-excel"
        )


        ages = [guest["Возраст"] for guest in table_data]
        st.subheader("Возраст на графике:")
        st.bar_chart(ages)

        heights = [guest["Рост"] for guest in table_data]
        st.subheader("Рост на графике:")
        st.bar_chart(heights)

    st.write("---")
    if st.button("🔄 Обновить данные"):
        st.rerun()
