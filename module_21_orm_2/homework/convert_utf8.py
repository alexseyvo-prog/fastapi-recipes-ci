# Конвертация файла
with open('students.csv', 'r', encoding='windows-1251') as f:
    content = f.read()

with open('students_utf8.csv', 'w', encoding='utf-8') as f:
    f.write(content)

print('Файл сконвертирован в students_utf8.csv')