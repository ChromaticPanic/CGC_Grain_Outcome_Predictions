import csv, sys, re


class CSVBorderReader:
    SYS_MAX_INT = 2147483647

    def __init__(self, pathToData='./data/'):
        csv.field_size_limit(CSVBorderReader.SYS_MAX_INT)
        self.input = [] # input is a 2D array: primary index refers to rows, secondary index refers to columns
        self.pathToData = pathToData


    def read(self, filename):
        try:
            with open(self.pathToData + filename, newline='') as inputFile:
                csvReader = csv.reader(inputFile, delimiter=',')
        
                for row in csvReader:
                    self.input.append(row)
        except:
            self.input = []

    def getGISBorders(self, createCSV=False):
        provinces = []  # holds the province abbreviation is parallel to borders
        borders = []    # holds each provinces borders is parallel to provinces
        output = None   # is None if script fails or returns a tuple of the processed data (province, border)

        if(self.input):
            provinces, borders = self.__processInput(self.input)
            borders = self.__conformBorders(borders)

            if(self.hasValidProvinces(provinces) and self.hasValidBorders(borders)):
                output = self.__processOutput(provinces, borders, createCSV)

        return output

    def __processInput(self, inputRow):
        provinces = []      # holds the province abbreviation is parallel to borders
        borders = []        # holds each provinces borders is parallel to provinces
        currProv = -1       # set to -1 because we immedatiely will increment on our first iteration
        combinedCols = ''   # used to combine columns in instance of incomplete border data

        # input is a 2D array: primary index refers to rows, secondary index refers to columns
        # starts at 1 to skip over headers at row 0
        for i in range(1, len(inputRow)):
            if(self.__isProvince(inputRow[i][0])):    # found a province, store name and borders (b/c of CSV limitations may not be complete)
                provinces.append(inputRow[i][0])
                borders.append(inputRow[i][1])
                currProv += 1 
            else:                                   # found an instance of contiued data, scrap if empty else append to the previous province
                if(inputRow[i][0]):                 # if data is not empty proceed with processing
                    combinedCols = ''

                    for col in inputRow[i]:         # add all columns together (start of data is all housed in a single cell)
                        if(col):                    # if data is not empty add it
                            combinedCols += col + ','
                    borders[currProv] += combinedCols[:-1] + ')))'

        return provinces, borders

    def __isProvince(self, string):
        return len(string) == 2 and re.search('[A-Z]{2}', string)

    def __conformBorders(self, borders):
        for i in range(0, len(borders)):
            borders[i] = borders[i].replace('\"', '')           # some rows contained ", remove them
            borders[i] = self.__enforceEndParenthesis(borders[i])    # ensures all border data ends with the correct number of parenthesis (3)

            # ensure borders are multipolygons (some were simply polygons, which themselves are valid multipolygons)
            if(borders[i][0] == 'P'):
                borders[i] = re.sub('POLYGON ', 'MULTIPOLYGON (', borders[i])

        return borders

    def __enforceEndParenthesis(self, border):
        enforcedBorder = border     # by default we will assume the current border satisfies our requirements
        currChar = len(border) - 1  # holds our position in the data (starts at the end)
        numParenthesis = 0          # holds the count of closing parenthesis
        numToCorrect = 0            # the number of parenthesis need to be removed

        while(border[currChar] == ')'):
            numParenthesis += 1
            currChar -= 1

        numToCorrect = numParenthesis - 3   # all data will contain atleast 3 because of data processing (line 51)
        if(numToCorrect):   # If we have parenthesis to correct (string[:0] has undesired behavior)
            enforcedBorder = border[:-numToCorrect]

        return enforcedBorder

    def hasValidBorders(self, borders):
        isValid = True

        if(not borders):
            isValid = False
        else:
            for border in borders:
                if(not border):
                    isValid = False
                    break

            for border in borders:
                if(not self.__hasValidParenthesis(border)):
                    isValid = False
                    break

            for border in borders:
                if(not re.match('MULTIPOLYGON', border)):
                    isValid = False
                    break        

        return isValid

    def hasValidProvinces(self, provinces):
        isValid = True

        if(not provinces):
            isValid = False
        else:
            for province in provinces:
                if(not provinces):
                    isValid = False
                    break

            for province in provinces:
                if(not self.__isProvince(province)):
                    isValid = False
                    break   

        return isValid

    def __hasValidParenthesis(self, border):
        unsatisfiedParenthesis = 0  # holds the number of opening parenthesis (+1) and closing parenthesis (-1)

        for char in border:
            if(char == '('):
                unsatisfiedParenthesis += 1
            elif(char == ')'):
                unsatisfiedParenthesis -= 1

        return unsatisfiedParenthesis == 0  # all parenthesis should be satisfied

    def __processOutput(self, provinces, borders, createCSV):
        output = []         # returns output data (province, border)
        
        for i in range(0, len(provinces)):
            output.append((provinces[i], borders[i]))
            
        if(createCSV):
            with open('boundaries.csv', 'w', newline='') as outputFile:
                csvwriter = csv.writer(outputFile, delimiter=',')
                csvwriter.writerows([provinces, borders])

        return output