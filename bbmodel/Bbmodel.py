import os
import tkinter
import tkinter.filedialog
import json

from component import Texture
from component import Element

class Bbmodel:
    def __init__(self,filePath):
        # load file
        with open(filePath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # load texture
        if "textures" in self.data:
            self.textures = []
            for x in self.data["textures"]:
                self.textures.append(Texture(x))

        # load elements
        if "elements" in self.data:
            self.elements = []
            for x in self.data["elements"]:
                self.elements.append(Element(x, self.textures, self.scale_factor))


    def initialize(self):
        self.scale_factor = []
        for value in self.data["textures"]:
            self.scale_factor.append(int(value["width"] / value["uv_width"]))

        self.getTextures()

    @classmethod
    def loadFromFile(cls):
        widget = tkinter.Tk()
        widget.withdraw()
        fileType = [("BlockBench Model","*.bbmodel")]
        iDir = os.path.abspath(os.path.dirname(__file__))

        filePath = tkinter.filedialog.askopenfilename(filetypes = fileType,initialdir = iDir)

        if os.path.exists(filePath):
            try:
                return cls(filePath)
            
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