import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Бухгалтер-калькулятор",
    page_icon="📊",
    layout="centered",
)

st.title("📊 AI Бухгалтер-калькулятор")
st.caption("Голосовой преподаватель • Русский / Қазақша")

INSTRUCTIONS = """
Ты — терпеливый преподаватель профессии «бухгалтер-калькулятор»
для кафе и ресторанов в Казахстане.

Обучай человека с абсолютного нуля. Объясняй простыми словами,
по одному шагу за раз, с примерами в тенге. Учи калькуляции блюд,
себестоимости, технологическим картам, приходам, расходам,
складскому учёту, инвентаризации, списаниям, Excel и 1С.

Поддерживай русский и казахский языки. Отвечай на языке вопроса.
После объяснения предлагай одно небольшое практическое задание.
Проверяй вычисления подробно. Не выдумывай нормы законодательства
Казахстана; если вопрос зависит от актуальных правил, предупреди,
что их нужно проверить по официальному источнику.
"""

def get_client():
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

client = get_client()

if client is None:
    st.warning(
        "Чтобы включить ИИ, добавь OPENAI_API_KEY в Secrets "
        "настройках приложения. Не публикуй ключ в коде GitHub."
    )
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def ask_teacher(question: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=INSTRUCTIONS,
        input=st.session_state.messages + [
            {"role": "user", "content": question}
        ],
    )
    return response.output_text

def make_speech(text: str) -> bytes:
    audio = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="shimmer",
        input=text,
    )
    return audio.read()

question = st.chat_input("Напиши вопрос преподавателю...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Преподаватель готовит ответ..."):
            try:
                answer = ask_teacher(question)
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
                with st.spinner("Готовлю голосовой ответ..."):
                    audio = make_speech(answer)
                st.audio(audio, format="audio/mp3")
            except Exception as error:
                st.error("Не удалось получить ответ. Проверь API-ключ и подключение.")
                st.caption(f"Техническая информация: {error}")

st.divider()
st.subheader("🎤 Задать вопрос голосом")
recording = st.audio_input("Нажми и запиши свой вопрос")

if recording and st.button("Распознать речь и спросить", type="primary"):
    with st.spinner("Распознаю речь..."):
        try:
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=("question.wav", recording.getvalue(), "audio/wav"),
            )
            spoken_question = transcript.text
            st.write("Распознано:", spoken_question)
            st.session_state.messages.append(
                {"role": "user", "content": spoken_question}
            )
            with st.spinner("Преподаватель отвечает..."):
                answer = ask_teacher(spoken_question)
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
            st.audio(make_speech(answer), format="audio/mp3")
        except Exception as error:
            st.error("Не удалось обработать голосовой вопрос.")
            st.caption(f"Техническая информация: {error}")

with st.sidebar:
    st.header("📚 Учебная программа")
    st.write(
        "1. Основы учёта\n"
        "2. Калькуляция блюд\n"
        "3. Себестоимость\n"
        "4. Технологические карты\n"
        "5. Склад и инвентаризация\n"
        "6. Списание продуктов\n"
        "7. Excel и 1С"
    )
    if st.button("Очистить диалог"):
        st.session_state.messages = []
        st.rerun()
