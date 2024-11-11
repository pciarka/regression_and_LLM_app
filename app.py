from pathlib import Path
from datetime import date
from getpass import getpass
from IPython.display import Image
import instructor
from pydantic import BaseModel
# from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
from pycaret.regression import  load_model, predict_model
from typing import Optional
import streamlit as st

from langfuse.decorators import observe
from langfuse.openai import OpenAI

# załadowanie .env i wczytanie klucza
load_dotenv()
key = os.getenv("OPENAI_API_KEY")

# schemat odpowiedzi AI
class Desc_of_men(BaseModel):
    Age_category: Optional[int] = None
    Gender: Optional[int] = None
    Time_5_km: Optional[int] = None
    
# dane wejściowe 
# input()="jestem mężczyzną, mam 100 lat przebiegam 5km w 30 minut" 
#user_input = input("Napisz o sobie: ")

# funkcja  - pytanie do AI
@observe()
def ask_AI (input):
    instructor_openai_client = instructor.from_openai(OpenAI(api_key=key))

    resp_AI = instructor_openai_client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Desc_of_men,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Wypełnij klasę Desc_of_men:  
                        -Age_category wiek zaokrąglony do pełnych dziesięcioleci w dół
                        Gender płeć 0 lub 1
                        Time_5_km czas przebiegnięcia 5 km przeliczony na sekundy
                        nie zmyślaj danych, jak nie wiesz zwróć wtedy None
                        jeśli prompt jest pusty zwróć 3 x None
                        Twój input: """+ input,
                    },
                    # {
                    #     "type": "image_url",
                    #     "image_url": {
                    #         "url": image_data,
                    #         "detail": "high"
                    #     },
                    # },
                ],
            },
        ],
    )
    return resp_AI

#Sprawdzenie, czy któraś z kolumn ma brakującą wartość (NaN)
def check_AI_response(df):
    if pd.isna(df.loc[0, 'Age_category']) or pd.isna(df.loc[0, 'Gender']) or pd.isna(df.loc[0, 'Time_5_km']):
        return False
    return True

# Wydruk czego brakuje
def check_AI_response_info(df):
    missing_info = ""
    
    if pd.isna(df.loc[0, 'Age_category']):
        missing_info += f"<br> coś o Twoim wieku, "
    if pd.isna(df.loc[0, 'Gender']):
        missing_info += f"<br>  o Twojej płci, "
    if pd.isna(df.loc[0, 'Time_5_km']):
        missing_info += f"<br> jak idzie Ci bieganie na 5 km, "
    
    # Jeżeli missing_info nie jest pusty, znaczy że są brakujące dane
    if missing_info:
        # Usunięcie ostatniego przecinka i spacji
        missing_info = missing_info.rstrip(', ')
        return st.markdown(f"Potrzebuję informacji, dopisz je: {missing_info}?", unsafe_allow_html=True)
    else:
        return st.write("Dziękuję - mam wszystkie potrzebne informacje.")
    
# funkcja sprawdzenie odpowiedzi z AI i dopytka lub podanie wyniku przetworzenia modelu
def predict(df):
        # 1. Załaduj zapisany model
        model = load_model('best_time_model')  # Upewnij się, że model jest w katalogu roboczym i bez rozszerzenia '.pkl'
        # 2. Przygotuj nowe dane do predykcji
        new_data = df
        # 3. Wykonaj predykcje
        predictions = predict_model(model, data=new_data, verbose=False)
        # Zmień nazwę kolumny predykcji na 'Predicted_time_of_halfmarathon'
        predictions = predictions.rename(columns={'prediction_label': 'Predicted_time_of_halfmarathon'})
        # Wyświetl wynik predykcji
        return predictions
  
def convert_seconds(total_seconds):
    hours = int(total_seconds // 3600)          # Pełne godziny
    minutes = int((total_seconds % 3600) // 60) # Pełne minuty
    seconds = int(total_seconds % 60)           # Pełne sekundy
    return hours, minutes, seconds

st.title("Cześć, sprawdzę dla Ciebie jaki czas osiągniesz w półmaratonie.")
st.subheader("""Opowiedz mi trochę o sobie: jesteś kobietą czy mężczyzną, ile masz lat oraz jaki masz aktualny czas na 5 km""")

# Dane początkowe pusty df załadowany do session state
if 'df' not in st.session_state:
    data = {
    "Age_category": [None],  # przykładowe kategorie wiekowe
    "Gender": [None],  # przykładowe płcie
    "Time_5_km": [None]  # przykładowy czas na 5 km w minutach
    }
    st.session_state.df =  pd.DataFrame(data)
df= st.session_state.df

if "user_input" not in st.session_state:
    st.session_state.user_input = ''
user_input = st.session_state.user_input
st.write(st.session_state)  #tymczasowy wydruk session_state
       
# Właściwy kod apki to poniższe dwa if'y            

user_input = st.text_input("Napisz o sobie:", st.session_state.user_input, key=f"input_2")
if st.button("Zatwierdź", key=f"input_3"):
        df = ask_AI(user_input)
        df = pd.DataFrame([df.dict()])
        while not check_AI_response(df):
            st.write(df) #tymczasowy wydruk tabeli z danymi
            check_AI_response_info(df) # info dla usera o czym opowiedzieć
            break
      
if check_AI_response(df): 
    a=predict(df)
    st.write(a) #tymczasowy wydruk odpowiedzi AI
    total_seconds = a.loc[0, 'Predicted_time_of_halfmarathon']
    hours, minutes, seconds = convert_seconds(total_seconds)
    your_time=(f"Przewidywany czas ukończenia półmaratonu to: {hours}h {minutes}min {seconds}sek \n Powodzenia w biegu!")
    st.write(your_time)



