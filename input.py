# Zapytaj użytkownika o dane
input_value = input("Napisz o sobie: ")

# Funkcja do edytowania poprzedniego inputu
def edit_previous_input(input_value):
    print(f"Poprzedni input: {input_value}")
    new_input = input(f"Jeśli chcesz, możesz go edytować lub dopisać (pozostaw puste, by nie zmieniać): ")
    
    # Jeśli nowy input jest pusty, nie zmieniamy poprzedniego inputu
    if new_input.strip() != "":
        input_value = new_input  # Zmieniamy input na nowy
    else:
        print("Nie dokonano zmian.")
    
    return input_value

# Wywołanie funkcji
input_value = edit_previous_input(input_value)

# Wypisanie finalnego inputu
print(f"Ostateczny input: {input_value}")

# Możesz teraz używać tej wartości w dalszej części programu
