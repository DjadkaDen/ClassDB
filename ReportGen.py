from sqlalchemy import create_engine
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font

class ExcelReportGenerator:
    def __init__(self, db_type, db_api, host, user, password, database, port):
        self.connection_string = f'{db_type}+{db_api}://{user}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(self.connection_string)

    def fetch_data(self, query):
        """Выгрузка данных из базы данных."""
        return pd.read_sql(query, self.engine)

    def save_to_excel(self, data, output_file):
        """Сохранение данных в Excel с динамическими фильтрами и закрепленной областью."""
        wb = Workbook()
        ws = wb.active

        # Добавление заголовков
        for r in dataframe_to_rows(data, index=False, header=True):
            ws.append(r)

        # Применение стилей к заголовкам
        for cell in ws[1]:  # Заголовки находятся в первой строке
            cell.font = Font(bold=True)

        # Добавление динамических фильтров
        ws.auto_filter.ref = ws.dimensions

        # Закрепление области по ячейке B2
        ws.freeze_panes = 'B2'

        # Сохранение файла
        wb.save(output_file)

# Пример вызова класса
if __name__ == "__main__":
    # Замените параметры на свои
    report_generator = ExcelReportGenerator(
        db_type='postgresql',
        db_api='psycopg2',
        host='192.168.86.222',
        user='classuser',
        password='ClassUser',
        database='class_db',
        port='5432'
    )


    # Запрос для выгрузки данных
    query = 'SELECT * FROM fact'
    
    # Получение данных
    data = report_generator.fetch_data(query)

    # Сохранение данных в Excel
    output_file = 'report_with_filters.xlsx'
    report_generator.save_to_excel(data, output_file)

    print(f"Отчет сохранен в файл: {output_file}")
