from config import *

# Конфигурация
BASE_URL = BASE_URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME2}"
DOWNLOAD_DIR = "bulletins"
START_DATE = date(2023, 1, 1)

# Инициализация SQLAlchemy
Base = declarative_base()


class TradingResult(Base):
    __tablename__ = 'trading_results'

    id = Column(Integer, primary_key=True)
    exchange_product_id = Column(String(20), nullable=False)
    exchange_product_name = Column(String(255), nullable=False)
    oil_id = Column(String(10), nullable=False)
    delivery_basis_id = Column(String(10), nullable=False)
    delivery_basis_name = Column(String(255), nullable=False)
    delivery_type_id = Column(String(10), nullable=False)
    volume = Column(Numeric(20, 2))
    total = Column(Numeric(20, 2))
    count = Column(Integer, nullable=False)
    trade_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default='now()')
    updated_at = Column(DateTime, server_default='now()', onupdate='now()')

    __table_args__ = (
        UniqueConstraint('exchange_product_id', 'trade_date', name='unique_trade_record'),
    )


class BulletinParser:
    def __init__(self):
        self.base_url = "https://spimex.com"
        self.trade_section_url = "/markets/oil_products/trades/results/"
        self.start_date = date(2023, 1, 1)
        self.driver = None
        self.engine = None
        self.Session = None

        # Настройка драйвера и БД
        self.setup_driver()
        self.setup_database()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def setup_database(self):
        self.engine = create_engine(DB_URL)
        self.Session = sessionmaker(bind=self.engine)

        # Создаем таблицы, если они не существуют
        Base.metadata.create_all(self.engine)

    def get_bulletin_links(self, page_num: int) -> List[dict]:
        try:
            url = f"{self.base_url}{self.trade_section_url}?page=page-{page_num}"
            print(f"Переход на страницу {page_num}: {url}")

            self.driver.get(url)
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='trades/results']"))
            )

            # Даем время для загрузки контента
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Ищем все ссылки на бюллетени (xls файлы)
            bulletins = []
            for item in soup.find_all(string=re.compile(r'Бюллетень по итогам торгов в Секции «Нефтепродукты»')):
                if not item.strip():
                    continue

                # Находим родительский элемент со ссылкой
                parent = item.find_parent()
                link = parent.get("href") if parent else None

                date_match = re.search(r'(\d{8})', link)
                if not date_match:
                    continue

                trade_date = datetime.strptime(date_match.group(1), '%Y%m%d').date()

                if link:
                    bulletins.append({
                        'url': urljoin(BASE_URL, link),
                        'date': datetime.strptime(trade_date.strftime('%d%m%Y'), '%d%m%Y').date(),
                        'filename': f"oil_products_{trade_date}.xls"
                    })

            return bulletins

        except Exception as e:
            print(f"Ошибка при получении списка бюллетеней: {str(e)}")
            return []

    def get_all_bulletin_links(self) -> List[dict]:
        all_bulletins = []
        current_page = 1
        last_date = date.today()

        while last_date >= self.start_date:
            page_bulletins = self.get_bulletin_links(current_page)
            if not page_bulletins:
                break

            all_bulletins.extend(page_bulletins)
            last_date = page_bulletins[-1]['date']

            print(f"Страница {current_page}, последняя дата: {last_date}")

            # Проверяем, не вышли ли мы за пределы 2023 года
            if last_date < self.start_date:
                break

            current_page += 1

        # Фильтруем только бюллетени начиная с 2023 года
        filtered_bulletins = [b for b in all_bulletins if b['date'] >= self.start_date]
        print(f"Найдено {len(filtered_bulletins)} бюллетеней с {self.start_date}")
        return filtered_bulletins

    def download_bulletin(self, bulletin_info: dict) -> Optional[str]:
        try:
            # Используем requests для скачивания файла

            session = requests.Session()
            session.headers.update({'User-Agent': 'Mozilla/5.0'})

            response = session.get(bulletin_info['url'], stream=True)
            response.raise_for_status()

            # Сохраняем файл
            filename = f"oil_products_{bulletin_info['date'].strftime('%Y%m%d')}.xls"
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            return filename

        except Exception as e:
            print(f"Ошибка при скачивании бюллетеня за {bulletin_info['date']}: {str(e)}")
            return None

    def parse_bulletin(self, filepath: str, trade_date: date) -> Optional[pd.DataFrame]:
        try:
            # Читаем Excel файл
            xls = pd.ExcelFile(filepath)

            # Проверяем наличие листа TRADE_SUMMARY
            if 'TRADE_SUMMARY' not in xls.sheet_names:
                print(f"Лист TRADE_SUMMARY не найден в файле {filepath}")
                return None

            # Читаем весь лист для поиска даты и данных
            df_raw = pd.read_excel(filepath, sheet_name='TRADE_SUMMARY', header=None)

            # Ищем дату торгов
            trade_date = None
            for i, row in df_raw.iterrows():
                if "Дата торгов:" in str(row.values):
                    date_match = re.search(r'\d{2}\.\d{2}\.\d{4}', str(row.values))
                    if date_match:
                        trade_date = datetime.strptime(date_match.group(), '%d.%m.%Y').date()
                    break

            if not trade_date:
                print(f"Не удалось определить дату торгов в файле {filepath}")
                return None

            start_row = None
            metric_ton_found = False
            for i, row in df_raw.iterrows():
                row_str = str(row.values)

                if "Единица измерения: Метрическая тонна" in row_str:
                    metric_ton_found = True
                    continue

                if metric_ton_found and "Цена (за единицу измерения), руб." in row_str:
                    start_row = i
                    break

            if start_row is None:
                print(f"Не найдена таблица с метрическими тоннами в файле {filepath}")
                return None

            # Читаем таблицу с данными
            df = pd.read_excel(
                filepath,
                sheet_name='TRADE_SUMMARY',
                header=start_row,
                skipfooter=2  # Пропускаем итоговые строки
            )
            # Очищаем заголовки от лишних пробелов и символов
            df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]

            # Сопоставляем столбцы с нужными нам полями
            column_mapping = {
                'Код Инструмента': 'exchange_product_id',
                'Наименование Инструмента': 'exchange_product_name',
                'Базис поставки': 'delivery_basis_name',
                'Объем Договоров в единицах измерения': 'volume',
                'Объем Договоров, руб.': 'total',
                'Обьем Договоров, руб.': 'total',
                'Количество Договоров, шт.': 'count'
            }

            # Переименовываем столбцы по шаблону
            renamed_columns = {}
            for col in df.columns:
                for pattern, new_name in column_mapping.items():
                    if pattern in col:
                        renamed_columns[col] = new_name
                        break

            # Проверяем, что нашли все нужные столбцы
            if len(renamed_columns) + 1 < len(column_mapping):
                missing = set(column_mapping.values()) - set(renamed_columns.values())
                print(f"В файле {filepath} отсутствуют столбцы: {missing}")
                return None

            df = df.rename(columns=renamed_columns)

            # Преобразуем числовые колонки и заменяем прочерки на NaN
            numeric_cols = ['volume', 'total', 'count']
            for col in numeric_cols:
                if col in df.columns:
                    # Заменяем прочерки и пустые строки на NaN
                    df[col] = df[col].replace(['-', ''], pd.NA)
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Фильтруем строки с count > 0 (не пустые и не нулевые)
            if 'count' not in df.columns:
                print(f"В файле {filepath} отсутствует столбец count")
                return None

            df = df[df['count'].notna() & (df['count'] > 0)].copy()

            # Добавляем дополнительные поля
            a = df.iloc[:, 1]
            df['oil_id'] = a.str[:4]
            df['delivery_basis_id'] = a.str[4:7]
            df['delivery_type_id'] = a.str[-1]
            df['trade_date'] = trade_date

            # Выбираем только нужные колонки
            result_cols = [
                'exchange_product_id', 'exchange_product_name', 'oil_id',
                'delivery_basis_id', 'delivery_basis_name', 'delivery_type_id',
                'volume', 'total', 'count', 'trade_date'
            ]

            # Проверяем наличие всех колонок
            available_cols = [col for col in result_cols if col in df.columns]
            if len(available_cols) != len(result_cols):
                missing = set(result_cols) - set(df.columns)
                print(f"В данных отсутствуют колонки: {missing}")
                return None

            df = df[df['delivery_basis_name'].notna()]

            return df[result_cols]

        except Exception as e:
            print(f"Ошибка при парсинге файла {filepath}: {str(e)}")
            return None

    def save_to_db(self, df: pd.DataFrame):
        if df is None or df.empty:
            return

        session = self.Session()
        try:
            records = df.to_dict('records')
            for record in records:
                # Проверяем существование записи
                exists = session.query(TradingResult).filter(
                    TradingResult.exchange_product_id == record['exchange_product_id'],
                    TradingResult.trade_date == record['trade_date']
                ).first()

                if not exists:
                    session.add(TradingResult(**record))

            session.commit()
            print(f"Добавлено {len(records)} записей за {records[0]['trade_date']}")

        except Exception as e:
            session.rollback()
            print(f"Ошибка при сохранении в базу данных: {str(e)}")
        finally:
            session.close()

    def process_all_bulletins(self):
        current_page = 1
        processed_count = 0
        stop_processing = False

        while not stop_processing:
            bulletins = self.get_all_bulletin_links()
            if not bulletins:
                break

            # Проверяем, не вышли ли за пределы 2023 года
            last_date = bulletins[-1]['date']
            if last_date < self.start_date:
                break

            for bulletin in bulletins:
                if bulletin['date'] < self.start_date:
                    print(f"Достигнута дата {bulletin['date']} - завершение обработки")
                    stop_processing = True
                    break

                filepath = self.download_bulletin(bulletin)
                if not filepath:
                    continue

                df = self.parse_bulletin(filepath, bulletin['date'])
                if df is not None and not df.empty:
                    self.save_to_db(df)
                    processed_count += len(df)

                # Удаляем временный файл
                if os.path.exists(filepath):
                    os.remove(filepath)

                time.sleep(1)

            current_page += 1

            if bulletins[-1]['date'] <= date(2023, 1, 9):
                print("Достигнута последняя таблица (09.01.2023) - завершение обработки")
                break

        self.driver.quit()
        print(f"Обработка завершена. Всего обработано {processed_count} записей")

    def run(self):
        self.process_all_bulletins()
        print("Обработка данных завершена")


if __name__ == "__main__":
    parser = BulletinParser()
    parser.run()
