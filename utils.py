def validate_input(prompt, validator):
    while True:
        user_input = input(prompt)
        if validator(user_input):
            return user_input
        else:
            print("Geçersiz giriş! Lütfen tekrar deneyin.")

# Örnek bir doğrulama fonksiyonu
def is_positive_integer(input_str):
    try:
        return int(input_str) > 0
    except ValueError:
        return False