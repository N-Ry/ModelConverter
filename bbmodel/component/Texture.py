import base64
import numpy as np
import io 
from PIL import Image

class texture:
    def __init__(self,data):
        # base64でテクスチャ情報を取得
        img_base64 = data['source'].removeprefix("data:image/png;base64,")           

        # base64で受け取った画像データをデコードしてndarrayで格納
        img_binary = base64.b64decode(img_base64)           # binary  <- base64
        img_png = Image.open(io.BytesIO(img_binary))    # image   <- binary
        self.array = np.array(img_png)                  # ndarray <- image

        # 読み取り専用データの取得
        self._name = self.data["name"]
        self._width = self.data["width"]
        self._height = self.data["height"]
        self._uv_width = self.data["uv_width"]
        self._uv_height = self.data["uv_height"]
        self._scale_factor = int(self.data["width"] / self.data["uv_width"])
    
    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
    
    @property
    def uv_width(self):
        return self._uv_width
    
    @property
    def uv_height(self):
        return self._uv_height
    
    @property
    def scale_factor(self):
        return self._scale_factor
    
    def encode64():
        pass