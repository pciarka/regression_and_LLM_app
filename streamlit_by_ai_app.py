import streamlit as st
import openai
import pandas as pd
import os
from dotenv import load_dotenv

# Wczytanie klucza API OpenAI
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Funkcja wywołująca model OpenAI do przetwarzania danych i zwrócenia DataFrame
def extract_data_from_text(text):
    try:
        # Wywołanie modelu z endpointem v1/completions
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Możesz również użyć gpt-4, jeśli masz dostęp
            prompt=f"Extract gender (Male/Female), age category, and 5 km time (in seconds) from the following description: {text}",
            max_tokens=50,
            temperature=0.2
        )

        # Odpowiedź z modelu zawiera 'choices' z 'text'
        extracted_data = response['choices'][0]['text'].strip()

        # Zakładamy, że model zwróci dane w formacie: "Male, 25, 1800"
        parts = extracted_data.split(',')

        # Walidujemy wynik, sprawdzając, czy uzyskaliśmy wszystkie trzy informacje
        if len(parts) == 3:
            gender, age_category, time_5k = parts[0].strip(), parts[1].strip(), parts[2].strip()
        else:
            gender, age_category, time_5k = None, None, None

        # Tworzymy DataFrame na podstawie wyodrębnionych danych
        return pd.DataFrame({
            'Gender': [gender],
            'Age Category': [age_category],
            '5 km Time': [time_5k]
        })

    except Exception as e:
        st.error(f"Wystąpił błąd: {e}")
        return None

# Funkcja sprawdzająca brakujące dane i generująca dodatkowe pytania
def get_missing_info_prompt(dataframe):
    missing_fields = []
    if not dataframe['Gender'].iloc[0]:
        missing_fields.append("gender")
    if not dataframe['Age Category'].iloc[0]:
        missing_fields.append("age category")
    if not dataframe['5 km Time'].iloc[0]:
        missing_fields.append("5 km time")

    # Tworzymy prośbę o uzupełnienie brakujących informacji
    if missing_fields:
        return "Opowiedz więcej o " + ", ".join(missing_fields)
    return None

# Nagłówek aplikacji
st.title("Cześć, sprawdzę dla Ciebie jaki czas osiągniesz w półmaratonie.")
st.subheader("Opowiedz mi trochę o sobie: jesteś kobietą czy mężczyzną, ile masz lat oraz jaki masz aktualny czas na 5 km")

# Przechowujemy stan aplikacji, aby umożliwić dodatkowe iteracje zapytań
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
if "followup_prompt" not in st.session_state:
    st.session_state.followup_prompt = None

# Okno tekstowe dla użytkownika do wprowadzenia informacji
if st.session_state.followup_prompt:
    user_input = st.text_area(st.session_state.followup_prompt, placeholder="Wpisz tutaj...")
else:
    user_input = st.text_area("Opisz siebie", placeholder="Wpisz tutaj...")

# Przycisk wyślij
if st.button("Wyślij"):
    if user_input:
        with st.spinner("Przetwarzanie danych..."):
            # Jeżeli nie mamy jeszcze DataFrame, wywołujemy model po raz pierwszy
            if st.session_state.dataframe is None:
                st.session_state.dataframe = extract_data_from_text(user_input)
            else:
                # Jeśli już istnieje, aktualizujemy go o nowe informacje z modelu
                new_data = extract_data_from_text(user_input)
                for col in ["Gender", "Age Category", "5 km Time"]:
                    if not st.session_state.dataframe[col].iloc[0] and new_data[col].iloc[0]:
                        st.session_state.dataframe[col].iloc[0] = new_data[col].iloc[0]

            # Sprawdzamy, czy wszystkie dane są dostępne
            missing_info = get_missing_info_prompt(st.session_state.dataframe)
            if missing_info:
                # Jeśli brakuje jakichś danych, zapisujemy prompt i prosimy o więcej informacji
                st.warning(missing_info)
                st.session_state.followup_prompt = missing_info
            else:
                # Jeśli dane są kompletne, wyświetlamy wynik
                st.write("Oto przetworzone dane:")
                st.dataframe(st.session_state.dataframe)
                st.session_state.followup_prompt = None  # Czyścimy prompt po zakończeniu
    else:
        st.warning("Proszę wprowadzić informacje o sobie.")
