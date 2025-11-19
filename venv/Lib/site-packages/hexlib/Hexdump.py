class Hexdump():
    def __init__(self) -> None:
        self.filterZeroRows = False
        self.filterNonAsciiRows = False
        self.zeroRowCounter = 0
        self.nonAsciiRowCounter = 0
        self.fileHandle = None

    def filter(self, filterZeroRows=False, filterNonAsciiRows=False):
        self.filterZeroRows = filterZeroRows
        self.filterNonAsciiRows = filterNonAsciiRows

    def printTwin(self, outfile, twin):
        self.fileHandle = open(outfile, "a")
        self.__printHexHeader()
        self.__printHexRows(twin.rows)
        self.fileHandle.close()

    def __printHexHeader(self):
        h = "{:16}   {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2} {:2}    {:16}".format("          Offset", "00", "01", "02", "03", "04", "05",
                                                                                                                            "06", "07", "08", "09", "0A", "0B",
                                                                                                                            "0C", "0D", "0E", "0F", "ASCII")
        self.fileHandle.write(h + "\n")
        self.fileHandle.write(("-"*16) + "   " + ("-"*47) + "    " + ("-"*16) +" \n")

    def __printHexRows(self, rows):
        if(self.filterNonAsciiRows):
            self.__filterNonAscii(rows)    
        elif(self.filterZeroRows):
            self.__filterZero(rows)  
        else:
            for row in rows:
                self.__printHexRow(row)

    def __filterNonAscii(self, rows):
        for i in range(0, len(rows)):
            isRowNonAscii = rows[i][3]
            row = rows[i]
            if(isRowNonAscii): 
                self.nonAsciiRowCounter += 1
            elif(not isRowNonAscii):
                if(self.nonAsciiRowCounter > 0):
                    self.__printPlaceholder("{:,}".format(self.nonAsciiRowCounter) + " non ASCII rows")
                    self.nonAsciiRowCounter = 0
                self.__printHexRow(row)
                
            if(len(rows)-1 == i and self.nonAsciiRowCounter > 0):
                self.__printPlaceholder("{:,}".format(self.nonAsciiRowCounter) + " non ASCII rows")
        
    def __filterZero(self, rows):
        for i in range(0, len(rows)):
            isRowZero = rows[i][2]
            row = rows[i]
            if(isRowZero): 
                self.zeroRowCounter += 1
            elif(not isRowZero):
                if(self.zeroRowCounter > 0):
                    self.__printPlaceholder("{:,}".format(self.zeroRowCounter) + " zero rows")
                    self.zeroRowCounter = 0
                self.__printHexRow(row)
                
            if(len(rows)-1 == i and self.zeroRowCounter > 0):
                self.__printPlaceholder("{:,}".format(self.zeroRowCounter) + " zero rows")
    

    def __printHexRow(self, row):
        formatStr = "{:16}   {:47}    {:16}"
        offset = hex(row[0]).split('x')[-1].rjust(16, "0").upper()
        hexValues = row[1].hex(" ").upper()
        asc = "".join(chr(v) if (v >= 32 and v <= 126) else "." for v in row[1])
        r = formatStr.format(offset, hexValues, asc)
        self.fileHandle.write(r + " \n")

    def __printPlaceholder(self, text):
        msg = f"   Skipped {text} "
        self.fileHandle.write("\n" + ("-"*15) + ">" + msg + " \n\n")