import os
from dotenv import load_dotenv
import asyncio
import aiohttp
import asyncpg
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import time
from datetime import date, datetime
import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Optional, Dict
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
import requests
import psycopg2
import xlrd
import time
