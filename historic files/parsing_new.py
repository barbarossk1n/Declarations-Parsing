from libraries_1 import *
from config_1 import *


class Parsing:
    
    # Initial variables that are created during the start of the program
    def __init__(self, script_path):

        self.script_path = script_path
        self.progrm_path = self.script_path.replace('\\main_script', '')

        def check_n_create(inp_name, ch_pth):
            lst_dir = os.listdir(ch_pth)

            if inp_name not in lst_dir:
                os.chdir(ch_pth)
                os.mkdir(inp_name)

            return ch_pth + '\\' + inp_name

        self.queries = check_n_create('queries', self.progrm_path)
        self.projects = check_n_create('projects', self.progrm_path)
        
        self.pdf = check_n_create('pdf', self.projects)
        self.json = check_n_create('json', self.projects)
        if 'database.json' not in os.listdir(self.json):
            os.chdir(self.json)
            
            json_database = json.dumps({})
            with open('database.json', 'w') as outfile:
                outfile.write(json_database)
        
        self.excel = check_n_create('excel', self.projects)

        self.ser = Service(self.script_path + '\\chromedriver.exe')
        self.opt = Options()
        
    # Getting the number of lists with the projects and projects' links and ids
    def projects_links(self, url, attempt = 10, theme = None):
        
        template_link = 'https://xn--80az8a.xn--d1aqf.xn--p1ai/%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D1%8B/%D0%BA%D0%B0%D1%82%D0%B0%D0%BB%D0%BE%D0%B3-%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B5%D0%BA/%D0%BE%D0%B1%D1%8A%D0%B5%D0%BA%D1%82/'
        
        '''
        ===============================================================
        First Part
        ===============================================================
        '''
        
        # entering the name of the theme for research
        if theme == None:
            theme = input('Введите название для темы поиска: ')
            
        # change the link parameter (up to 100 projects on the page)
        if '&limit=10' in url and '&limit=100' not in url:
            main_url = url.replace('&limit=10', '&limit=100')
        
        elif '&limit=10' not in url and '&limit=100' not in url:
            main_url = url + '&limit=100'
            
        else:
            main_url = url
            
        # open browser
        def get_list_projects(url):
            driver = webdriver.Chrome(service=self.ser)
            driver.get(url)
            
            '''
            Starting parsing process consisting of the next aspects:
            - find class pagination (buttons with pages selection)
            - find the last button which will show number of pages
            '''
            
            # find pagination
            pag_break = False
            pag_time = 0
            pag = None
            
            while pag_break == False and pag_time < attempt:
                try:
                    pag = driver.find_element(By.XPATH, pagination_param)
                    pag_break = True
                    
                    print('Элемент pag найден!')
                    
                except NoSuchElementException:
                    time.sleep(1)
                    
                    pag = None
                    pag_time += 1
                    
            if pag == None:
                pag = driver
                
            # check whether there is "next" button
            try:
                nxt_but = pag.find_element(By.XPATH, next_param)
            
            except NoSuchElementException:
                nxt_but = 0
                
            # create list of the list numbers
            if nxt_but != 0:
                all_lis = pag.find_elements(By.TAG_NAME, type_next)
                numb_pg = int(all_lis[-2].text)

                self.pages = list(range(0, numb_pg))

            else:
                self.pages = [0]
                
            driver.close()
            
        list_created = False
        created_time = 0
        
        while list_created == False and created_time < attempt:
            try:
                get_list_projects(main_url)
                list_created = True
                
                print('Элемент next найден!')
                
            except StaleElementReferenceException:
                created_time += 1
                
        if list_created == False:
            print('/nНе получилось достать список проектов для выгрузки по фильтру: {}!/n'.format(theme))
            
            return None
        
        
        '''
        ===============================================================
        Second Part
        ===============================================================
        '''
        
        lnk_lst = []
        self.proj_dict = {}

        for page in self.pages:
            new_url = main_url.replace('&page=0', '&page={}'.format(page))
            
            # open browser
            driver = webdriver.Chrome(service=self.ser)
            driver.get(new_url)
            
            
            '''
            To get projects' links, it's needed to take the next actions:
            - find table containing projects
            - extract row named as link of the project and thus extract link by itself
            - extract id of the building
            - return dictionary with keys as ids and values as links
            '''
            
            # find web-table
            web_break = False
            web_time = 0
            
            while web_break == False and web_time < attempt:
                try:
                    web_table = driver.find_element(By.XPATH, table_projects)
                    web_break = True
                    
                except NoSuchElementException:
                    time.sleep(1)
                    
                    web_time += 1
                    
            if web_break == False:
                driver.close()
                
                print('На странице №{} нет информации!'.format(page))
                return None

            # find ids
            id_break = False
            id_time = 0
            
            while id_break == False and id_time < attempt:
                try:
                    span_tbl = web_table.find_elements(By.XPATH, name_container)
                    span_lst = [element.text.replace('ID: ', '') for element in span_tbl]
                    
                    id_break = True
                except NoSuchElementException:
                    time.sleep(1)
                    
                    id_time += 1
                    
            if id_break == False:
                driver.close()
                
                print('На странице №{} нет информации!'.format(page))
                return None
            
            # combine ids and links
            for i in range(len(span_lst)):
                self.proj_dict[span_lst[i]] = template_link + str(span_lst[i])
                
            driver.close()
            
        
        '''
        ===============================================================
        Third Part
        ===============================================================
        '''
            
        os.chdir(self.queries)
        
        if theme not in os.listdir(self.queries):
            prjs_dcts = theme + '.json'

            with open(prjs_dcts, "w", encoding='utf8') as outfile:
                json.dump(self.proj_dict, outfile, ensure_ascii=False)
            
        return self.proj_dict
    
    def get_declarations(self, sel_name = None, url_prjct = None, 
                                check_new = False, attempt = 2):
        
        count_old = 0
        
        '''
        ===============================================================
        First Part
        ===============================================================
        '''
        
        url_lst = []
        
        if sel_name != None:
            os.chdir(self.queries)

            try:
                with open(sel_name + '.json') as json_file:
                    data = json.load(json_file)

                for el in data:
                    url_lst.append(data[el])
                    
            except FileNotFoundError:
                print('Такого файла нет: {}!'.format(sel_name))
                return None
                
        elif url_prjct != None:
            url_lst.append(url_prjct)
            
        else:
            print('Выберите ссылку(-и) для выгрузки декларации(-ий)!')
            return None
        
        os.chdir(self.json)

        f = open('database.json')
        projects_db = json.load(f)
        
        for url_prj in url_lst:
            self.id_prj = url_prj.split('/')[-1]
            
            if self.id_prj in projects_db.keys() and self.id_prj in os.listdir(self.json):
                
                count_old += 1
                print('Проект {} старый!'.format(self.id_prj))
                
                if check_new == False:
                    continue
                    
                else:
                    new_declaration = False
                    self.lt_date = projects_db[self.id_prj]['latest_date']
            
            else:
                print('Проект {} новый!'.format(self.id_prj))
                new_declaration = True
                        
            # Open browser
            driver = webdriver.Chrome(service=self.ser)
            driver.get(url_prj)
            
            print('Усё')
            
            # if new_declaration == False:
            #     latest_break = False
            #     latest_time = 0
            #     latest_declaration = None
                
            #     while latest_break == False and latest_time < attempt:
            #         try:
            #             names_find = driver.find_elements(By.XPATH, sub_build_info)
            #             names_find = [el.text for el in names_find]
                        
            #             print(names_find)
                        
