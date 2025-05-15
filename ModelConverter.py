import os
import tkinter
import tkinter.filedialog
import json
import base64
import numpy as np
import cv2

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def main():
    original = Bbmodel()
    original.loadFile()
    
    elements = original.getElements()
    textures = original.getTextures()

    # すべてのUVテクスチャが入りきる最小のピクセルサイズを計算
    rectangles = []
    for i, elem in enumerate(elements):
        ratio = original.uv_ratio[elem.texture_index]
        rectangles.insert(i,(ratio*elem.width,ratio*elem.height))
    
    L = min_square_size(rectangles)
    px = next_power_of_two(L)

    # 各UVの基点座標を取得
    anchor = place_rectangles(L,rectangles)

    # 新しいUV座標を設定
    original.data["elements"] = []
    for i, elem in enumerate(elements):
        ratio = original.uv_ratio[elem.texture_index]
        elem.new["faces"] = elem.generateBoxUVCord(anchor[i][0]/ratio,anchor[i][1]/ratio)

        elem.new["uv_offset"] = [anchor[i][0]/ratio,anchor[i][1]/ratio]
        
        original.data["elements"].append(elem.new)
    
    # ファイルフォーマットをModded Entityに変更
    original.data["meta"]["model_format"] = "modded_entity"

    
    original.exportFile()
    print(px)

class Bbmodel:
    def initialize(self):
        self.uv_ratio = []
        for value in self.data["textures"]:
            self.uv_ratio.append(int(value["width"] / value["uv_width"]))

    def loadFile(self):
        widget = tkinter.Tk()
        widget.withdraw()
        fileType = [("BlockBench Model","*.bbmodel")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        self.filePath = tkinter.filedialog.askopenfilename(filetypes = fileType,initialdir = iDir)

        if os.path.exists(self.filePath):
            try:
                with open(self.filePath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    self.initialize()
                return self.data
            
            except Exception as e:
                print(f"Unable to load bbmodel file. An unexpected error occurred: {e}")
        else:
            print("指定されたファイルは存在しません。")

    def exportFile(self):
        widget = tkinter.Tk()
        widget.withdraw()
        
        iName = os.path.splitext(os.path.basename(self.filePath))[0]
        iName = iName + "_Modded.bbmodel"

        fileType = [("BlockBench Model","*.bbmodel")]
        iDir = self.filePath
        path = tkinter.filedialog.asksaveasfilename(initialfile=iName,filetypes = fileType,initialdir = iDir)

        with open(path,"w") as f:
            json.dump(self.data,f,indent=2)
        
    def getElements(self):
        if "elements" in self.data:
            list = []
            for x in self.data["elements"]:
                list.append(self.Element(x))
            return list
        else:
            return None
    
    def getTextures(self):
        if "textures" in self.data:
            self.textures = []

            for x in self.data["textures"]:
                img_base64 = x['source'].removeprefix("data:image/png;base64,")

                # base64で受け取った画像データをデコード
                img_binary = base64.b64decode(img_base64)       # binary  <- base64
                jpg=np.frombuffer(img_binary,dtype=np.uint8)    # jpg     <- binary
                img=cv2.imdecode(jpg, cv2.IMREAD_COLOR)         # raw img <- jpg

                self.textures.append(img)
            
            return self.textures
        else:
            return None
        
    class Element():
        def __init__(self, raw):
            self.raw = raw
            self.new = raw

            self.texture_index = raw["faces"]["north"]["texture"]
            self.box_uv = raw["box_uv"]

            self.faces = {}

            dict = self.raw["faces"]

            for index, (key, value) in enumerate(dict.items()):
                self.faces[key] = self.Face(value)
            
            self.width = self.faces["north"].width + self.faces["east"].width + self.faces["east"].width + self.faces["south"].width
            self.height = self.faces["up"].height + self.faces["north"].height
        
        def generateBoxUVCord(self,x,y):
            new_faces = self.raw["faces"]

            # up
            anchor = [x + self.faces["east"].width , y]

            vertex = self.faces["up"].setVertex(anchor[0],anchor[1])
            uv_pos = self.faces["up"].directionVector(vertex)

            new_faces["up"]["uv"] = [uv_pos[0][0],uv_pos[0][1],uv_pos[1][0],uv_pos[1][1]]

            # down
            anchor = [x + self.faces["east"].width  + self.faces["north"].width, y]
            
            vertex =  self.faces["down"].setVertex(anchor[0],anchor[1])
            uv_pos = self.faces["down"].directionVector(vertex)

            new_faces["down"]["uv"] = [uv_pos[0][0],uv_pos[0][1],uv_pos[1][0],uv_pos[1][1]]

            # east
            anchor = [x, y + self.faces["up"].height]
            
            vertex =  self.faces["east"].setVertex(anchor[0],anchor[1])
            uv_pos = self.faces["east"].directionVector(vertex)

            new_faces["east"]["uv"] = [uv_pos[0][0],uv_pos[0][1],uv_pos[1][0],uv_pos[1][1]]

            # north
            anchor = [x + self.faces["east"].width, y + self.faces["up"].height]
            
            vertex = self.faces["north"].setVertex(anchor[0],anchor[1])
            uv_pos = self.faces["north"].directionVector(vertex)

            new_faces["north"]["uv"] = [uv_pos[0][0],uv_pos[0][1],uv_pos[1][0],uv_pos[1][1]]

            # west
            anchor = [x + self.faces["east"].width  + self.faces["north"].width, y + self.faces["up"].height]
            
            vertex =  self.faces["west"].setVertex(anchor[0],anchor[1])
            uv_pos = self.faces["west"].directionVector(vertex)

            new_faces["west"]["uv"] = [uv_pos[0][0],uv_pos[0][1],uv_pos[1][0],uv_pos[1][1]]
    
            # south
            anchor = [x + self.faces["east"].width  + self.faces["north"].width + self.faces["west"].width, y + self.faces["up"].height]
            
            vertex = self.faces["south"].setVertex(anchor[0],anchor[1])
            uv_pos = self.faces["south"].directionVector(vertex)

            new_faces["south"]["uv"] = [uv_pos[0][0],uv_pos[0][1],uv_pos[1][0],uv_pos[1][1]]

            return new_faces

        class Face:
            def __init__(self,raw_face):
                self.vec = [(raw_face["uv"][2] - raw_face["uv"][0]),(raw_face["uv"][3]-raw_face["uv"][1])]

                self.width = abs(self.vec[0])
                self.height = abs(self.vec[1])

                self.vertex = self.setVertex(min(raw_face["uv"][0],raw_face["uv"][2]),min(raw_face["uv"][1],raw_face["uv"][3]))

                self.checkDirection()
            
            def checkDirection(self):
                if self.vec[0] >= 0:
                    if self.vec[1] > 0:
                        self.direction = "right_up"
                    else:
                        self.direction = "right_down"
                else:
                    if self.vec[1] > 0:
                        self.direction = "left_up"
                    else:
                        self.direction = "left_down"
            
            def setVertex(self,x,y):
                vertex = []
                vertex.insert(0,[x,y])
                vertex.insert(1,[x + self.width, y])
                vertex.insert(2,[x, y + self.height])
                vertex.insert(3,[x + self.width, y + self.height])

                return vertex

            def directionVector(self,vertex):
                if self.direction == "right_up":
                    return [vertex[2],vertex[1]]
                elif self.direction == "right_down":
                    return [vertex[0],vertex[3]]
                elif self.direction == "left_up":
                    return [vertex[3],vertex[0]]
                elif self.direction == "left_down":
                    return [vertex[1],vertex[2]]

# Lを抑える最小の2のべき乗を求める
def next_power_of_two(L):
    # 整数型に型変換
    L = int(L)

    if L <= 0:
        return 1  # 0や負数の場合、2^0 = 1 を返す
    return 1 << (L - 1).bit_length()

# 1辺の長さ L の正方形に長方形集合 rectangles が入りきるか
def can_pack(L, rectangles) -> bool:
    x = 0
    y = 0
    shelf_height = 0

    for w, h in rectangles:
        if w > L or h > L:
            return False  # 正方形に入らない

        if x + w <= L:
            x += w
            shelf_height = max(shelf_height, h)
        else:
            y += shelf_height
            if y + h > L:
                return False
            x = w
            shelf_height = h
            
    return True

# 与えられた長方形集合が入りきる最小の正方形サイズ
def min_square_size(rectangles):
    # 下限: 最大幅・高さのどちらか
    left = max(max(w for w, h in rectangles), max(h for w, h in rectangles))

    # 上限: 全面を縦か横に並べたとき（単純な合計）
    right = sum(max(w, h) for w, h in rectangles)

    while left < right:
        mid = (left + right) // 2
        if can_pack(mid, rectangles):
            right = mid
        else:
            left = mid + 1
    return left

# サイズLの正方形に長方形集合を配置
def place_rectangles(L, rectangles):
    # 元インデックスを保持して、高さ・幅の降順にソート
    indexed_rects = list(enumerate(rectangles))
    indexed_rects.sort(key=lambda r: (-r[1][1], -r[1][0]))

    x = 0
    y = 0
    shelf_height = 0
    placed_positions = {}

    for idx, (w, h) in indexed_rects:
        if x + w <= L:
            placed_positions[idx] = (x, y)
            x += w
            shelf_height = max(shelf_height, h)
        else:
            y += shelf_height
            if y + h > L:
                return None  # 入りきらない
            x = 0
            shelf_height = h
            placed_positions[idx] = (x, y)
            x += w

    # 出力を元インデックス順に復元
    result = [placed_positions[i] for i in range(len(rectangles))]
    return result

# デバッグ用
def rectangles_visualizer(L, rectangles, positions):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, L)
    ax.set_ylim(0, L)
    ax.set_aspect('equal')
    ax.set_title(f"Packed Rectangles in {L}x{L} Square")

    for idx, ((x, y), (w, h)) in enumerate(zip(positions, rectangles)):
        rect = Rectangle((x, y), w, h, edgecolor='black', facecolor='skyblue')
        ax.add_patch(rect)
        # サイズとインデックスを表示
        ax.text(x + w / 2, y + h / 2 - 0.3, f"{w}×{h}", ha='center', va='center', fontsize=8)
        ax.text(x + w / 2, y + h / 2 + 0.3, f"#{idx}", ha='center', va='center', fontsize=7, color='darkblue')

    ax.grid(True)
    plt.gca().invert_yaxis()
    plt.show()

if __name__ == "__main__":
    main()