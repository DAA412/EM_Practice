from config import *

Base = declarative_base()

# Подключение к PostgreSQL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME1}"
engine = create_engine(DATABASE_URL)


class Genre(Base):
    __tablename__ = 'genre'

    genre_id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)

    books = relationship('Book', back_populates='genre')


class Author(Base):
    __tablename__ = 'author'

    author_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    books = relationship('Book', back_populates='author')


class Book(Base):
    __tablename__ = 'book'

    book_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    price = Column(Numeric(8, 2), nullable=False)
    amount = Column(Integer, nullable=False, default=0)

    genre_id = Column(Integer, ForeignKey('genre.genre_id'))
    author_id = Column(Integer, ForeignKey('author.author_id'))

    genre = relationship('Genre', back_populates='books')
    author = relationship('Author', back_populates='books')
    buy_books = relationship('BuyBook', back_populates='book')


class City(Base):
    __tablename__ = 'city'

    city_id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    delivery_time = Column(Integer, comment='Время доставки в днях')

    clients = relationship('Client', back_populates='city')


class Client(Base):
    __tablename__ = 'client'

    client_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)

    city_id = Column(Integer, ForeignKey('city.city_id'))

    city = relationship('City', back_populates='clients')
    buys = relationship('Buy', back_populates='client')


class Buy(Base):
    __tablename__ = 'buy'

    buy_id = Column(Integer, primary_key=True)
    notes = Column(String(200), comment='Пожелания покупателя')

    client_id = Column(Integer, ForeignKey('client.client_id'))

    client = relationship('Client', back_populates='buys')
    buy_books = relationship('BuyBook', back_populates='buy')
    buy_steps = relationship('BuyStep', back_populates='buy')


class BuyBook(Base):
    __tablename__ = 'buy_book'

    buy_book_id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False, default=1)

    buy_id = Column(Integer, ForeignKey('buy.buy_id'))
    book_id = Column(Integer, ForeignKey('book.book_id'))

    buy = relationship('Buy', back_populates='buy_books')
    book = relationship('Book', back_populates='buy_books')


class Step(Base):
    __tablename__ = 'step'

    step_id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)

    buy_steps = relationship('BuyStep', back_populates='step')


class BuyStep(Base):
    __tablename__ = 'buy_step'

    buy_step_id = Column(Integer, primary_key=True)
    date_start = Column(Date)
    date_end = Column(Date)

    buy_id = Column(Integer, ForeignKey('buy.buy_id'))
    step_id = Column(Integer, ForeignKey('step.step_id'))

    buy = relationship('Buy', back_populates='buy_steps')
    step = relationship('Step', back_populates='buy_steps')


# Session = sessionmaker(bind=engine)

# Создание таблиц
Base.metadata.create_all(engine)