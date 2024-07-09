from libraries import *
from config import *


class Parsing:

    '''
    Initial variables that are created during the start of the program
        @ folder projects - to save the real estate projects, including:
            a) excel folder - for the excel files for each project, which is created separately by the certain function;
            b) json folder - for the collecting information about the projects in more optimized way;
            c) pdf folder - for the collecting declarations of the projects;
        @ folder queries - to save the queries for the downloading projects by the chosen parameters
    '''
    def __init__(self, script_path = None):

        # check whether the path to the files was entered initially by the user
        if script_path == None:
            script_path = os.getcwd()
        self.script_path = script_path

        # check whether platform of the user starts with "win" (standing for the windows - either "windows" or "win32", etc.)
        if str(sys.platform).lower().startswith('win'):
            self.slash = '\\'
        else:
            self.slash = '/'

        # setting the root for the folders of the program
        if 'main_script' not in self.script_path:
            self.progrm_path = self.script_path
            self.script_path = self.script_path + self.slash + 'main_script'
        else:
            self.progrm_path = self.script_path.replace(self.slash + 'main_script', '')

        # setting the path for the chrome driver
        if self.slash == '\\':
            chomedriver_path = self.script_path + self.slash + 'chromedriver.exe'
        else:
            chomedriver_path = self.script_path + self.slash + 'chromedriver'

        # function for the creating new folders
        def check_n_create(inp_name, ch_pth):
            lst_dir = os.listdir(ch_pth)

            if inp_name not in lst_dir:
                os.chdir(ch_pth)
                os.mkdir(inp_name)

            return ch_pth + self.slash + inp_name

        # creating different folders and files
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

        # setting default options for the google drive (where to download from)
        self.ser = Service(chomedriver_path)
        self.opt = Options()

        # template link for the single project (need to add ID of the project in the end of the url)
        self.template_link = TEMPLATE_LINK


    '''
    Function for checking of the certain element in the code of the web-page
    '''
    def find_special_elements(self, driver: object, button = None, 
                                parameter = None, scrolling_time = 0, attempt = 1, driver_close = False):

        # scrolling down the page in order to find button for the page expansion
        if button != None:
            scrolling_break = False
            while scrolling_break == False:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scrolling_time)

                try:
                    button_find = driver.find_element(By.XPATH, "//button[@class='{}']".format(button))
                    button_find.click()
                except:
                    scrolling_break = True

        # find the certain element if it is required by the task
        if parameter != None:
            break_time = 0
            break_find = None

            while break_time <= attempt:
                try:
                    break_find = driver.find_elements(By.XPATH, parameter)
                    print('Element {} is found!'.format(parameter))

                    if driver_close == True:
                        driver.close()

                    return break_find

                except:
                    time.sleep(1)
                    break_find = None
                    break_time += 1

            if driver_close == True:
                driver.close()
                return break_find

            print('Element {} is not found!'.format(parameter))


    '''
    Getting the number of lists with the projects and projects' links and ids
    '''
    def projects_links(self, url: str, attempt = 1, theme = None, new = True):
        # if the query is new, then parse the site by the given link to get list of projects
        if new == True:

            # entering the name of the theme for research
            if theme == None:
                theme = input('Введите название для темы поиска: ')

            # start using chrome for search of the projects list
            driver = webdriver.Chrome(service=self.ser)
            driver.get(url)
            
            '''
            HISTORY OF UPDATES: 
            @ date: ???, list of pages included in the link, needed to find pagination button or button "next";
            @ optimal version: 08.07.2024, no list of pages, only button "LOAD MORE"
            '''
            projects_list = "//div[@class='{}']".format(PROJECTS_LIST)
            projects_rows = self.find_special_elements(driver = driver, button = PROJECTS_LIST_BUTTON, parameter = projects_list, attempt = attempt)[0]
            
            if projects_rows != None:
                dict_projects = {}

                # find ids and names + commissioning dates of the projects
                project_id = "//p[@class='{}']".format(SINGLE_PROJECT_ID)
                project_name = "//p[@class='{}']".format(SINGLE_PROJECT_NAME)

                # lists of the found elements
                list_ids = self.find_special_elements(driver = driver, parameter = project_id, attempt = attempt)
                list_names = self.find_special_elements(driver = driver, parameter = project_name, attempt = attempt)

                # transforming elements into text values
                texts_ids = [str(id.text.replace('ID: ', '')) for id in list_ids]
                # texts_names = [str(name.text).encode('ascii', 'ignore') for name in list_names]
                texts_names = [str(name.text) for name in list_names]

                # sorting between names and commissioning dates
                builds_names = texts_names[::2]
                builds_vvods = texts_names[1::2]

                for i in range(len(texts_ids)):
                    dict_projects[texts_ids[i]] = {'name': builds_names[i], 'date': builds_vvods[i]}

                # save the theme as a json file as a historical request
                os.chdir(self.progrm_path + self.slash + 'queries')

                try:  
                    with open(theme + '.json', 'w') as outfile:
                        json.dump(dict_projects, outfile)

                    self.dict_projects = dict_projects
                
                except TypeError as e:
                    print(f'Error: {e}')

            else:
                print('No projects for the request were found!')

        # if the query already exists, upload it into the dictionary
        else:
            os.chdir(self.progrm_path + self.slash + 'queries')

            with open(theme + '.json', 'r') as f:
                self.dict_projects = json.load(f)


    '''
    Getting the basic information about the project and download its declarations
    '''
    def get_declarations(self, attempt = 1, new = False, theme = None):
        if new != False and theme != None:
            os.chdir(self.progrm_path + self.slash + 'queries')

            with open(theme + '.json', 'r') as f:
                self.dict_projects = json.load(f)

            for id in list(self.dict_projects.keys())[3:4]:
                pdf_directory = self.progrm_path + self.slash + 'projects'
                os.chdir(pdf_directory + self.slash + 'pdf')

                if id not in os.listdir(pdf_directory + self.slash + 'pdf'):
                    os.mkdir(id)
                
                os.chdir(id)

                # all links have the same template
                project_link = TEMPLATE_LINK + '/' + id

                # run the link of the single project to 
                driver = webdriver.Chrome(service=self.ser)
                driver.get(project_link)

                single_project_declarations = "//div[@class='{}']/div/a".format(SINGLE_PROJECT_TABLE_DECLARATIONS)
                single_declaration_date = "//span[@class='{}']".format(SINGLE_DECLARATION_DATE)

                # try to scroll the page fully down and find list of declarations
                list_declarations_elements = self.find_special_elements(driver = driver, button = SINGLE_PROJECT_BUTTON, 
                                                                        parameter = single_project_declarations, attempt = attempt)
                list_declarations_hrefs = [element.get_attribute('href') for element in list_declarations_elements]

                # try to find the dates for each of the declarations
                list_declarations_subdates = self.find_special_elements(driver = driver, 
                                                                     parameter = single_declaration_date, attempt = attempt)
                list_declarations_dates = [date.text for date in list_declarations_subdates]
                
                


if __name__ == '__main__':
    test_url = 'https://наш.дом.рф/сервисы/каталог-новостроек/список-объектов/список?place=0-1&metroId=1.98&time=-30'

    parsing = Parsing()
    parsing.projects_links(url = test_url, theme = 'test', new = False)
    parsing.get_declarations(new = True, theme = 'test')
