from time import sleep
from time import sleep
from utils.parser_handler import remove_duplicates_on_list, remove_whitespaces
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException

import os
import requests
import shutil


def getAmazonImageGalery(driver):
    print('> Iniciando extração da galeria...')
    driver.implicitly_wait(10)

    try:
        modal = driver.find_element_by_css_selector('.a-dynamic-image.a-stretch-horizontal')
        modal.click()
    except NoSuchElementException:
        try:
            modal = driver.find_element_by_css_selector('.a-dynamic-image.a-stretch-horizontal')
            modal.click()
        
        except Exception as erro:
            print(f'> Erro ao pega dados da galeria')
            return

    sleep(5)

    images_container = driver.find_element_by_id('ivThumbs')
    buttons = images_container.find_elements_by_css_selector('.ivThumbImage')

    # print(buttons)
    galery = []
    for button in buttons:
        try:
            button.click()
        
        except ElementNotInteractableException:
            pass

        else:
            pass
        
        sleep(3)
        main_container = driver.find_element_by_id('ivLargeImage')
        image = main_container.find_element_by_tag_name('img').get_attribute('src')

        galery.append(image)

    galery = remove_duplicates_on_list(galery)
    print('> Imagens extraídas!')
    return ','.join(galery)


def download_image(url):
    pic_folder = "/galeria"
    if not os.path.isdir(pic_folder):
        os.makedirs(pic_folder)

    if url.split('/')[2] == 'm.media-amazon.com':
        filename = url.split('/')[-1].split('.')[0]        
    else:
        filename = url.split('/')[4]

    with open(f"{filename}.jpg", 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
    
    try:
        shutil.move(f'./{filename}.jpg', pic_folder)
    
    except shutil.Error:
        os.unlink(f'./{filename}.jpg')
        print('Imagem já movida!')

    return f"{pic_folder}/{filename}"


def find_magalu_images(soap):
    def sanitize_image(image):
        return image['src'].split('/')[-1]

    def higher_resolution(image):
        try:
            return image.replace('88x66','618x463')
        
        except TypeError:
            return

    galery = soap.find('div', class_="pgallery")
    images = []

    for image in galery.find_all('img'):
        try:
            image_test = sanitize_image(image)
            if not image_test.endswith('.svg'):
                image = higher_resolution(image['src'])
                images.append(f"{image}")
        except (KeyError, TypeError):
            pass
    
    images = remove_duplicates_on_list(images)
    return ','.join(images)


def get_specs(raw_specs):
    
    specs = []

    for column in raw_specs.find_all('tr'):    
        title_table = column.select('td')[0].text
        content_table = column.select('td')[-1].text
        text_table = f"{remove_whitespaces(title_table)}: {remove_whitespaces(content_table)}"
        specs.append(text_table)

    return '\n'.join(specs)


def get_magazine_specs(soap):
    try:
        container = soap.find('table', class_="tab ficha-tecnica")
        raw_tecnical_content = container.find('tr', class_="element level1 odd")
        spec_content = raw_tecnical_content.find('td', class_="element")
        specs = get_specs(spec_content)
        return specs

    except AttributeError:
        return ""
