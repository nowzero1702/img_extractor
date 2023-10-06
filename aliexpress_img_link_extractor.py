from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urljoin
from urllib.parse import urlparse
import openpyxl

class ChromeDriver:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def open_url(self, url):
        self.driver.get(url)
        time.sleep(2)

    def scroll_page(self, scroll_count=1):
        time.sleep(1)
        for _ in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, 1500);")
            time.sleep(2)

    def get_page_source(self):
        return self.driver.page_source

    def close(self):
        self.driver.quit()


class ImageExtractor:
    def __init__(self, driver):
        self.driver = driver
        self.soup = None  # 초기에는 None으로 설정

    def initialize_soup(self):
        page_source = self.driver.get_page_source()
        self.soup = BeautifulSoup(page_source, 'html.parser')

    def extract_option_images(self):
        img_link = []
        if self.soup is None:
            self.initialize_soup()  # soup이 None인 경우 초기화
        sku_divs = self.soup.find_all('div', class_=lambda value: value and 'sku' in value)
        for sku_div in sku_divs[1]:
            option_image_links = [img['src'] for img in sku_div.find_all('img')]
            # print("옵션 이미지 링크:")
            for link in option_image_links:
                img_link.append(link)
        return img_link

    def extract_product_images(self):
        img_link = []
        if self.soup is None:
            self.initialize_soup()  # soup이 None인 경우 초기화
        images_view_divs = self.soup.find_all('div', class_=lambda value: value and 'images-view' in value)
        for images_view_div in images_view_divs[0]:
            image_links = [img['src'] for img in images_view_div.find_all('img')]
            # print("상품 이미지 링크:")
            for link in image_links:
                img_link.append(link)
                # print(link)
        return img_link
    def extract_detail_images(self):
        img_link = []
        if self.soup is None:
            self.initialize_soup()  # soup이 None인 경우 초기화
        detail_desc_divs = self.soup.find_all('div', class_=lambda value: value and 'product-description' in value)
        for detail_desc_div in detail_desc_divs:
            image_links = [img['src'] for img in detail_desc_div.find_all('img')]
            # print("상세 이미지 링크:")
            for link in image_links:
                img_link.append(link)
                # print(link)
        return img_link

class link_trimmer:
    def __init__(self, urls):
        self.urls = urls

    def extract_filenames(self):
        filenames = []
        for url_list in self.urls:
            filename = []
            for urls in url_list:
                # print(urls)
                # URL에서 마지막 슬래시 뒤의 문자열 추출
                # ".jpg"까지의 부분 추출
                file_name = urls.split(".jpg")[0] + ".jpg"

                # print(file_name)

                filename.append(file_name)
            filenames.append(filename)

        return filenames

class ImageDownloader:
    def __init__(self):
        self.session = requests.Session()


    def download_image(self, img_url, save_directory,filename):
        # 이미지 다운로드
        img_data = self.session.get(img_url).content

        # 이미지의 확장자를 추출
        parsed_url = urlparse(img_url)
        img_extension = os.path.splitext(parsed_url.path)[1]

        # 이미지를 저장할 파일명 설정
        filename = os.path.join(save_directory, filename + img_extension)

        # 이미지 저장
        with open(filename, 'wb') as img_file:
            img_file.write(img_data)

        print(f'이미지 저장 완료: {filename}')





