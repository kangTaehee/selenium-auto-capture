## -*- coding: utf-8 -*-  # 한글 주석쓸려면 적기
# 탭사이즈 4
import os, time, re
from selenium import webdriver
from bs4 import BeautifulSoup
from PIL import Image
import pandas as pd

domain = 'http://ucms.unpl.co.kr' #사이트 도메인

site_id = 'sitename' #사이트 아이디와 같은 폴더 생성
menu_file = site_id + '.csv'

df = pd.read_csv(os.getcwd() + '\\' + menu_file, encoding="UTF-8", low_memory=False,sep=",")
df = df.fillna('')  #nan을 공백으로 처리
#MENU_NO,MENU_NM,ALL_MENU_COURS

df['ALL_MENU_COURS'] = df['ALL_MENU_COURS'].str.replace('&amp;','&')

#IE는 자신의 현재 브라우저 사이즈로만 동작된다 & headless 모드가 안된다.
resolutions = ['360', '765', '1200'] #캡춰 사이즈 너비 설정 ie할때는 배열값은 한개만...
height = '1080' #수정안해도 됨.

def fullpage_screenshot(driver, file):

    # print("Starting chrome full page screenshot workaround ...")

    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    # print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            # print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width,top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            # print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.2)

        file_name = "part_{0}.png".format(part)
        # print("Capturing {0} ...".format(file_name))

        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        # print("Adding to stitched image with offset ({0}, {1})".format(offset[0],offset[1]))
        stitched_image.paste(screenshot, offset)

        del screenshot
        os.remove(file_name)
        part = part + 1
        previous = rectangle

    stitched_image.save(file)
    # print("Finishing chrome full page screenshot workaround...")
    return True

for width in resolutions:
		# 크롬설정 성공		
		# options = webdriver.ChromeOptions()
		# options.add_argument('headless')
		# options.add_argument('window-size=' + width + 'x' + height)
		# options.add_argument("disable-gpu")
		# driver = webdriver.Chrome(os.getcwd() + '\\driver\\chromedriver.exe', chrome_options=options)
		
		# 엣지설정 성공
		# Edge(MicrosoftWebDriver)를 이용해 Edge를 실행합니다.
		# driver = webdriver.Edge(executable_path='C:/Users/user/Downloads/edgedriver_win64/msedgedriver.exe')
		
		# IE설정 열댓번만에 성공...이런 신발...
		# driver = webdriver.Ie(os.getcwd() + '\\driver\\IEDriverServer.exe') 실패..실패..실패..
		# driver = webdriver.Ie(os.getcwd() + '\\driver\\IEDriverServer2.4.exe') 성공... 화면 틀어짐 실패
		# driver = webdriver.Ie(os.getcwd() + '\\driver\\IEDriverServer3.9.0.exe') 실패
		# driver = webdriver.Ie(os.getcwd() + '\\driver\\IEDriverServer4.exe') 실패
		driver = webdriver.Ie(os.getcwd() + '\\driver\\IEDriverServer380.exe') #성공
    try:
        os.stat(os.getcwd() + '\\' + site_id + '\\' + str(width) + 'px')
    except:
        os.mkdir(os.getcwd() + '\\' + site_id + '\\' + str(width) + 'px')


    for idx, row in df.iterrows():
        try:
            driver.get(domain + row['ALL_MENU_COURS'])
        except Exception as e:
            print(e)
            continue
        try:
            alert = driver.switch_to_alert()
            alert.accept()
        except Exception as e:
            print(e)
            pass

        try:
            fullpage_screenshot(driver, os.getcwd() + '\\' + site_id + '\\' + str(width) + 'px\\' + str(row['MENU_NO']) + '-' + str(row['MENU_NM']) + '(' + width + 'px).png')
            print('====', idx, row['MENU_NO'], '======')
        except Exception as e:
            print(e)
            continue

    driver.quit()