#                         found_permission = False
#                         for el in names_find:
#                             if el == 'Разрешение на ввод':
#                                 found_permission = True

#                                 break
                            
#                         if found_permission == False:
#                             latest_declaration = driver.find_element(By.XPATH, last_declar).text.split('от ')[1]
                            
            #             latest_break = True
                            
            #         except StaleElementReferenceException:
            #             time.sleep(1)
                        
            #     if latest_break == False:
            #         driver.close()
            #         print('Не удалось обновить информацию для декларации проекта {}'.format(self.id_prj))
                
            #         continue
            
            # driver.close()
                
#                 elif str(self.lt_date) == str(latest_declaration):
#                     print('Для проекта {} загружена последняя декларация'.format(self.id_prj))
                    
#                     continue
            
#             # Try to download all information about the project from its web-page
#             if check_new == True:
#                 house_rf_information = {}
            
#                 def parse_element(drvr, class_name):
#                     try:
#                         class_return = drvr.find_element(By.XPATH, class_name)

#                     except NoSuchElementException:
#                         class_return = None
                        
#                     return class_return
                
#                 def parse_elements(drvr, class_name):
#                     try:
#                         class_return = drvr.find_elements(By.XPATH, class_name)

#                     except NoSuchElementException:
#                         class_return = None
                        
#                     return class_return
                
#                 # Common information - name, adress or even date of finishing of the building
#                 house_rf_information['Базовая информация'] = {}

# # ------------->
#                 name_proj = parse_element(driver, "//h1[@class='styles__Name-sc-eng632-3 fuLxCe']")
#                 if name_proj != None:
#                     house_rf_information['Базовая информация']['Название:'] = name_proj.text
            
#                 address_proj = parse_element(driver, "//p[@class='styles__Address-sc-eng632-10 edldDl']")
#                 if address_proj != None:
#                     house_rf_information['Базовая информация']['Адрес:'] = address_proj.text.replace('Адрес: ', '')
                
