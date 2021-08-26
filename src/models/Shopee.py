from utils.setup import setSelenium
from utils.webdriver_handler import smooth_scroll


def crawl_shopee(url, root_path):

    print('> Iniciando Shopee Crawler...')
    driver = setSelenium(root_path=root_path, console=False)
    try:
        print('> Driver inicializado! iniciando site...')
        driver.get(url)
        driver.implicitly_wait(220)

        print('> scrollando página...')
        smooth_scroll(driver)

        print('> Extraindo dados...')
        print('> Extrair Nome...')
        title = driver.find_element_by_css_selector('.attM6y').text

        print('> Extrair preço...')
        price_container = driver.find_element_by_css_selector('.flex.items-center._3iPGsU')
        promotional_price = price_container.find_element_by_css_selector('._2MaBXe').text
        price = price_container.find_element_by_css_selector('.flex.items-center').find_element_by_tag_name('div').text
        
        print('> Extrair categoria...')
        category = str(driver.find_element_by_css_selector('.flex.items-center._1J-ojb.page-product__breadcrumb').text).replace('\n', ' > ')
        
        print('> Extrair descrição')
        description = driver.find_elements_by_css_selector('._3wdEZ5')
        short_description = description[0].text
        details = description[-1].text
        
        print('\n')
        print('> Mostrar resultados...')
        print('Nome: ', title)
        print('Preço promocional: ', promotional_price)
        print('Preço: ', price)
        print('Url Externa: ', url)
        print('Categoria: ', category)
        print('Descrição curta: ', short_description)
        print('Descrição: ', details)
    
    except Exception:
        driver.quit()
        raise

    except KeyboardInterrupt:
        driver.quit()
        print('> Saindo volte sempre!')