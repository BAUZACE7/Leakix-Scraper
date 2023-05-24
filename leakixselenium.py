import requests
import sys
import time
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from twocaptcha import TwoCaptcha
import concurrent.futures

timeoutCount = 7
solver = TwoCaptcha('21b23e5f2cd3969b0f2faacc77397c15')

# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument('--headless')


def process_chunk(chunk, thread_id):
    driver = webdriver.Chrome(options=chrome_options)

    for line in chunk:
        for i in range(1, 11):
            try:
                target_url = f"https://leakix.net/search?page={i}&q={line.strip()}&scope=leak"
                driver.get(target_url)
                time.sleep(0.2)
                pg = driver.page_source

                if "DDoS protection" in pg:
                    process_ddos_protection(driver, pg)
                elif "Your request is rate limited" in pg:
                    time.sleep(7)
                elif "The request site is currently unavailable" in pg:
                    handle_ban()
                else:
                    process_page(driver, pg, line, thread_id)
            except Exception as e:
                print(f"Error: {e}")
                pass

    driver.quit()


def process_ddos_protection(driver, pg):
    print('Submitting Captcha')
    soup = BeautifulSoup(pg, 'html.parser')
    link = soup.find('img', {'alt': 'Captcha'})
    linkOfCaptcha = link['src']
    result = solver.normal(linkOfCaptcha)
    Code = result['code']
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/form/div[2]/input').send_keys(Code)
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/form/div[3]/button').click()


def handle_ban():
    print('Been Banned ...')
    requests.get('https://api.telegram.org/bot1820321014:AAHECx5eEBBJ3EI-PsoLSo6jrU4XwRXMCO0/sendMessage?chat_id=1676973501&text=Stopped%20Due%20to%20IP%20Change,%20Go%20Change%20It')
    input('Change IP and Press Enter')


def process_page(driver, pg, line, thread_id):
    soup = BeautifulSoup(pg, 'html.parser')
    parent = soup.findAll('div', {'class': 'col-xl-4'})

    if not parent:
        print(f'No Remaining Domains for {line.strip()}...')
    else:
        with open('result.txt', 'a', encoding="utf-8") as rz:
            for ip in parent:
                ipstripped = ip.find('a', href=True)
                print(ipstripped.text)
                rz.write(ipstripped.text + '\n')


def split_file(filepath, num_chunks):
    with open(filepath, 'r') as fp:
        lines = fp.readlines()

    return [lines[i::num_chunks] for i in range(num_chunks)]


def main(filepath, num_threads=5):
    chunks = split_file(filepath, num_threads)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_chunk, chunk, i) for i, chunk in enumerate(chunks)]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread execution: {e}")

if __name__ == "__main__":
    banner = """
BBBBB  AAAAA  U   U  ZZZZZ   AAAAA  CCCCC  EEEEE   777
B   B  A   A  U   U     Z    A   A  C      E         7
BBBBB  AAAAA  U   U    Z    AAAAA  C      EEEE      7
B   B  A   A  U   U   Z    A   A  C      E         7
BBBBB  A   A   UUU   ZZZZ A   A  CCCCC  EEEEE  77777
"""

    print(banner)

    filename = input('Keyword file: ')

    main(filename)