#                 project_info = parse_element(driver, "//div[@class='styles__Container-sc-17wkiw0-0 juxYqm']")
#                 if project_info != None:
#                     new_info = parse_elements(project_info, "//div[@class='styles__Row-sc-13pfgqd-0 dlQqAu']")
#                     if new_info != None:
#                         lst_of_info = [el.text for el in new_info]
                    
#                         for info_el in lst_of_info:
#                             info_el = info_el.split('\n')
#                             if len(info_el) > 1:
#                                 house_rf_information['Базовая информация'][info_el[0]] = info_el[1]
                
#                 # Additional information (like ceiling hight, number of elevators and so on)
#                 main_characters = parse_element(driver, "//div[@class='styles__Wrapper-sc-2i4wxn-0 gNDvQd']")
#                 if main_characters != None:
#                     new_characters = parse_elements(main_characters, "//div[@class='styles__CharacteristicsWrapper-sc-1fyyfia-0 kheFpy']")
#                     if new_characters != None:
#                         lst_of_characters = [el.text for el in new_characters]
                    
#                         for char_el in lst_of_characters:
#                             char_el = char_el.split('\n')
                            
#                             if len(char_el) > 2:
#                                 house_rf_information[char_el[0]] = {}
                                
#                                 i = 1
#                                 while i < len(char_el):
#                                     if 'Количество грузовых' in char_el[i]:
#                                         house_rf_information[char_el[0]]['{0} {1}'.format(char_el[i], char_el[i + 1])] = char_el[i + 2]
#                                         i += 3
                                    
#                                     else:
#                                         house_rf_information[char_el[0]][char_el[i]] = char_el[i + 1]
#                                         i += 2
                
#                 # Information about indices (clearance of the air or accessibility of the vehicles) and nearest objects
#                 map_container = parse_element(driver, "//div[@class='styles__Container-sc-gha8r9-0 kHltig']")
#                 if map_container != None:
                    
#                     # Indices
#                     index_lst = parse_element(map_container, "//div[@class='styles__IndexWrapper-sc-gha8r9-1 kXiWIQ']")
#                     if index_lst != None:
#                         class_index_lst = parse_elements(index_lst, "//div[@class='styles__Wrapper-sc-1f4892z-0 fCqoiD']")
#                         if class_index_lst != None:
#                             values_index = parse_elements(index_lst, "//span[@class='styles__Value-sc-1gf1bla-1 ikjQpB']")
#                             names_index = parse_elements(index_lst, "//div[@class='styles__Title-sc-1f4892z-2 jxFQYg']")

#                             if values_index != None and names_index != None:
#                                 house_rf_information['Индексы'] = {}
                                
#                                 for i in range(len(values_index)):
#                                     try:
#                                         house_rf_information['Индексы'][names_index[i].text] = values_index[i].text
                                    
#                                     except IndexError:
#                                         continue
                                    
#                     # Nearest objects
#                     near_objects = parse_element(map_container, "//div[@class='styles__Wrapper-sc-17w8udf-0 bhlSzw']")
#                     if near_objects != None:
#                         nearest_lst = parse_elements(near_objects, "//div[@class='styles__FilterWrapper-sc-17w8udf-1 ilLAXA']")
#                         if nearest_lst != None:
#                             values_object = parse_elements(near_objects, "//span[@class='styles__CheckboxCounter-sc-11ih1xm-3 dipJaV']")
#                             names_object = parse_elements(near_objects, "//span[@class='styles__CheckboxLabel-sc-11ih1xm-2 bsXGRf']")
                            
#                             if values_object != None and names_object != None:
#                                 house_rf_information['Объекты поблизости'] = {}
                                
#                                 for i in range(len(values_object)):
#                                     try:
#                                         house_rf_information['Объекты поблизости'][names_object[i].text] = values_object[i].text
                            
#                                     except IndexError:
#                                         continue
# # ------------->

#                 for prj in os.listdir(self.json):
#                     if prj == self.id_prj:
#                         with open(self.json + '\\' + prj + '\\' + self.id_prj + '_general.json', "w", encoding='utf8') as outfile:
#                             json.dump(house_rf_information, outfile, ensure_ascii=False)
                            
#                         break
                    
#             # Finding table with declarations
#             table_break = False
#             table_time = 0
            
#             while table_break == False and table_time < attempt:
#                 try:
#                     web_table = driver.find_element(By.XPATH, table_declar)
#                     table_break = True
                    
#                 except NoSuchElementException:
#                     time.sleep(1)

#                     table_time += 1
                    
#             if table_break == False:
#                 print('Деклараций для проекта {} нет!'.format(self.id_prj))
                
