import requests
from PIL import Image
from io import BytesIO

# 이미지 URL

# 이미지 다운로드
response = requests.get(image_url)

# 다운로드한 데이터를 이미지로 변환
if response.status_code == 200:
    image_data = BytesIO(response.content)
    image = Image.open(image_data)

    # 이미지 저장
    image.save("extracted_image.jpg")  # 원하는 파일 이름으로 변경 가능

    # 이미지 표시 (선택 사항)
    image.show()
else:
    print("이미지를 다운로드할 수 없습니다.")
