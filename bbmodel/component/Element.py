class Element():
        def __init__(self, data, scale_factor: int = 1):
            self.data = data
            self.scale_factor = scale_factor

            self.pos_from = data["from"]
            self.pos_to = data["to"]

            self.isBoxUV = data["box_uv"]

            self.faces = []
            for key, value in dict.items():
                self.faces.append(Face(value,key))
            
            #0:north,1:east,2:south,3:west,4:up,5:down
            self.width = self.faces[0].width + self.faces[1].width + self.faces[2].width + self.faces[3].width
            self.height = self.faces[0].height + self.faces[4].height

        def convertToBoxUV(self,origin):
            x = origin[0]
            y = origin[1]
            
            # 各Faceごとのアンカーポイントを設定
            anchor = []
            anchor.append([x + self.faces[3].width, y +self.faces[4].height])                                                   #0:north
            anchor.append([x, y + self.faces[4].height])                                                                        #1:east
            anchor.append([x + (self.faces[3].width  + self.faces[0].width + self.faces[3].width), y + self.faces[4].height])   #2:south
            anchor.append([x + (self.faces[3].width  + self.faces[0].width), y + self.faces[4].height])                         #3:west
            anchor.append([x + self.faces[3].width , y])                                                                        #4:up
            anchor.append([x + (self.faces[3].width  + self.faces[0].width), y])                                                #5:down

            for index, face in enumerate(self.faces):
                face.anchor = anchor[index]
                face.vertex = face.getVertex(face.anchor,face.width,face.height)
                face.uv = face.getUV()
        
        def apply(self):
            pass

class Face():
    def __init__(self,data,name,scale_factor : int = 1):
        self.data = data
        self.name = name
        self.texture = data["texture"]

        self.scale_factor = scale_factor

        self.uv_vec = [scale_factor*(data["uv"][2] - data["uv"][0]),scale_factor*(data["uv"][3]-data["uv"][1])]
        self.direction = self.checkDirection(self.uv_vec)

        self.width = abs(scale_factor*self.uv_vec[0])
        self.height = abs(scale_factor*self.uv_vec[1])

        self.anchor = [scale_factor*min(data["uv"][0],data["uv"][2]),scale_factor*min(data["uv"][1],data["uv"][3])]
        self.vertex = self.getVertex(self.anchor,self.width,self.height)
        self.uv = self.getUV()
    
    @staticmethod
    def checkDirection(vector):
        if vector[0] >= 0:
            if vector[1] > 0:
                return "right_up"
            else:
                return "right_down"
        else:
            if vector[1] > 0:
                return "left_up"
            else:
                return "left_down"
    
    @staticmethod
    def getVertex(anchor,width,height):
        x = anchor[0]
        y = anchor[1]

        vertex = []
        vertex.append([x,y])
        vertex.append([x + width, y])
        vertex.append([x, y + height])
        vertex.append([x + width, y + height])

        return vertex

    def getUV(self):
        if self.direction == "right_up":
            return [self.vertex[2][0],self.vertex[2][1],self.vertex[1][0],self.vertex[1][1]]
        elif self.direction == "right_down":
            return [self.vertex[0][0],self.vertex[0][1],self.vertex[3][0],self.vertex[3][1]]
        elif self.direction == "left_up":
            return [self.vertex[3][0],self.vertex[3][1],self.vertex[0][0],self.vertex[0][1]]
        elif self.direction == "left_down":
            return [self.vertex[1][0],self.vertex[1][1],self.vertex[2][0],self.vertex[2][1]]