#                 driver.close()
#                 continue
            
#             scrolling_break = False
#             while scrolling_break == False:
#                 try:
#                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                     time.sleep(1)

#                     try:
#                         # bttn = web_table.find_element(By.XPATH, "//button[@class='styles__LoadMore-sc-130vmhh-1 cKBFEI']")
#                         bttn = web_table.find_element(By.XPATH, button_load_more)
#                         bttn.click()
                        
#                     except NoSuchElementException:
#                         scrolling_break = True
#                         break

#                 except ElementNotInteractableException:
#                     scrolling_break = True
                    
#             # Find elements inside table as the links
#             try:
#                 # declarations_links = driver.find_elements(By.XPATH, "//div[@class='styles__Wrapper-sc-9x6nxn-2 iAZlrB soz-undefined']/a")
#                 declarations_links = driver.find_elements(By.XPATH, declaration_link)
#                 links_lst = [el.get_attribute('href') for el in declarations_links]
                
#                 # declarations_dates = driver.find_elements(By.XPATH, "//span[@class='styles__Date-sc-10m5x2s-0 gZZSdd']")
#                 declarations_dates = driver.find_elements(By.XPATH, declaration_date)
#                 dates_lst = [el.text for el in declarations_dates]
                
#                 driver.close() 
                
#             except NoSuchElementException:
#                 print('Не получилось выгрузить декларации для проекта {}'.format(self.id_prj))
                
#                 driver.close()
#                 continue
            
#             print(declarations_links)
#             print(declarations_dates)
            
            
#             '''
#             ===============================================================
#             Second Part
#             ===============================================================
#             '''
            
            
#             new_path = self.pdf + '\\' + self.id_prj + '_' + dates_lst[0]
            
#             if new_declaration == False:
#                 json_prjj = os.listdir(self.json + '\\' + self.id_prj)
                
#                 if self.id_prj + '_' + dates_lst[0] + '.json' not in json_prjj:
#                     os.rename(self.pdf + '\\' + self.id_prj + '_' + self.lt_date, new_path)
#                     time.sleep(0.1)
                    
#                     i = 0
#                     while i < len(dates_lst) and str(dates_lst[i]) != str(self.lt_date):
#                         i += 1

#                     indx_dwnld_end = i
                    
#                 else:
                    
#                     continue
                        
#             else:
#                 os.chdir(self.pdf)
#                 os.mkdir(new_path)
                
#                 os.chdir(new_path)
#                 os.mkdir('Download')
                
#                 indx_dwnld_end = len(dates_lst)
            
#             # Creating special options for the browser in order to download to this folder
#             prefs = {}
#             prefs['download.default_directory'] = new_path + '\\Download'
            
#             self.opt.add_experimental_option("prefs", prefs)
#             wbr_updated = webdriver.Chrome(service=self.ser, options=self.opt)
            
#             # Declarations downloading
#             for i in range(min(indx_dwnld_end, 24)):
#                 stop_download = False
                
#                 if i > 0 and dates_lst[i] == dates_lst[i - 1]:
#                     stop_download = True
                    
#                 try:
#                     if stop_download == False:
#                         get_link = links_lst[i]
                        
#                         wbr_updated.get(get_link)
#                         time.sleep(0.2)
                        
#                         os.chdir(self.pdf)
#                         dwnlds_lst = os.listdir(new_path + '\\Download')
                        
#                         while dwnlds_lst[0].endswith('.tmp') or dwnlds_lst[0].endswith('.crdownload'):
#                             time.sleep(0.1)
#                             dwnlds_lst = os.listdir(new_path + '\\Download')
                        
#                         os.chdir(new_path)
#                         os.chdir('Download')
#                         os.rename(dwnlds_lst[0], self.id_prj + '_' + dates_lst[i] + '.pdf')
                        
#                         shutil.move(new_path + '\\Download\\' + self.id_prj + '_' + dates_lst[i] + '.pdf', new_path)
                        
#                         if i == 0:
#                             projects_db[self.id_prj] = {}
#                             projects_db[self.id_prj]['latest_date'] = dates_lst[i]
#                             projects_db[self.id_prj]['href'] = url_prj
                            
#                             if sel_name != None:
#                                 projects_db[self.id_prj]['query'] = sel_name
                            
#                             else:
#                                 projects_db[self.id_prj]['query'] = 'unique search'
                        
#                 except IndexError:
#                     continue
            
#             os.chdir(self.json)
            
#             updated_database = json.dumps(projects_db)
#             with open('database.json', 'w') as outfile:
#                 outfile.write(updated_database)
            
#             os.chdir(new_path)
            
#             wbr_updated.close()
            
#         if sel_name != None:
#             print('Количество старых проектов: {}'.format(count_old))