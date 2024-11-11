import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = sq.Column(sq.Integer, primary_key=True)
    telegram_id = sq.Column(sq.String(length=50), unique=True, nullable=False)

class Words(Base):
    __tablename__ = 'words'

    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=30), unique = True, nullable=False)

    def __str__(self):
        return f'{self.word}'

class Translations(Base):
    __tablename__ = 'translations'
    id = sq.Column(sq.Integer, primary_key=True)
    word_id = (sq.Column(sq.Integer, sq.ForeignKey('words.id')))
    translation = sq.Column(sq.String(length=30),nullable=False) #unique = False
    is_primary = sq.Column(sq.BOOLEAN, nullable=True)

    def __str__(self):
        return f'{self.translation}'

class User_translation(Base):
    __tablename__ = 'user_words'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))
    translation_id = sq.Column(sq.Integer, sq.ForeignKey('translations.id'))

def create_tables(engine):
    Base.metadata.drop_all(engine)  # Удалить все таблицы
    Base.metadata.create_all(engine)




