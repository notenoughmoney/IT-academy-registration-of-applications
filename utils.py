def column(matrix, i): return [row[i] for row in matrix]

def getReasonId(array, text):
    for item in array:
        if item[0] == text:
            return item[1]

def getReasonText(array, id):
    for item in array:
        if item[1] == id:
            return item[0]
