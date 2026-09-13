import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🍷 Undertaker 🍷", layout="wide")
st.title("🍷 Undertaker 🍷")

# Подключаем бесплатный API ключ из секретов
API_KEY = st.secrets["SAMBANOVA_API_KEY"]
client = OpenAI(base_url="https://sambanova.ai", api_key=API_KEY)

# Полный список доступных флагманских моделей
MODELS = {
    "DeepSeek R1 (Идеальная память и NSFW)": "DeepSeek-R1",
    "Qwen 3.8 Max (Новейший флагман)": "Qwen3.8-Max",
    "Llama 3.3 70B (Супер для отыгрыша)": "Meta-Llama-3.3-70B-Instruct"
}

# Инициализация структуры комнат в памяти приложения
if "rooms" not in st.session_state:
    st.session_state.rooms = {
        "Основная ролка": {
            "messages": [], 
            "system_prompt": "", 
            "lore_bank": "", 
            "model": "DeepSeek R1 (Идеальная память и NSFW)"
        }
    }
if "current_room" not in st.session_state:
    st.session_state.current_room = "Основная ролка"

# Боковое меню для управления комнатами и настройками
with st.sidebar:
    st.header("🚬 Ваши ролевые комнаты")
    
    # Создание новой комнаты
    new_room_name = st.text_input("Название новой ролки:", placeholder="Например: Аниме 86...")
    if st.button("➕ Создать комнату"):
        if new_room_name and new_room_name not in st.session_state.rooms:
            st.session_state.rooms[new_room_name] = {
                "messages": [], 
                "system_prompt": "", 
                "lore_bank": "",
                "model": "DeepSeek R1 (Идеальная память and NSFW)"
            }
            st.session_state.current_room = new_room_name
            st.rerun()

    st.write("---")
    
    # Выбор текущей активной комнаты
    room_list = list(st.session_state.rooms.keys())
    current_room = st.selectbox("Переключить на чат:", room_list, index=room_list.index(st.session_state.current_room))
    st.session_state.current_room = current_room
    
    st.write("---")
    st.header("⚙️ Настройки текущей ролки")
    
    # Индивидуальные настройки для выбранной комнаты
    room_data = st.session_state.rooms[st.session_state.current_room]
    
    model_name = st.selectbox("Выбор нейросети", list(MODELS.keys()), 
                              index=list(MODELS.keys()).index(room_data["model"]))
    st.session_state.rooms[st.session_state.current_room]["model"] = model_name
    
    system_prompt = st.text_area("Системный промт (Твоя роль / Характер бота)", 
                                 value=room_data["system_prompt"],
                                 placeholder="Напиши сюда, кем должна быть нейросеть...", 
                                 height=150)
    st.session_state.rooms[st.session_state.current_room]["system_prompt"] = system_prompt

    # ✨ НАШ ОБНОВЛЕННЫЙ БЛОКНОТ ЛОРА И ДЕТАЛЕЙ СО ЗВЕЗДОЧКАМИ
    lore_bank = st.text_area("✨ Блокнот Лора (Сюжет, детали аниме, важные мелочи) ✨", 
                             value=room_data.get("lore_bank", ""),
                             placeholder="Напиши сюда важные мелочи, которые бот не должен забывать...", 
                             height=200)
    st.session_state.rooms[st.session_state.current_room]["lore_bank"] = lore_bank
    
    if st.button("🗑️ Удалить эту комнату"):
        if len(st.session_state.rooms) > 1:
            del st.session_state.rooms[st.session_state.current_room]
            st.session_state.current_room = list(st.session_state.rooms.keys())
            st.rerun()
        else:
            st.session_state.rooms[st.session_state.current_room]["messages"] = []
            st.rerun()

# Работа со средней частью — выбранным чатом
active_room = st.session_state.rooms[st.session_state.current_room]
st.subheader(f"📍 Текущий чат: {st.session_state.current_room}")

# Отображение истории сообщений конкретной комнаты
for message in active_room["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода пользователя
if user_input := st.chat_input("Напишите сообщение персонажу..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.rooms[st.session_state.current_room]["messages"].append({"role": "user", "content": user_input})

    # Формируем скрытый контекст запроса с учетом Системного промта и Блокнота Лора
    full_system_context = ""
    if active_room["system_prompt"]:
        full_system_context += f"Main role and instructions:\n{active_room['system_prompt']}\n\n"
    if active_room.get("lore_bank", ""):
        full_system_context += f"Important lore details to remember:\n{active_room['lore_bank']}\n"

    api_messages = []
    if full_system_context:
        api_messages.append({"role": "system", "content": full_system_context})
        
    for msg in active_room["messages"]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # Запрос к SambaNova
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model=MODELS[active_room["model"]],
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
            st.error(f"Ошибка. Текст ошибки: {e}")
            
    st.session_state.rooms[st.session_state.current_room]["messages"].append({"role": "assistant", "content": full_response})
