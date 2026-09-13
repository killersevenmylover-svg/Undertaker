import os
import requests
import streamlit as st

st.set_page_config(page_title="🍷 Undertaker 🍷", layout="wide")

# 🔒 ЭСТЕТИЧНАЯ ЗАЩИТА ТВОИМ ПАРОЛЕМ
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🍷 Undertaker 🍷</h2>", unsafe_allow_html=True)
    user_password = st.text_input("Введи пароль для входа в клуб:", type="password")
    if user_password == "2512":  # ✅ Твой новый персональный пароль!
        st.session_state.authenticated = True
        st.rerun()
    else:
        if user_password:
            st.error("Неверный пароль!")
        st.stop()

# 🔑 Твой личный рабочий API-ключ уже зашит намертво внутри:
API_KEY = "e851758e-5458-4271-a552-bbe5b8854536"

# Официальные точные системные имена моделей для SambaNova
MODELS = {
    "DeepSeek R1 (Идеальная память и NSFW)": "deepseek-ai/DeepSeek-R1",
    "gpt-oss 120B (Тяжелый флагман)": "gpt-oss-120b",
    "Llama 3.3 70B (Супер для отыгрыша)": "meta-llama/Llama-3.3-70B-Instruct"
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
    
    room_data = st.session_state.rooms[st.session_state.current_room]
    
    current_model = room_data.get("model", "DeepSeek R1 (Идеальная память and NSFW)")
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

# Отображение истории сообщений
active_room = st.session_state.rooms[st.session_state.current_room]

for message in active_room.get("messages", []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Прямой защищённый запрос с маскировкой под Chrome
if user_input := st.chat_input("Написать Андертейкеру..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    if "messages" not in st.session_state.rooms[st.session_state.current_room]:
        st.session_state.rooms[st.session_state.current_room]["messages"] = []
    st.session_state.rooms[st.session_state.current_room]["messages"].append({"role": "user", "content": user_input})

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
        
        # Полный обход анти-бот систем
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        payload = {
            "model": MODELS[active_room["model"]],
            "messages": api_messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False
        }
        
        try:
            url = "https://sambanova.ai"
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result_json = response.json()
                full_response = result_json["choices"][0]["message"]["content"]
                message_placeholder.markdown(full_response)
                st.session_state.rooms[st.session_state.current_room]["messages"].append({"role": "assistant", "content": full_response})
            else:
                st.error(f"Ошибка сервера ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Ошибка соединения: {e}")
