
'''
Работа с директорией
================================================================
'''
import os
import glob
import shutil
import sys

os.environ["JAVA_HOME"] ="C:\Program Files\Java\jdk-21"

import csv
import json


'''
Библиотеки для парсинга
================================================================
'''
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.common.exceptions import *

from urllib import request

from bs4 import BeautifulSoup as bs


# '''
# Библиотеки для работы с пдф-файлами
# ================================================================
# '''
# import pdfplumber
# import pdfminer
# from pdfminer.pdfparser import *


# '''
# Прочие библиотеки
# ================================================================
# '''
# import time
# from datetime import datetime

# import pandas as pd
# import numpy as np

# from collections import Counter

# import difflib
