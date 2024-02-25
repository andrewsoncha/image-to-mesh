import cv2
import argparse

parser = argparse.ArgumentParser(description='Generate a 3D obj file from one image. 3d model will be a (width, height) array of pilars with each pilar being as tall as pixel value')
parser.add_argument('imageName', metavar='imageName', type=str, help='name of the image file(ex:\'picture.png\')')
parser.add_argument('-wi', metavar='--width', type=int, default=32, help='the width of the 2D pilar array')
parser.add_argument('-he', metavar='--height', type=int, default=32, help='the height of the 2D pilar array')
parser.add_argument('-m', metavar='--maxZVal', type=int, default=20, help='the maximum height of the pilar. The heights of the pilars will be scaled accordingly.')
parser.add_argument('-o', metavar='--output', type=str, default='result.obj', help='Name of the resulting .obj file')
args = parser.parse_args()

target_size = (args.he,args.wi)
imgName = args.imageName
maxHeight = args.m
outputName = args.o        

class Pilar:
    def __init__(self,zVal,leftTopIdx,rightTopIdx,leftBottomIdx,rightBottomIdx):
        self.zVal = zVal
        self.leftTopIdx = leftTopIdx
        self.rightTopIdx = rightTopIdx
        self.leftBottomIdx = leftBottomIdx
        self.rightBottomIdx = rightBottomIdx
    def getUpperCorners(self):
        return [self.leftTop, self.rightTop, self.leftBottom, self.rightBottom]
    def getTopFace(self):
        return [self.leftTopIdx,self.rightTopIdx,self.leftBottomIdx],[self.rightTopIdx,self.rightBottomIdx,self.leftBottomIdx]

def getHorizontalWall(leftPilar, rightPilar):
    tri1 = []
    tri2 = []
    tri1 = [leftPilar.rightTopIdx, leftPilar.rightBottomIdx, rightPilar.leftBottomIdx]
    tri2 = [leftPilar.rightTopIdx, rightPilar.leftTopIdx, rightPilar.leftBottomIdx]
    return tri1, tri2

def getVerticalWall(upperPilar, bottomPilar):
    tri1 = []
    tri2 = []
    tri1 = [upperPilar.leftBottomIdx, upperPilar.rightBottomIdx, bottomPilar.leftTopIdx]
    tri2 = [upperPilar.rightBottomIdx, bottomPilar.rightTopIdx, bottomPilar.leftTopIdx]
    return tri1, tri2

def generateFourCorners(x,y,z):
    return [[x,y,z],[x+1,y,z],[x,y+1,z],[x+1,y+1,z]]

vertexList = []
indexList = []
pilarList = []

squareList = []

img = cv2.imread(imgName, cv2.IMREAD_COLOR)
gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
resize_img = cv2.resize(gray_img, (target_size[1],target_size[0]))

base_height = 10
idxCnt = 0
for i in range(target_size[0]):
    rowPilar = []
    for j in range(target_size[1]):
        zVal = resize_img[i][j]/255*maxHeight
        newCorners = generateFourCorners(i,j,zVal)
        vertexList.extend(newCorners)
        newPilarObj = Pilar(zVal,idxCnt,idxCnt+1,idxCnt+2,idxCnt+3)
        idxCnt+=4
        
        topTri1, topTri2 = newPilarObj.getTopFace()
        indexList.append(topTri1)
        indexList.append(topTri2)
        rowPilar.append(newPilarObj)
    pilarList.append(rowPilar)

for i in range(target_size[0]-1):
    for j in range(target_size[1]):
        horTri1, horTri2 = getHorizontalWall(pilarList[i][j],pilarList[i+1][j])
        indexList.append(horTri1)
        indexList.append(horTri2)


for i in range(target_size[0]):
    for j in range(target_size[1]-1):
        verTri1,verTri2 = getVerticalWall(pilarList[i][j],pilarList[i][j+1])
        indexList.append(verTri1)
        indexList.append(verTri2)

topRow = []
bottomRow = []
for i in range(target_size[1]):
    newTopCorners = generateFourCorners(-1,i,0)
    vertexList.extend(newTopCorners)
    newTopPilar = Pilar(0,idxCnt,idxCnt+1,idxCnt+2,idxCnt+3)
    topRow.append(newTopPilar)
    idxCnt+=4
    newBottomCorners = generateFourCorners(target_size[0],i,0)
    vertexList.extend(newBottomCorners)
    newBottomPilar = Pilar(0,idxCnt,idxCnt+1,idxCnt+2,idxCnt+3)
    bottomRow.append(newBottomPilar)
    idxCnt+=4

leftColumn = []
rightColumn = []
leftTopIdx = idxCnt
rightTopIdx = idxCnt+4
for i in range(target_size[0]):
    newLeftCorners = generateFourCorners(i,-1,0)
    vertexList.extend(newLeftCorners)
    newLeftPilar = Pilar(0,idxCnt,idxCnt+1,idxCnt+2,idxCnt+3)
    leftColumn.append(newLeftPilar)
    idxCnt+=4
    newRightCorners = generateFourCorners(i,target_size[1],0)
    vertexList.extend(newRightCorners)
    newRightPilar = Pilar(0,idxCnt,idxCnt+1,idxCnt+2,idxCnt+3)
    rightColumn.append(newRightPilar)
    idxCnt+=4
rightBottomIdx = idxCnt-1
leftBottomIdx = idxCnt-5

for i in range(target_size[1]):
    topTri1, topTri2 = getHorizontalWall(topRow[i],pilarList[0][i])
    indexList.append(topTri1)
    indexList.append(topTri2)
    bottomTri1, bottomTri2 = getHorizontalWall(pilarList[target_size[0]-1][i],bottomRow[i])
    indexList.append(bottomTri1)
    indexList.append(bottomTri2)

for i in range(target_size[0]):
    leftTri1, leftTri2 = getVerticalWall(leftColumn[i], pilarList[i][0])
    indexList.append(leftTri1)
    indexList.append(leftTri2)
    rightTri1, rightTri2 = getVerticalWall(pilarList[i][target_size[1]-1], rightColumn[i])
    indexList.append(rightTri1)
    indexList.append(rightTri2)

indexList.append([leftTopIdx, leftBottomIdx, rightBottomIdx])
indexList.append([leftTopIdx, rightTopIdx, rightBottomIdx])

with open(outputName, 'w') as f:
    for vertex in vertexList:
        vertexStr = 'v '+str(float(vertex[0]))+' '+str(float(vertex[1]))+' '+str(float(vertex[2]))+'\n'
        f.write(vertexStr)
    for face in indexList:
        faceStr = 'f '+str(face[0]+1)+' '+str(face[1]+1)+' '+str(face[2]+1)+'\n'
        f.write(faceStr)