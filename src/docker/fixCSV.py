import csv, sys, re

SYS_MAX_INT = 2147483647

class CSVBorderReader:

    def __init__(self):
        csv.field_size_limit(SYS_MAX_INT)
        self.input = []


    def read(self, filename):
        with open(filename, newline='') as input:
            csvReader = csv.reader(input, delimiter=',')
    
            for row in csvReader:
                self.input.append(row)

    def getGISBorders(self, createCSV=False):
        output = None
        provinces, borders = self.processInput(self.input)
        
        if(self.hasValidData(provinces, borders)):
            output = self.processOutput(provinces, borders, createCSV)
        else:
            print('shit something didnt work')
            sys.exit()

        return output

    def processInput(self, input):
        provinces = []
        borders = []

        for i in range(1, len(input)):
            currProv = -1

            if(self.isProvince(input[i][0])):
                provinces.append(input[i][0])
                borders.append(input[i][1])
                currProv += 1 
            else:
                if(input[i][0]):
                    combinedCols = ''

                    for col in input[i]:
                        if(col):
                            combinedCols += col + ','
                    borders[currProv] += combinedCols[:-1] + '))))'

        return provinces, borders

    def isProvince(self, string):
        return len(string) == 2 and re.search('[A-Z]{2}', string)

    def hasValidData(self, provinces, borders):
        isValid = True

        for i in range(0, len(borders)):
            borders[i] = borders[i].replace('\"', '')

            if(borders[i][0] == 'P'):
                borders[i] = re.sub('POLYGON ', 'MULTIPOLYGON (', borders[i])

            currChar = len(borders[i]) - 1
            numParenthesis = 0
            while(borders[i][currChar] == ')'):
                numParenthesis += 1
                currChar -= 1

            borders[i] = borders[i][:-(numParenthesis - 3)] # :-0 breaks this and removes a fuck ton of characters

        #add parenthesis count
            if(not self.hasValidParenthesis(borders)):
                print('case ' + str(i) + ' failed')
                isValid = False
                break

        return isValid

    def hasValidParenthesis(self, border):
        unsatisfiedParenthesis = 0

        for char in border:
            if(char == '('):
                unsatisfiedParenthesis += 1
            elif(char == ')'):
                unsatisfiedParenthesis -= 1

        return unsatisfiedParenthesis == 0

    def countParenthesis(self, currProvince):
        currPosi = len(currProvince) - 2
        numParenthesis = 0
            
        while(currProvince[currPosi] == ')'):
            print(currProvince[currPosi])
            numParenthesis += 1
            currPosi -= 1

        sys.exit()

        return numParenthesis

    def processOutput(self, provinces, borders, createCSV):
        outputFile = None
        output = []
        
        for i in range(0, len(provinces)):
            output.append((provinces[i], borders[i]))
            
        if(createCSV):
            with open('boundaries.csv', 'w', newline='') as outputFile:
                csvwriter = csv.writer(outputFile, delimiter=',')
                csvwriter.writerows([provinces, borders])

        return output, outputFile
    
# remove space
# verify parenthesis
# verify everything is multi