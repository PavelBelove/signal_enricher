import pandas as pd

# Список ключевых слов для фильтрации
keywords = [
    "Brand", "Revenue", "Growth", "Legal", "Financial", "Risk", "CCO",
    "Experience", "Distribution", "Robotics", "CFO", "Sales", "CMO", "CRO"
]

# Функция для проверки, содержит ли строка любое из ключевых слов
def contains_keyword(text):
    return any(keyword.lower() in str(text).lower() for keyword in keywords)

# Чтение Excel файла
input_file = 'Crunch_apolo/input.xlsx'  # Замените на имя вашего входного файла
df = pd.read_excel(input_file)

# Фильтрация данных
filtered_df = df[~df['Title'].apply(contains_keyword)]

# Сохранение отфильтрованных данных в новый Excel файл
output_file = 'Crunch_apolo/output_filtered.xlsx'
filtered_df.to_excel(output_file, index=False)

print(f"Отфильтрованные данные сохранены в файл: {output_file}")