from pathlib import Path
from datetime import date
from getpass import getpass
from IPython.display import Image
import instructor
from pydantic import BaseModel
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os
from pycaret.regression import  load_model, predict_model
from typing import Optional

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
user_input = input("Napisz o sobie: ")

# funkcja  - pytanie do AI
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
                        "text": """Wypełnij klasę Desc_of_men  
                        wiek zaokrąglony do pełnych dziesięcioleci w dół i czas przebiegnięcia 5 km przeliczony na sekundy,
                        nie zmyślaj danych jak nie wiesz zwróć wtedy None
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

def check_AI_response(df):
    # Sprawdzenie, czy któraś z kolumn ma brakującą wartość (NaN)
    # if pd.isna(df.loc[0, 'Age_category']) or pd.isna(df.loc[0, 'Gender']) or pd.isna(df.loc[0, 'Time_5_km']):
    #     missing_info = df.loc[0, 'Info']
    #     print(f"Brakuje mi danych, opowiedz więcej o: {missing_info}")
    #     return False
    missing_info = ""
    
    if pd.isna(df.loc[0, 'Age_category']):
        missing_info += "opowiedz o swoim wieku, "
    if pd.isna(df.loc[0, 'Gender']):
        missing_info += "jaką masz płeć, "
    if pd.isna(df.loc[0, 'Time_5_km']):
        missing_info += "jak idzie Ci bieganie na 5 km, "
    
    # Jeżeli missing_info nie jest pusty, znaczy że są brakujące dane
    if missing_info:
        # Usunięcie ostatniego przecinka i spacji
        missing_info = missing_info.rstrip(', ')
        print(f"Brakuje mi danych: {missing_info}?")
        return False
    else:
        print("Wszystkie dane są obecne.")
        return True
    
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

# zapytanie do AI
df = ask_AI(user_input)
data_list = [df]
print(data_list)
df = pd.DataFrame([data.dict() for data in data_list])

while not check_AI_response(df):
    user_input = input("Napisz o sobie: ")
    df = ask_AI(user_input)
    data_list = [df]
    print(data_list)
    df = pd.DataFrame([data.dict() for data in data_list])

a=predict(df)

total_seconds = a.loc[0, 'Predicted_time_of_halfmarathon']
hours, minutes, seconds = convert_seconds(total_seconds)
print(f"{hours}h {minutes}min {seconds}sek Powodzenia w biegu!")


