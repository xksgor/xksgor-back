# from PIL import Image, ImageFont, ImageDraw

# target_img = Image.open("template.png")

# from IPython.display import Image as ipy_im

# def loadfont(fontsize=50):
# 	# ttf파일의 경로를 지정합니다.
# 	ttf = 'Pretendard-Bold.ttf'
# 	return ImageFont.truetype(font=ttf, size=fontsize)
#     #size : in pixels
    
# namefontObj = loadfont(fontsize=120)
# numfontObj = loadfont(fontsize=87)
    
# out_img = ImageDraw.Draw(target_img)


# name = "권오윤"
# num = "#123번째 시민"

# text_width, text_height = draw.textsize(num, font=numfontObj)

# out_img.text(xy=(218,220), text=name, fill=(259,259,259), font=namefontObj)
# out_img.text(xy=(1080-text_width,800), text=name, fill=(259,259,259), font=numfontObj)

# target_img.save("result.png")

# result_img = Image.open("result.png")
# result_img.show()

from fastapi import FastAPI, Form
from pydantic import BaseModel
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Optional

app = FastAPI()

# 전역 폰트와 템플릿 이미지 객체
font_path = "Pretendard-Bold.ttf"
template_path = "template.png"
namefontObj = None
numfontObj = None
template_img = None

class Item(BaseModel):
    name: str
    description: str = None


# 애플리케이션 시작 시 폰트 및 템플릿 이미지 로드
@app.on_event("startup")
async def startup():
    global namefontObj, numfontObj, template_img
    namefontObj = ImageFont.truetype(font=font_path, size=120)
    numfontObj = ImageFont.truetype(font=font_path, size=87)
    template_img = Image.open(template_path)


def create_image(name: str, num: int):
    # 템플릿 이미지 복제 (각 요청마다 새로 생성)
    target_img = template_img.copy()
    out_img = ImageDraw.Draw(target_img)

    # 숫자를 포맷팅 (세 자리마다 콤마 + # 추가)
    formatted_num = f"#{num:,}"

    # num 텍스트 크기 계산
    num_bbox = out_img.textbbox((0, 0), formatted_num, font=numfontObj)
    text_width = num_bbox[2] - num_bbox[0]

    # 텍스트 렌더링
    out_img.text((218, 220), name, fill=(255, 255, 255), font=namefontObj)  # 이름 출력
    out_img.text((1080 - text_width, 800), formatted_num, fill=(255, 255, 255), font=numfontObj)  # 번호 출력

    # 결과 이미지를 바이트로 저장하여 메모리에서 처리
    img_byte_arr = io.BytesIO()
    target_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)  # 이미지의 시작 부분으로 포인터 이동

    return img_byte_arr


@app.post("/generate-image/")
async def generate_image(name: str = Form(...), num: int = Form(...)):
    """
    FastAPI 엔드포인트: name과 num을 입력받아 이미지를 생성 후 반환합니다.
    """
    img_byte_arr = create_image(name, num)
    return FileResponse(img_byte_arr, media_type="image/png", filename="result.png")

