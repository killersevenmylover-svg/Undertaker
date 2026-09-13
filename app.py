import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🎭 Приватная ролевая комната", layout="wide")
st.title("🎭 Моя приватная ролевая комната")

# Подключаем бесплатный API ключ из секретов
API_KEY = st.secrets["SAMBANOVA_API_KEY"]
client = OpenAI(base_url="https://sambanova.ai", api_key=API_KEY)

# Список доступных огромных моделей
MODELS = {
    "Llama 3.3 70B (Супер для отыгрыша)": "Meta-Llama-3.3-70B-Instruct",
    "Qwen 2.5 72B (Отличная логика)": "Qwen2.5-72B-Instruct"
}

# Боковое меню для настроек
with st.sidebar:
    st.header("⚙️ Настройки ролки")
    model_name = st.selectbox("Выбор нейросети", list(MODELS.keys()))
    system_prompt = st.text_area("Системный промт (Сюжет / Твоя роль)", 
                                 placeholder="Напиши сюда, кем должна быть нейросеть...", 
                                 height=200)
    if st.button("Очистить чат"):
        st.session_state.messages = []

# Инициализация истории сообщений
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение старых сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода пользователя
if user_input := st.chat_input("Напишите сообщение персонажу..."):
    # Показываем сообщение пользователя
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Формируем запрос для нейросети
    api_messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # Запрос к SambaNova
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model=MODELS[model_name],
                messages=api_messages,
                temperature=0.8,
                stream=True
            )
            for chunk in response:
                if chunk.choices.delta.content:
                    full_response += chunk.choices.delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ошибка. Проверьте ключ в настройках. Текст ошибки: {e}")
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
