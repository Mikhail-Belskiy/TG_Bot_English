from sqlalchemy.orm import sessionmaker
from models import Users, User_translation, Words, Translations
from models import create_tables
import sqlalchemy


DSN = "postgresql://postgres:Mb20041995@localhost:5432/Tg_Bot_translation"
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)  # Создаём таблицы

Session = sessionmaker(bind=engine)
session = Session()

# Создаём слова
words = [
    Words(word='Привет'),
    Words(word='Кошка'),
    Words(word='Собака'),
    Words(word='Красный'),
    Words(word='Машина')
]

# Добавляем слова в сессию
session.add_all(words)
session.commit()  # Сохраняем слова, чтобы получить их ID

# Получаем последние добавленные слова
word_1_id = words[0].id
word_2_id = words[1].id
word_3_id = words[2].id
word_4_id = words[3].id
word_5_id = words[4].id

# Создаём переводы word_id
translations = [
    Translations(word_id=word_1_id, translation='hello', is_primary=True),
    Translations(word_id=word_1_id, translation='world', is_primary=False),
    Translations(word_id=word_1_id, translation='peace', is_primary=False),
    Translations(word_id=word_1_id, translation='cat', is_primary=False),
    Translations(word_id=word_2_id, translation='cat', is_primary=True),
    Translations(word_id=word_2_id, translation='machine', is_primary=False),
    Translations(word_id=word_2_id, translation='vehicle', is_primary=False),
    Translations(word_id=word_2_id, translation='dog', is_primary=False),
    Translations(word_id=word_3_id, translation='dog', is_primary=True),
    Translations(word_id=word_3_id, translation='mouse', is_primary=False),
    Translations(word_id=word_3_id, translation='snake', is_primary=False),
    Translations(word_id=word_3_id, translation='cat', is_primary=False),
    Translations(word_id=word_4_id, translation='red', is_primary=True),
    Translations(word_id=word_4_id, translation='yellow', is_primary=False),
    Translations(word_id=word_4_id, translation='blue', is_primary=False),
    Translations(word_id=word_4_id, translation='green', is_primary=False),
    Translations(word_id=word_5_id, translation='car', is_primary=True),
    Translations(word_id=word_5_id, translation='machine', is_primary=False),
    Translations(word_id=word_5_id, translation='vehicle', is_primary=False),
    Translations(word_id=word_5_id, translation='dog', is_primary=False),
]

# Добавляем переводы в сессию
session.add_all(translations)
session.commit()  # Сохраняем все переводы

# Закрываем сессию
session.close()