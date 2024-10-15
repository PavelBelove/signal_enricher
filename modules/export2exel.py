import pandas as pd
import ast
import re

def clean_analysis_string(analysis_str):
    """
    Очищает строку анализа от лишних символов и возвращает очищенный список данных.
    """
    # Логируем оригинальную строку
    print(f"Оригинальная строка: {analysis_str}")

    # Убираем обрамляющие символы типа "```python" и другие
    cleaned_str = re.sub(r'```python|```', '', analysis_str).strip()  # Удаляем обрамляющий текст ```python```
    
    # Логируем очищенную строку
    print(f"Очищенная строка: {cleaned_str}")
    return cleaned_str

def process_analysis(analysis_str):
    try:
        # Очищаем строку и преобразуем её в список
        cleaned_str = clean_analysis_string(analysis_str)
        
        # Попытка конвертации очищенной строки в список
        analysis_list = ast.literal_eval(cleaned_str)

        # Логируем результат преобразования
        print(f"Преобразованный список: {analysis_list}")

        # Проверка на вложенные списки и обработка их
        def clean_element(element):
            if isinstance(element, list):
                return ', '.join(map(str, element)) if element else "N/A"
            return element

        # Обрабатываем список с учетом вложенных элементов и пустых значений
        analysis_list = [clean_element(item) for item in analysis_list]

        # Проверяем длину списка и заполняем данные в зависимости от длины
        if len(analysis_list) >= 6:
            return analysis_list[0], analysis_list[1], analysis_list[2], analysis_list[3], analysis_list[4], analysis_list[5]
        else:
            return analysis_list[0] if len(analysis_list) > 0 else "", \
                   analysis_list[1] if len(analysis_list) > 1 else "", \
                   analysis_list[2] if len(analysis_list) > 2 else "", \
                   analysis_list[3] if len(analysis_list) > 3 else "", \
                   analysis_list[4] if len(analysis_list) > 4 else "", \
                   analysis_list[5] if len(analysis_list) > 5 else ""
    except Exception as e:
        # Логируем возможную ошибку и возвращаем пустые значения
        print(f"Ошибка при обработке анализа: {str(e)}")
        return "", "", "", "", "", ""

# Чтение CSV файла
df = pd.read_csv('results/ALBI/2024-10-02/search_results_analysed.csv')

# Логируем размер исходного DataFrame
print(f"Размер DataFrame до обработки: {df.shape}")

# Применение функции process_analysis к столбцу 'analysis'
df[['Company', 'Signal', 'Time', 'Summary', 'Details1', 'Details2']] = df['analysis'].apply(process_analysis).apply(pd.Series)

# Логируем результат обработки
print(df[['Company', 'Signal', 'Time', 'Summary', 'Details1', 'Details2']].head())

# Сохранение результата в Excel файл
df.to_excel('results/ALBI/2024-10-02/ALBI_2024-10-02.xlsx', index=False)

print("Обработка завершена. Результат сохранен в файл 'results/ALBI/2024-10-02/ALBI_2024-10-02.xlsx'.")
