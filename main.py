import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException


def check_exists_by_css(check_driver, css):
    try:
        check_driver.find_element(By.CSS_SELECTOR, css)
    except NoSuchElementException:
        return False
    return True


def css_selector(element):
    css_dict = {
        'next_button': 'a[data-qa="pager-next"]',
        'salary': 'span[data-qa="vacancy-serp__vacancy-compensation"]',
        'address': 'div[data-qa="vacancy-serp__vacancy-address"]',
        'company': 'a[data-qa="vacancy-serp__vacancy-employer"]'
    }
    return css_dict[element]


def extracting_vacancy_attributes(vacancy_elm):
    title_element = vacancy_elm.find_element(By.CLASS_NAME, "serp-item__title")
    title = title_element.text
    link = title_element.get_attribute('href')
    address = vacancy_elm.find_element(By.CSS_SELECTOR, css_selector('address')).text
    salary = vacancy_elm.find_element(By.CSS_SELECTOR, css_selector('salary')).text
    try:
        company = vacancy_elm.find_element(By.CSS_SELECTOR, css_selector('company')).text
    except NoSuchElementException:
        company = vacancy_elm.find_element(By.CLASS_NAME, 'vacancy-serp-item__meta-info-company').text
    except:
        company = 'Не определено'
    vacancy_attrs = {
        'title': title,
        'link': link,
        'salary': salary.replace('\u202f', ' '),
        'address': address.split(',')[0],
        'company': company
    }
    return vacancy_attrs


def criteria_check(vacancy_obj):
    verification_passed = False
    if vacancy_obj['salary'].lower().find('usd') < 0:
        return verification_passed
    local_service = ChromeService(executable_path=ChromeDriverManager().install())
    local_driver = webdriver.Chrome(service=local_service)
    local_driver.get(vacancy_obj['link'])
    description = local_driver.find_element(By.CLASS_NAME, 'vacancy-description').text
    if description.find('Django') < 0:
        return verification_passed
    if description.find('Flask') < 0:
        return verification_passed
    verification_passed = True
    return verification_passed


if __name__ == '__main__':
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    HOST = 'https://spb.hh.ru/search/vacancy?area=1&area=2&only_with_salary=true&text=python'
    driver.get(HOST)

    vacancies = []
    while True:
        vacancies_element = driver.find_element(By.CLASS_NAME, 'vacancy-serp-content')
        for vacancy_element in vacancies_element.find_elements(By.CLASS_NAME, "serp-item"):
            vacancy = extracting_vacancy_attributes(vacancy_element)
            if criteria_check(vacancy):
                vacancies.append(vacancy)
        if not check_exists_by_css(driver, css_selector('next_button')):
            break
        next_button = driver.find_element(By.CSS_SELECTOR, css_selector('next_button'))
        next_link = next_button.get_attribute('href')
        driver.get(next_link)

    with open('vacancies_info.json', 'w') as f:
        json.dump(vacancies, f, indent=2, ensure_ascii=False)
