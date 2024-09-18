import pandas as pd
import ast

def process_analysis(analysis_str):
    try:
        analysis_list = ast.literal_eval(analysis_str)
        if len(analysis_list) >= 3:
            return analysis_list[0], analysis_list[1], analysis_list[2], analysis_list[3]
        else:
            return analysis_list[0] if len(analysis_list) > 0 else "", \
                   analysis_list[1] if len(analysis_list) > 1 else "", \
                   analysis_list[1] if len(analysis_list) > 2 else "", \
                   analysis_list[2] if len(analysis_list) > 3 else ""
    except:
        return "", "", "", ""

# Чтение CSV файла
df = pd.read_csv('results/enreport/2024-08-20/search_results_analysed.csv')

# Применение функции process_analysis к столбцу 'analysis'
df[['Company', 'Signal', 'Time', 'Summary']] = df['analysis'].apply(process_analysis).apply(pd.Series)

# Сохранение результата в Excel файл
df.to_excel('enreport1.xlsx', index=False)

print("Обработка завершена. Результат сохранен в файл 'enreport1.xlsx'.")