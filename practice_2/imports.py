from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date
import re
import time
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC