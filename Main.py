from PIL import Image

from utils import RectBoxUVAligner
from bbmodel import Bbmodel

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def main():
    original = Bbmodel()
    original.loadFromFile()
    
    elements = original.element

    # すべてのUVテクスチャが入りきる最小のピクセルサイズを計算
    rectangles = []
    for i, elem in enumerate(elements):
        scale_factor = elem.scale_factor[elem.texture_index]
        rectangles.insert(i,(scale_factor*elem.width,scale_factor*elem.height))
    
    L = RectBoxUVAligner.min_square_size(rectangles)
    px = RectBoxUVAligner.next_power_of_two(L)

    # 各UVの基点座標を取得
    anchor = RectBoxUVAligner.place_rectangles(L,rectangles)
    rectangles_visualizer(L,rectangles,anchor)

    # テクスチャを作成
    new_texture = Image.new("RGBA",(px,px),(0,0,0,0))

    # 新しいUV座標を設定し、新しいテクスチャにマッピング
    original.data["elements"] = []
    for i, elem in enumerate(elements):
        elem.new["faces"] = elem.generateBoxUV(anchor[i][0],anchor[i][1],new_texture)
        elem.new["uv_offset"] = [anchor[i][0],anchor[i][1]]
        
        original.data["elements"].append(elem.new)

    # ファイルフォーマットをModded Entityに変更
    original.data["meta"]["model_format"] = "modded_entity"

    new_texture.save("transparent_image.png")
    print(px)
    original.exportFile()

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