class Directory_maker:
    def __init__(self, file_path, sheet_name, base_directory):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.base_directory = base_directory


    def read_column(self,column_letter):
        try:
            # 엑셀 파일 열기
            workbook = openpyxl.load_workbook(self.file_path)

            # 원하는 시트 선택
            sheet = workbook[self.sheet_name]

            # 특정 열의 모든 값을 읽어오기
            column_values = []
            for cell in sheet[column_letter]:
                column_values.append(cell.value)

            # 엑셀 파일 닫기
            workbook.close()

            return column_values[1:]
        except Exception as e:
            print(f"오류 발생: {e}")
            return None
    def create_directory(self, new_directory_name):
        # 새 디렉토리 경로 생성
        option_dirs = []
        product_dirs = []
        detail_dirs = []
        new_directory_path = os.path.join(self.base_directory, new_directory_name)
        option_directory_path = os.path.join(new_directory_path, '옵션이미지')
        product_directory_path = os.path.join(new_directory_path, '상품이미지')
        detail_directory_path = os.path.join(new_directory_path, '상세이미지')

        option_dirs.append(option_directory_path)
        product_dirs.append(product_directory_path)
        detail_dirs.append(detail_directory_path)
        

        # 디렉토리 생성
        try:
            os.mkdir(new_directory_path)
            os.mkdir(option_directory_path)
            os.mkdir(product_directory_path)
            os.mkdir(detail_directory_path)
            print(f"디렉토리 생성 완료: {new_directory_path}")
            return option_directory_path, product_directory_path, detail_directory_path
        except FileExistsError:
            print(f"디렉토리가 이미 존재합니다: {new_directory_path}")
            return option_directory_path, product_directory_path, detail_directory_path
        except Exception as e:
            print(f"디렉토리 생성 중 오류 발생: {e}")

# 사용 예제
if __name__ == "__main__":

    # ======================= 엑셀 접근 ===============
    file_path = r'C:\Users\이제영\PycharmProjects\img_extractor\쿠팡 소싱 리스트(업로드).xlsx'  # 엑셀 파일 경로와 파일명으로 변경
    base_directory = r'C:\Users\이제영\OneDrive - 한국외국어대학교\바탕 화면\알리 이미지 추출'

    sheet_name = '알리_이제영'  # 시트 이름으로 변경
    name_column = 'C'  # 읽고자 하는 열의 열 번호로 변경 (예: 'A', 'B', 'C' 등)
    link_column = 'O'
    dir_maker = Directory_maker(file_path, sheet_name,base_directory)

    # 메서드 호출 예제
    folder_name = dir_maker.read_column('C')
    img_link = dir_maker.read_column('O')

    print(folder_name)
    print(img_link)


    #1차 디렉터리 만들기
    option_dirs = []
    product_dirs = []
    detail_dirs = []

    for name in folder_name:
        opt_dir, pro_dir, det_dir = dir_maker.create_directory(name)
        option_dirs.append(opt_dir)
        product_dirs.append(pro_dir)
        detail_dirs.append(det_dir)
    print(option_dirs)
    print(product_dirs)
    print(detail_dirs)
    # =========================== 엑셀 접근 완료 ===============

    # =========== 이미지 다운로드 및 저장 ==================== #
    print(img_link)
    for link in img_link:
        url = link

        driver = ChromeDriver()
        driver.open_url(url)
        driver.scroll_page(scroll_count=1)

        extractor = ImageExtractor(driver)
        option_link = extractor.extract_option_images()
        product_link = extractor.extract_product_images()
        detail_link = extractor.extract_detail_images()

        print("option link = ", option_link)
        print("product link = ", product_link)
        print("detail link = ", detail_link)

        link_lists = []
        link_lists.append(option_link)
        link_lists.append(product_link)
        link_lists.append(detail_link)
        print(link_lists)

        # print(option_link)
        # print(link_lists)
        link_trimmer_c = link_trimmer(link_lists)
        trimmed_link = link_trimmer_c.extract_filenames()

        option_link = trimmed_link[0]
        product_link = trimmed_link[1]
        detail_link = trimmed_link[2]
        print(trimmed_link)
        # link_trimmer.
        print(len(option_link))



        count_opt = 1
        count_pro = 1
        count_det = 1


        # img_url = 'https://ae01.alicdn.com/kf/S0037a2bb0f89429d9cba3a2451fac606D/-.jpg'  # 이미지 URL
        # save_directory = r'C:\Users\이제영\PycharmProjects\img_extractor'
        driver.close()





