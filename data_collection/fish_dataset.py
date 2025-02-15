from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import os
from PIL import Image
from io import BytesIO


chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

url = 'https://www.inaturalist.org/taxa/99684-Echinus-esculentus/browse_photos'
driver.get(url)
time.sleep(10)  # Sayfanın yüklenmesi için bekleme süresi

last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


thumbnails = driver.find_elements(By.CSS_SELECTOR, 'div.CoverImage')

print(f"Bulunan küçük resim sayısı: {len(thumbnails)}")

# Resimleri kaydetmek için dizin oluştur
save_folder = "downloaded_images"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

count = 1
for thumb in thumbnails:
    try:
 
        style = thumb.get_attribute('style')
        start_index = style.find('url("') + 5
        end_index = style.find('")', start_index)
        if start_index != -1 and end_index != -1:
            small_img_url = style[start_index:end_index]
            
   
            large_img_url = small_img_url.replace('medium', 'large')

            response = requests.get(large_img_url)
            img = Image.open(BytesIO(response.content))
            img_name = os.path.join(save_folder, f"image_{count}.jpg")
            img.save(img_name)
            print(f"Resim {count} indirildi: {img_name}")
            count += 1

        # İndirme limiti
        if count > 700:  
            break
    except Exception as e:
        print(f"Resim indirilemedi, Hata: {e}")

# Tarayıcıyı kapat
driver.quit()
