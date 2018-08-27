import json, os

def parseFile(filePath=None):
    if filePath == None:
        return None
    elif not os.path.isfile(filePath):
        return None
    else:
        try:
            with open(filePath) as file:
                return parseText(file.read())
        except:
            return None

def parseText(text=''):
    if text == None or text == '':
        return None
    else:
        try:
            jsonData = json.loads(text)
            return jsonData
        except:
            return None