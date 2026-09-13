import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="🍷 Undertaker 🍷", layout="wide")

# 🔒 ЭСТЕТИЧНАЯ ЗАЩИТА ТВОИМ ПАРОЛЕМ
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🍷 Undertaker 🍷</h2>", unsafe_allow_html=True)
    user_password = st.text_input("Введи пароль для входа в клуб:", type="password")
    if user_password == "2512":  # Твой персональный пароль!
        st.session_state.authenticated = True
        st.rerun()
    else:
        if user_password:
            st.error("Неверный пароль!")
        st.stop()

# 🔑 Твой рабочий API-ключ от OpenRouter зашит намертво внутри:
API_KEY = "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"

# Подключаемся к стабильным серверам OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai",
    api_key=API_KEY
)

# 📦 ТВОИ ЛЮБИМЫЕ МОДЕЛИ БЕЗ ИЗМЕНЕНИЙ
MODELS = {
    "DeepSeek R1 (Идеальная память и рассуждения)": "deepseek/deepseek-r1:free",
    "Llama 3.3 70B (Супер для отыгрыша ролок)": "meta-llama/llama-3.3-70b-instruct:free",
    "Qwen 2.5 72B (Мощная логика и канон)": "qwen/qwen-2.5-72b-instruct:free"
}

# Инициализация структуры комнат в памяти приложения
if "rooms" not in st.session_state:
    st.session_state.rooms = {
        "Основная ролка": {
            "messages": [], 
            "system_prompt": "", 
            "lore_bank": "", 
            "model": "DeepSeek R1 (Идеальная память и рассуждения)"
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
                "model": "DeepSeek R1 (Идеальная память и рассуждения)"
            }
            st.session_state.current_room = new_room_name
            st.rerun()

    st.write("---")
    
    # Выбор текущей активной комнаты с железной защитой от вылетов
    room_list = list(st.session_state.rooms.keys())
    if st.session_state.current_room not in room_list:
        st.session_state.current_room = room_list[0] if room_list else "Основная ролка"
        
    current_room = st.selectbox("Переключить на чат:", room_list, index=room_list.index(st.session_state.current_room))
    st.session_state.current_room = current_room
    
    st.write("---")
    st.header("⚙️ Настройки текущей ролки")
    
    # Индивидуальные настройки для выбранной комнаты
    room_data = st.session_state.rooms[st.session_state.current_room]
    
    current_model = room_data.get("model", "DeepSeek R1 (Идеальная память и рассуждения)")
    if current_model not in MODELS:
        current_model = "DeepSeek R1 (Идеальная память и рассуждения)"
        
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
    
    # Исправленная безопасная очистка и удаление комнат
    if st.button("🗑️ Удалить эту комнату"):
        if len(st.session_state.rooms) > 1:
            old_room = st.session_state.current_room
            del st.session_state.rooms[old_room]
            st.session_state.current_room = list(st.session_state.rooms.keys())[0]
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

# Поле ввода пользователя с плавной стриминговой печатью
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
            st.error(f"Ошибка соединения с OpenRouter: {e}")
            
    if full_response:
        st.session_state.rooms[st.session_state.current_room]["messages"].append({"role": "assistant", "content": full_response})
