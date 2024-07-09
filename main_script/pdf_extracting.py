from main import *
from config import *


class PdfExtracting:
    
    # Initial variables 
    def __init__(self, script_path):
        self.pdf_directory = script_path.replace('\\main_script', '\\projects\\pdf')
        self.jsn_directory = script_path.replace('\\main_script', '\\projects\\json')
        self.xls_directory = script_path.replace('\\main_script', '\\projects\\excel')

    # Getting information about the project
    def project_work(self, project_id):
        
        # -------------------------------
        check_exists = False
        
        lst_pdf = os.listdir(self.pdf_directory)
        for prjjj in lst_pdf:
            if prjjj.startswith(project_id + '_'):
                project_pdfs = self.pdf_directory + '\\' + prjjj
                print(project_pdfs)
                
                check_exists = True
                
                break
        
        if check_exists == False:
            return None
        
        project_id_no_date = project_id
        project_jsons = self.jsn_directory + '\\' + project_id_no_date
        
        # -------------------------------
        if project_id_no_date not in os.listdir(self.jsn_directory):
            os.chdir(self.jsn_directory)
            os.mkdir(project_id_no_date)
            
            print('================================================================================================================')
            print('Проекта {} не было в списке!'.format(project_id_no_date))
            print('================================================================================================================\n')
            
        else:
            print('================================================================================================================')
            print('Проект {} есть в списке!'.format(project_id_no_date))
            print('================================================================================================================\n')
            
        # -------------------------------
        try:
            os.chdir(project_pdfs)
            list_declarations = os.listdir()

        except FileNotFoundError:
            print('================================================================================================================')
            print('У проекта {} отсутствуют декларации!'.format(project_id_no_date))
            print('================================================================================================================\n')

            return None
            
        # -------------------------------
        def format_text(text_block):
            formatted_text = ''
            for index, char in enumerate(text_block):
                if char != ' ' and index % 2 == 0:
                    continue
                formatted_text += char
            
            test_text = ''
            for char in formatted_text:
                if char != ' ':
                    test_text += char * 2
                else:
                    test_text += char
            
            if test_text == text_block:
                return formatted_text
            
            return text_block

        # -------------------------------
        def state_search(table, data_json, new_project, object_parameters):
            final_phrase = None
            
            for text_blocks in table:
                len_block = len(text_blocks)
                
                for block in text_blocks:
                    for key in object_parameters:
                        try:
                            if block.startswith(key) and not block.startswith(key + '.'):
                                strt = False
                                
                                for add_value in range(10):
                                    if  block.startswith(key + str(add_value)):
                                        strt = True
                                        
                                if strt == False:
                                    index_state = text_blocks.index(block)
                                    
                                    if index_state < len_block - 1:
                                        if text_blocks[index_state + 1] == None:
                                            if index_state < len_block - 2:
                                                index_value = index_state + 2
                                            
                                            else:
                                                index_value = -100
                                        
                                        else:
                                            index_value = index_state + 1
                                        
                                        if index_value > 0:
                                            try:
                                                try:
                                                    if text_blocks[index_value][-1] == ':':
                                                        if index_state < len_block - 3:
                                                            index_value = index_state + 3
                                                        
                                                        else:
                                                            final_phrase = key + ' ' + difflib.get_close_matches(
                                                                                                text_blocks[index_value].replace('\u200b', '').replace('\n', ' ') + ':', 
                                                                                                object_parameters[key],
                                                                                                cutoff = 0.8
                                                                                            )[0]
                                                            
                                                except IndexError:
                                                    final_phrase = key + ' ' + text_blocks[index_value]
                                                    
                                                    final_val = '[null]'
                                                    index_value = -100
                                                        
                                                if index_value > 0:
                                                    if ':' in text_blocks[index_value]:
                                                        raw_divis = text_blocks[index_value].replace('\u200b', '').replace('\n', ' ').split(':')
                                                        raw_value = raw_divis[1:]
                                                        
                                                        try:
                                                            final_phrase = key + ' ' + difflib.get_close_matches(
                                                                                                raw_divis[0].replace('\u200b', '').replace('\n', ' ') + ':', 
                                                                                                object_parameters[key],
                                                                                                cutoff = 0.8
                                                                                            )[0]
                                                        except IndexError:
                                                            final_phrase = key + ' ' + text_blocks[index_value].replace('\u200b', '').replace('\n', ' ')
                                                        
                                                        if len(raw_value) > 1:
                                                            raw_value = ':'.join(raw_value)
                                                        
                                                        else:
                                                            raw_value = raw_value[0]
                                                        
                                                        raw_value = raw_value.replace('\n', '').replace('\u200b', '')
                                                        final_val = format_text(raw_value).lstrip(' ')
                                                        
                                                    else:
                                                        final_phrase = key + ' ' + text_blocks[index_value].replace('\u200b', '').replace('\n', ' ')
                                                        final_val = '[null]'
                                            
                                            except TypeError:
                                                final_phrase = key + ' ' + object_parameters[key][0]
                                                final_val = '[null]'
                                                
                                        else:
                                            try:
                                                final_phrase = key + ' ' + difflib.get_close_matches(
                                                                                            text_blocks[index_value].replace('\u200b', '').replace('\n', ' ') + ':', 
                                                                                            object_parameters[key],
                                                                                            cutoff = 0.8
                                                                                        )[0]
                                            
                                            except IndexError:
                                                final_phrase = key + ' ' + object_parameters[key][0]
                                            
                                            final_val = '[null]'
                                    
                                    else:
                                        final_phrase = key + ' ' + object_parameters[key][0]
                                        final_val = '[null]'
                                    
                                    if final_phrase != None:
                                        print(final_phrase + ' ' + format_text(final_val).lstrip(' '))
                                        
                                        if final_phrase in data_json[new_project].keys():
                                            data_json[new_project][final_phrase].append(format_text(final_val).lstrip(' '))
                                        
                                        else:
                                            data_json[new_project][final_phrase] = [format_text(final_val).lstrip(' ')]
                            
                        except AttributeError:
                            continue

            return data_json

        # -------------------------------
        def pdf_extract(declaration):
            new_declaration = False
            
            lst_jsons = os.listdir(project_jsons)
            
            print('------------------------------- Декларация: {} -------------------------------'.format(declaration))
            name_json = declaration.replace('pdf', 'json')
            data_json = {}
            
            if name_json not in lst_jsons:
                new_declaration = True
                
                os.chdir(project_pdfs)
                
                with pdfplumber.open(declaration) as pdf:
                    new_project = 'None'
                    
                    for page in range(len(pdf.pages)):
                        text_blocks = pdf.pages[page].extract_text().split('\n')
                        
                        for i in range(len(text_blocks)):
                            if ('ООббъъеекктт №№' in text_blocks[i] or 'Объект №' in text_blocks[i]):
                                if i <= len(text_blocks) - 2:
                                    if ('10 О виде договора' in text_blocks[i + 1].replace('\u200b', '')):
                                        new_project = format_text(text_blocks[i])
                                
                                elif page < len(pdf.pages) - 1:
                                    if ('10 О виде договора' in pdf.pages[page + 1].extract_text().split('\n')[0].replace('\u200b', '')):
                                        new_project = format_text(text_blocks[i])
                            
                        if (new_project != 'None'):
                            if new_project not in data_json:
                                print()
                                print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz {} zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'.format(new_project))
                                
                                data_json[new_project] = {}
                            
                            table = pdf.pages[page].extract_table()
                            if table:
                                data_json = state_search(table, data_json, new_project, object_parameters)
                                
                        else:
                            if 'Total' not in data_json:
                                data_json['Total'] = {}
                                
                            table = pdf.pages[page].extract_table()
                            if table:
                                data_json = state_search(table, data_json, 'Total', begin_params)
                                
                    os.chdir(project_jsons)
                            
                    with open(name_json, "w", encoding='utf8') as outfile:
                        json.dump(data_json, outfile, ensure_ascii=False)
                    
                    print(data_json)
            
            else:
                print('Уже есть в списке прогруженных деклараций!')

            print('\n\n')
            
            return new_declaration

        # -------------------------------
        for declaration in list_declarations:
            if 'obj' not in declaration and declaration != 'Download' and declaration != project_id_no_date + '_general.json':
                try:
                    pdf_extract(declaration)

                except PDFSyntaxError:
                    continue
            
            elif declaration == project_id_no_date + '_general.json':
                if project_id_no_date + '_general.json' in os.listdir(self.jsn_directory + '\\' + project_id_no_date):
                    os.remove(self.jsn_directory + '\\' + project_id_no_date + '_general.json')

                shutil.move(self.pdf_directory + '\\' + project_id + '\\' + project_id_no_date + '_general.json', self.jsn_directory + '\\' + project_id_no_date)
            
    # Creating excel file for the certain project
    def excel_creation(self, test_project, basic_dummy=True):
        
        def format_text(text_block):
            formatted_text = ''
            for index, char in enumerate(text_block):
                if char != ' ' and index % 2 == 0:
                    continue
                formatted_text += char
            
            test_text = ''
            for char in formatted_text:
                if char != ' ':
                    test_text += char * 2
                else:
                    test_text += char
            
            if test_text == text_block:
                return formatted_text
            
            return text_block
    
        def check_value(parameter, string):
            if parameter in string:
                split_string = string.split(parameter + ':')
                if len(split_string) > 1:
                    return (1, split_string[1].lstrip(' '))

            return (0, string)

        name = test_project + '.xlsx'

        project_name = self.jsn_directory + '\\' + test_project
        listing_name = os.listdir(project_name)
        
        os.chdir(project_name)

        dates_dictionary = {}

        for json_declar in listing_name:
            print('------------------------------------------ {} ------------------------------------------'.format(json_declar))

            # ======================================================================
    
            if not json_declar.endswith('.json'):
                continue
            
            else:
                
                # ======================================================================
                
                if json_declar == test_project + '_general.json':
                    f = open(json_declar, encoding='utf8')
                    json_read = json.load(f)
                    
                    dict_to_table = {'Базовая информация': ['ID Проекта'], 'Значение параметра': [test_project]}
                    
                    for key in json_read:
                        dict_to_table['Базовая информация'] = dict_to_table['Базовая информация'] + [sub_key for sub_key in json_read[key].keys()]
                        dict_to_table['Значение параметра'] = dict_to_table['Значение параметра'] + [sub_val for sub_val in json_read[key].values()]
                    
                    if basic_dummy == True:
                        basic_table = pd.DataFrame.from_dict(dict_to_table)
                    
                # ======================================================================
                    
                else:
                    json_read = pd.read_json(json_declar, orient='index').T
                    json_read
                
                    lst_tbls = {}
                    
                    date_declar = json_declar.split('_')[1].split('.json')[0]
                    lst_tbls[date_declar] = {}
                    
                    json_read = pd.read_json(json_declar, orient='index').T
                    
                    columns_json = json_read.columns
                    number_of_objects = len(columns_json) - 1

                    # ======================================================================
                
                    begin_dict = {}
                    
                    total = columns_json[0]
                    tbl_total = json_read[total]
                    
                    new_total = tbl_total.to_frame().dropna()
                    new_total = new_total.rename(columns={total: date_declar}).T
                    
                    for begin_key in begin_params:
                        for column in new_total.columns:
                            if column.startswith(begin_key):
                                
                                if begin_key in exceptions:
                                    new_phrase = begin_key + ' ' + exceptions[begin_key]
                                    
                                    raw_value = list(new_total[column])[0]
                                    formt_value = format_text(raw_value[0].replace('\u200b', '').replace('\n', ' '))
                                    final_value = formt_value.replace('м2', '').rstrip(' ')
                                                
                                    try:    
                                        final_value = str(float(final_value.replace(',', '.').replace(' ', '')))
                                    
                                    except ValueError:
                                        pass
                                    
                                    if new_phrase in begin_dict:
                                        begin_dict[new_phrase].append(final_value)
                                    
                                    else:
                                        begin_dict[new_phrase] = [final_value]
                                
                                else:
                                    phrase = column.split(begin_key)[1].lstrip(' ')

                                    if begin_key in begin_exceptions:
                                        try:
                                            new_phrase = difflib.get_close_matches(
                                                                                    phrase.replace('\u200b', '').replace('\n', ' ') + ':', 
                                                                                    list(initial_parameters.values()),
                                                                                    cutoff = 0.7
                                                                                    )[0]

                                            raw_value = list(new_total[column])[0]
                                            formt_value = format_text(raw_value[0].replace('\u200b', '').replace('\n', ' '))
                                            final_value = formt_value.replace('м2', '').rstrip(' ')
                                            
                                            try:
                                                final_value = str(float(final_value.replace(',', '.').replace(' ', '')))
                                                
                                            except ValueError:
                                                pass

                                            for state, state_phrase in initial_parameters.items():
                                                if state_phrase == new_phrase:
                                                    lst_phrase = state + ' ' + state_phrase
                                                    
                                                    if lst_phrase in begin_dict:
                                                        begin_dict[lst_phrase].append(final_value)
                                                    
                                                    else:
                                                        begin_dict[lst_phrase] = [final_value]
                                            
                                        except IndexError:
                                            continue
                                    
                                    else:
                                        try:
                                            raw_value = list(new_total[column])[0]
                                            
                                            for blblbl in range(len(raw_value)):
                                                if begin_key == '6.1.3' or begin_key == '6.1.4':
                                                    try:
                                                        new_phrase = begin_key + ' ' + difflib.get_close_matches(
                                                                                                phrase.replace('\u200b', '').replace('\n', ' ') + ':', 
                                                                                                begin_params[begin_key],
                                                                                                cutoff = 0.6
                                                                                                )[0]
                                                        
                                                    except IndexError:
                                                        if begin_key + ' ' + begin_params[begin_key][0] in begin_dict:
                                                            new_phrase = begin_key + ' ' + begin_params[begin_key][1]
                                                            
                                                        else:
                                                            new_phrase = begin_key + ' ' + begin_params[begin_key][0]
                                                        
                                                else:
                                                    if len(raw_value) > 1:
                                                        new_phrase = begin_key + ' ' + str(blblbl + 1) + ' ' + begin_params[begin_key][0]
                                                    else:
                                                        new_phrase = begin_key + ' ' + begin_params[begin_key][0]
                                                
                                                formt_value = format_text(raw_value[blblbl].replace('\u200b', '').replace('\n', ' '))
                                                
                                                if ('м2' in formt_value or
                                                    'руб.' in formt_value):
                                                    
                                                    formt_value = formt_value.replace(',', '.').replace('м2', '').replace('руб.', '').replace(' ', '').replace('(', '-').replace(')', '')
                                                
                                                    if 'тыс.' in formt_value:
                                                        formt_value = str(float(formt_value.replace('тыс.', ''))*1000)
                                            
                                                final_value = formt_value.rstrip(' ')
                                                
                                                check_home = check_value('Дом', final_value)
                                                check_corp = check_value('Корпус', check_home[1])
                                                check_strn = check_value('Строение', check_corp[1])
                                                
                                                final_changed = False
                                        
                                                if check_home[0] == 1:
                                                    new_home = check_home[1].split('Строение:')[0].rstrip(' ')
                                                    new_home = new_home.split('Корпус:')[0].rstrip(' ')

                                                    final_value = ''
                                                    final_changed = True
                                                    final_value += 'Дом: ' + format_text(new_home)
                                                    
                                                if check_corp[0] == 1:
                                                    new_corp = check_corp[1].split('Строение:')[0].rstrip(' ')
                                                    
                                                    if final_changed == True:
                                                        final_value += ' Корпус: ' + format_text(new_corp)
                                                        
                                                    else:
                                                        final_value = 'Корпус: ' + format_text(new_corp)
                                                    
                                                if check_strn[0] == 1:
                                                    if final_changed == True:
                                                        final_value += ' Строение: ' + format_text(check_strn[1])
                                                        
                                                    else:
                                                        final_value = 'Строение: ' + format_text(check_strn[1])
                                                
                                                if new_phrase in begin_dict:
                                                    begin_dict[new_phrase].append(final_value)
                                                    
                                                else:
                                                    begin_dict[new_phrase] = [final_value]
                                        
                                        except ValueError:
                                            continue
                                    
                    lst_tbls[date_declar].update({'Total' : begin_dict})
                    
                    # ======================================================================
                
                    common_columns = columns_json[1:]

                    for object in common_columns:
                        object_dict = {}
                        
                        print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz {} zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'.format(object))

                        object_tbl = json_read[object]
                    
                        new_object = object_tbl.to_frame().dropna()
                        new_object = new_object.rename(columns={object: date_declar}).T
                        
                        for standard_key in object_parameters:
                            for column in new_object.columns:
                                if column.startswith(standard_key) and not column.startswith(standard_key + '.'):
                                    new_value = list(new_object[column])[0]
                                    
                                    if standard_key in exceptions:
                                        new_phrase = standard_key + ' ' + exceptions[standard_key]

                                    else:
                                        phrase = column.split(standard_key)[1].lstrip(' ').replace('\u200b', '').replace('\n', ' ')
                                        
                                        try:
                                            new_phrase = standard_key + ' ' + difflib.get_close_matches(
                                                                                    phrase, 
                                                                                    list(initial_parameters.values()),
                                                                                    cutoff = 0.6
                                                                                    )[0]
                                            
                                        except IndexError:
                                            if standard_key != '12.1.1':
                                                if standard_key == '12.3.2' and phrase[-1] != ':':
                                                    continue
                                                
                                                else:
                                                    print('\n\n\n\n\n\n')
                                                    print(standard_key)
                                                    print(phrase.split(':')[0] + ':')
                                                    print(new_value)
                                                    print('\n\n\n\n\n\n')
                                                    
                                                    continue
                                                
                                    new_lst = []
                                    for el in new_value:
                                        el = el.replace('руб.', '').replace('м2', '').replace('м²', '').replace('р.', '')
                                        
                                        if standard_key != '12.3.1':
                                            el = el.replace('_', '.')
                                        
                                        try:
                                            el = str(float(el.replace(',', '.').replace(' ', '')))
                                            
                                        except ValueError:
                                            pass
                                        
                                        new_lst.append(el)
                                        
                                    object_dict[new_phrase] = new_lst
                                    
                        if date_declar not in lst_tbls:
                            lst_tbls[date_declar] = {object : object_dict}
                            
                        else:
                            lst_tbls[date_declar].update({object : object_dict})
                            
                    dict_to_dates = {}
                
                    # ======================================================================

                    for date_special in lst_tbls:
                        dict_to_dates[date_special] = {}
                        
                        for obj in lst_tbls[date_special]:
                            dict_to_dates[date_special][obj] = {}
                            
                            for state_special in lst_tbls[date_special][obj]:
                                for init_key in initial_parameters:
                                    if state_special.startswith(init_key) and not state_special.startswith(init_key + '.'):
                                        key_count = 1
                                        
                                        split_state = state_special.split(init_key)
                                        
                                        for value in lst_tbls[date_special][obj][state_special]:
                                            dict_to_dates[date_special][obj].update({init_key + ' ({})'.format(key_count)  + split_state[1] : value})

                                            key_count += 1
                                                
                        dates_dictionary[date_declar] = dict_to_dates[date_declar]
        
        for project in os.listdir(self.pdf_directory):
            if project.startswith(test_project + '_'):
                shutil.rmtree(self.pdf_directory + '\\' + project)
                
                break
        
        os.chdir(self.xls_directory)
        writer = pd.ExcelWriter(name, engine = 'openpyxl')
            
        dict_to_pd = {}
        for date in dates_dictionary:
            for object in dates_dictionary[date]:
                if object not in dict_to_pd:
                    dict_to_pd[object] = {date : dates_dictionary[date][object]}
                    
                else:
                    dict_to_pd[object].update({date: dates_dictionary[date][object]})
        
        if basic_dummy == True:
            basic_table.to_excel(writer, sheet_name='Basic', index=False)
                        
        for object in dict_to_pd:
            tbl_sel = pd.DataFrame(dict_to_pd[object]).T.fillna('[null]')
        

            tbl_rdx = tbl_sel.reset_index()
            tbl_rdx['index'] = pd.to_datetime(tbl_rdx['index'], format="%d.%m.%Y").dt.date
            tbl_rdx = tbl_rdx.rename(columns={'index': 'Дата выпуска декларации'})
            tbl_rdx['Месяц-год'] = pd.DataFrame([str(el)[:-3] for el in list(tbl_rdx['Дата выпуска декларации'])])
            
            tbl_new = tbl_rdx.set_index('Дата выпуска декларации')
            tbl_new = tbl_new.sort_index()

            tbl_new = tbl_new.sort_index(axis=1).fillna('[null]').replace('', '[null]')
            tbl_new.to_excel(writer, sheet_name=object)

        writer.close()
