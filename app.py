import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🍷 Undertaker 🍷", layout="wide")

# 🔒 ЭСТЕТИЧНАЯ ЗАЩИТА ПАРОЛЕМ
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Окно пароля по центру экрана, пока не введут правильный
    st.markdown("<h2 style='text-align: center;'>🍷 Undertaker 🍷</h2>", unsafe_allow_html=True)
    user_password = st.text_input("Введи пароль для входа в клуб:", type="password")
    if user_password == "2512":  # 💡 ПОМЕНЯЙ "0000" НА СВОЙ ЛЮБИМЫЙ ПАРОЛЬ!
        st.session_state.authenticated = True
        st.rerun()
    else:
        if user_password:
            st.error("Неверный пароль!")
        st.stop()

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

# Боковое меню — вся эстетика, названия и ползунки живут только здесь!
with st.sidebar:
    st.title("🍷 Undertaker 🍷")
    st.write("---")
    st.header("🚬 Ваши ролевые комнаты")
    
    # Создание новой комнаты
    new_room_name = st.text_input("Название новой ролки:", placeholder="Например: Аниме 86...")
    if st.button("➕ Создать комнату"):
        if new_room_name and new_room_name not in st.session_state.rooms:
            st.session_state.rooms[new_room_name] = {
                "messages": [], 
                "system_prompt": "", 
                "lore_bank": "",
                "model": "DeepSeek R1 (Идеальная память и NSFW)"
            }
            st.session_state.current_room = new_room_name
            st.rerun()

    st.write("---")
    
    # Выбор текущей активной комнаты
    room_list = list(st.session_state.rooms.keys())
    if st.session_state.current_room not in room_list:
        st.session_state.current_room = room_list if room_list else "Основная ролка"
        
    current_room = st.selectbox("Переключить на чат:", room_list, index=room_list.index(st.session_state.current_room))
    st.session_state.current_room = current_room
    
    st.write("---")
    st.header("⚙️ Настройки текущей ролки")
    
    # Индивидуальные настройки для выбранной комнаты
    room_data = st.session_state.rooms[st.session_state.current_room]
    
    # Защита на случай, если имя модели кривое
    current_model = room_data.get("model", "DeepSeek R1 (Идеальная память и NSFW)")
    if current_model not in MODELS:
        current_model = "DeepSeek R1 (Идеальная память и NSFW)"
        
    model_name = st.selectbox("Выбор нейросети", list(MODELS.keys()), index=list(MODELS.keys()).index(current_model))
    st.session_state.rooms[st.session_state.current_room]["model"] = model_name

    # 🎛️ Ползунки настроек ИИ
    st.markdown("### 🎛️ Тонкие настройки ИИ")
    temperature = st.slider("🌡️ Температура (Креативность)", min_value=0.1, max_value=1.5, value=0.8, step=0.1)
    top_p = st.slider("🎯 Top-P (Разнообразие слов)", min_value=0.1, max_value=1.0, value=0.9, step=0.05)
    
    st.write("---")
    
    system_prompt = st.text_area("Системный промт (Твоя роль / Характер бота)", 
                                 value=room_data.get("system_prompt", ""),
                                 placeholder="Напиши сюда, кем должна быть нейросеть...", 
                                 height=150)
    st.session_state.rooms[st.session_state.current_room]["system_prompt"] = system_prompt

    # ✨ Блокнот лора со звёздочками
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

# Работа со средней частью — теперь тут ТОЛЬКО чистый чат без мусорных заголовков!
active_room = st.session_state.rooms[st.session_state.current_room]

# Отображение истории сообщений
for message in active_room.get("messages", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода пользователя с кастомным текстом «Написать Андертейкеру...»
if user_input := st.chat_input("Написать Андертейкеру..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    if "messages" not in st.session_state.rooms[st.session_state.current_room]:
        st.session_state.rooms[st.session_state.current_room]["messages"] = []
    st.session_state.rooms[st.session_state.current_room]["messages"].append({"role": "user", "content": user_input})

    # Формируем скрытый контекст запроса
    full_system_context = ""
    if active_room.get("system_prompt", ""):
        full_system_context += f"Main role and instructions:\n{active_room['system_prompt']}\n\n"
    if active_room.get("lore_bank", ""):
        full_system_context += f"Important lore details to remember:\n{active_room['lore_bank']}\n"

    api_messages = []
    if full_system_context:
        api_messages.append({"role": "system", "content": full_system_context})
        
    for msg in st.session_state.rooms[st.session_state.current_room]["messages"]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # Запрос к SambaNova с учетом крутилок Температуры и Top-P
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            response = client.chat.completions.create(
                model=MODELS[active_room["model"]],
                messages=api_messages,
                temperature=temperature,
                top_p=top_p,
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
