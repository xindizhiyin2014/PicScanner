# 图片扫描工具

import os
import re
import hashlib

from codeUtils import CodeUtils

class PicScanner:
    # 项目路径
    projectPath: str
    # 结果输出路径
    resultPath: str
    # 项目中所有图片的路径组成的数组
    pictures: []
    # 项目中所有的源代码文件
    codeFiles: []
    # 重复的图片的数组
    repeatedPics: []
    codeUtils = CodeUtils()


    def __init__(self, projectPath: str, resultPath: str):
        self.projectPath = projectPath
        self.resultPath = resultPath
        self.pictures = self.__scanAllPictures()
        self.codeFiles = self.__scanAllCodeFiles()
        self.repeatedPics = []

    # 开始扫描
    def scan(self):

        if len(self.pictures) == 0:
            print("没有图片需要扫描处理")
            return False
        file = open(self.resultPath, 'w')
        file.write("**************没有使用的图片：**************\n")
        def handleNoUsePic(picPath: str):
            file.write(picPath)
            file.write("\n")

        file.write("\n")
        result = self.scanNoUsePictures(handleNoUsePic=handleNoUsePic)
        if result == False:
            print("扫描无用图片出现异常")
            file.close()
            return False
        file.write("\n\n\n")
        file.write("**************重复的图片扫描结果：**************\n")
        file.write("\n\n\n")
        def handleRepeatedPic(originPicPath: str, repeatdPath: []):
            originPicLine = "比较的图片:\n" + originPicPath + "\n"
            file.write(originPicLine)
            for path in repeatdPath:
                repeatLine = "重复的图片：\n" + path + "\n"
                file.write(repeatLine)
            file.write("\n")

        result = self.scanRepeatedPictures(handleRepeatedPic)
        if result == False:
            print("扫描重复图片出现异常")
            file.close()
            return False
        file.close()
        return True


    # 扫描无用图片
    #   1，扫描无用png，jpeg，pdf，svg
    def scanNoUsePictures(self, handleNoUsePic):
        for picPath in self.pictures:
            result = False
            if os.path.exists(picPath) == False:
                print("文件不存在:",picPath)
                return False
            if picPath.__contains__("AppIcon.appiconset") == True:
                continue
            if picPath.endswith("png") == True or picPath.endswith("PNG") == True:
                result = self.__confirmPngIsInUse(picPath)
                # print("")
            elif picPath.endswith("jpeg") == True or picPath.endswith("JPEG") == True:
                result = self.__confirmJPEGIsInUse(picPath)
                # print("")
            elif picPath.endswith("pdf") == True or picPath.endswith("PDF") == True:
                result = self.__confirmPDFIsInUse(picPath)
            elif picPath.endswith("svg") == True or picPath.endswith("SVG") == True:
                result = self.__confirmSVGIsInUse(picPath)
                # print("")
            if result == False:
                handleNoUsePic(picPath)
        return True


    # 扫描重复图片
    #  1，扫描重复的png，jpeg，pdf, svg
    def scanRepeatedPictures(self, handleRepeatPic):
        picturesCount = len(self.pictures)
        for index in range(0, picturesCount):
            originPic = self.pictures[index]
            if self.repeatedPics.__contains__(originPic) == True:
                continue
            # App图标不做重复扫描判断
            if originPic.__contains__("AppIcon.appiconset") == True:
                continue
            if os.path.exists(originPic) == False:
                print("文件不存在:",originPic)
                return False
            if index+1 == picturesCount:
                continue
            subPictures = self.pictures[index+1:]
            repeatedPictures = []
            for picPath in subPictures:
                if self.repeatedPics.__contains__(picPath) == True:
                    continue
                # App图标不做重复扫描判断
                if picPath.__contains__("AppIcon.appiconset") == True:
                    continue
                originPicMd5 = self.__getPicMd5(originPic)
                picMd5 = self.__getPicMd5(picPath)
                if originPicMd5 == picMd5:
                    repeatedPictures.append(picPath)
                    self.repeatedPics.append(picPath)
            if len(repeatedPictures) > 0:
                handleRepeatPic(originPic, repeatedPictures)
        return True

    # 将所有的图片扫描出来，并返回
    def __scanAllPictures(self):
        results = []
        def collectPic(picPath:str):
            results.append(picPath)
            return True

        path = os.path.join(self.projectPath, "Pods")
        CodeUtils().enumFileInDir(path=self.projectPath, block=collectPic, extensions=[".png", ".PNG", ".jpeg", ".JPEG", ".pdf", ".PDF", ".svg", ".SVG"], recursive=True, blackPaths=[path])
        return results

    # 将所有的swift文件扫描出来，并返回
    def __scanAllCodeFiles(self):
        results = []
        def collectSwift(codePath: str):
            results.append(codePath)
            return True

        CodeUtils().enumFileInDir(path=self.projectPath, block=collectSwift,
                                  extensions=[".swift", ".xib", ".storyboard"],
                                  recursive=True)
        return results

    # 确定图片是否正在使用中
    def __confirmPngIsInUse(self, picPath: str):
        fileName = self.codeUtils.getFileName(picPath)
        if fileName.endswith("@2x.png") == True:
            fileName = fileName.removesuffix("@2x.png")
        elif fileName.endswith("@3x.png") == True:
            fileName = fileName.removesuffix("@3x.png")
        elif fileName.endswith("@1x.png") == True:
            fileName = fileName.removesuffix("@1x.png")
        elif fileName.__contains__("@") ==True and fileName.endswith(".png") == True:
            components = fileName.split("@")
            fileName = components[0]
        elif fileName.endswith(".png") == True:
            fileName = fileName.removesuffix(".png")

        fileName = self.__adjustFileName(fileName)
        pattern = r'(UIImage\s*(\.init)?\(\s*named:\s*|\s*=.*|return\s+|\:\s*|\(\s*)"' + fileName + r'(.+)?' + r'"'
        result = self.__matchPic(pattern)
        return result

    def __confirmJPEGIsInUse(self, picPath: str):
        fileName = self.codeUtils.getFileName(picPath)
        if fileName.endswith(".jpeg") == True:
            fileName = fileName.removesuffix(".jpeg")
        elif fileName.endswith(".JPEG") == True:
            fileName = fileName.removesuffix(".JPEG")

        fileName = self.__adjustFileName(fileName)
        pattern = r'(UIImage\s*(\.init)?\(\s*named:\s*|\s*=.*|return\s+|\:\s*|\(\s*)"' + fileName + r'(.+)?' + r'"'
        result = self.__matchPic(pattern)
        return result

    def __confirmPDFIsInUse(self, picPath:str):
        fileName = self.codeUtils.getFileName(picPath)
        if fileName.endswith(".pdf") == True:
            fileName = fileName.removesuffix(".pdf")
        elif fileName.endswith(".PDF") == True:
            fileName = fileName.removesuffix(".PDF")

        fileName = self.__adjustFileName(fileName)
        pattern = r'(UIImage\s*(\.init)?\(\s*named:\s*|\s*=.*|return\s+|\:\s*|\(\s*)"' + fileName + r'(.+)?' + r'"'
        result = self.__matchPic(pattern)
        return result

    def __confirmSVGIsInUse(self, picPath: str):
        fileName = self.codeUtils.getFileName(picPath)
        if fileName.endswith(".svg") == True:
            fileName = fileName.removesuffix(".svg")
        elif fileName.endswith(".SVG") == True:
            fileName = fileName.removesuffix(".SVG")
        pattern = r'(SVGManager\.getSVGNode\(with:\s*|\.image\(named:\s*|\s*=.*|return\s+|\:\s*|\(\s*)"' + fileName + r'(.+)?' + r'"'
        result = self.__matchPic(pattern)
        return result

    def __matchPic(self, pattern: str):
        for swiftFile in self.codeFiles:
            oldFile = open(swiftFile, 'r')
            lines = oldFile.readlines()
            oldFile.close()
            lineCount = len(lines)
            for lineNum in range(0, lineCount):
                line = lines[lineNum]
                if len(line) < 10:
                    continue
                if line.startswith("//") == True:
                    continue
                results = re.findall(pattern, line)
                if len(results) == 0:
                    continue
                return True
        return False
    def __getPicMd5(self, path: str):
        limitCount = 5 * 1024 * 1024
        fileSize = os.path.getsize(path)
        md5_hash = hashlib.md5()
        if fileSize < limitCount:
            # 打开文件并读取内容
            with open(path, 'rb') as f:
                data = f.read()
            # 计算MD5值
            md5_hash.update(data)
            md5_value = md5_hash.hexdigest()
            return md5_value
        else:
            # 打开文件并读取内容
            with open(path, 'rb') as f:
                headData = f.read(1024 * 1024)
            # 计算MD5值
            md5_hash.update(headData)
            head_md5_value = md5_hash.hexdigest()

            with open(path, 'rb') as f:
                f.seek(-1024 * 1024, 2)  # 将文件指针移动到文件末尾的前1024*1024个字节处
                tailData = f.read()
            md5_hash.update(tailData)
            tail_md5_value = md5_hash.hexdigest()
            md5_value = head_md5_value + tail_md5_value
            return md5_value

    # 处理动画图片 aa1,aa2,aa3,等形式
    def __adjustFileName(self, fileName: str):
        tmpFileName = fileName
        # 判断图片名字是否是纯数字组成
        result1 = re.match(r'[0-9]+', tmpFileName, flags=0)
        if result1 == None:
            while re.match(r'.*[0-9]+$', tmpFileName, flags=0) != None:
                tail = len(tmpFileName) - 2
                if tail > 0:
                    tmpFileName = tmpFileName[0:tail]
            return tmpFileName
        else:
            return tmpFileName

