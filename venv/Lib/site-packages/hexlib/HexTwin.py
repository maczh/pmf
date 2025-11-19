class HexTwin():
    def __init__(self, path="") -> None:
        self.path = path
        self.rows = []
        if(path != ""):
            self.__read()
    
    def __read(self):
        with open(self.path, "rb") as f:
            offset = 0
            while True:
                data = f.read(16)
                if(not data):
                    break
                self.__process(offset, data)
                offset += 16  

    def __process(self, offset, data):
        byteArr = bytearray(data)
        isZeroRow = all(v == 0 for v in byteArr)
        isNonAsciiRow = all(not(v >= 32 and v <= 126) for v in byteArr)
        self.rows.append((offset, byteArr, isZeroRow, isNonAsciiRow))          

    def fromBytes(bytes_, offset=0):
        twin = HexTwin()
        offset_ = offset
        splittedBytes = [bytes_[i:i + 16] for i in range(0, len(bytes_), 16)]
        for b_ in splittedBytes:
            twin.__process(offset_, b_)
            offset_ += 16  
        return twin 
    
    def fromOffset(path, offset=0, noOfBytes=1):
        twin = None
        with open(path, "rb") as f:
            f.seek(offset, 0)
            bytes_ = f.read(noOfBytes)
            twin = HexTwin.fromBytes(bytes_, offset)
        return twin


