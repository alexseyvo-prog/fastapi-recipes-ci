from logging_tree import format
from logging_config import configure_logging

def main():
    # Настраиваем логирование так же, как в приложении
    configure_logging()

    # Строим описание дерева логгеров
    tree_text = format.build_description()

    # Записываем в файл
    with open('logging_tree.txt', 'w', encoding='utf-8') as f:
        f.write(tree_text)

if __name__ == '__main__':
    main()