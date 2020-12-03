import sys
from PyQt5.QtWidgets import QApplication, QWidget,QPushButton,QLabel,QLineEdit,QMessageBox
from PyQt5.QtWidgets import QHBoxLayout,QGridLayout,QStackedLayout,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import random 

def sequenceXOR(seq1,seq2):
    a=len(seq1)
    b=len(seq2)
    if(a>b):
        seq2=[0]*(a-b)+seq2
    elif(a<b):
        seq1=[0]*(b-a)+seq1
    idx=0
    result=''
    while(idx<len(seq1)):
        result=result+str(seq1[idx]^seq2[idx])
        idx=idx+1
    idx=0
    while(result[idx]=='0'):
        idx=idx+1
        if(len(result)==idx):
            return ''
    return result[idx:]

def sequeceDivision(str1,str2):
    k=len(str2)
    Q=''
    b=list(map(int, str2))
    while(len(str1)>=k):
        a=list(map(int, str1[:k]))
        tmpResult=sequenceXOR(a,b)
        deltaIdx=k-len(tmpResult)
        str1=tmpResult+str1[k:]
        Q=Q+'1'
            
        if(deltaIdx>1):
            if(len(str1)<k):
                Q=Q+'0'*(len(str1)-len(tmpResult))
            else:
                Q=Q+'0'*(deltaIdx-1)
                
    r=str1
    if(len(r)<k-1):
        r='0'*(k-1-len(r))+r
    return Q,r

def CRCencode(str1,str2):
    str1=str1+'0'*(len(str2)-1)    
    return sequeceDivision(str1,str2)
        
def calc_r(k):
    r = 1
    while 2 ** r - r - 1 < k:
        r += 1
    return r

def calc_k_r(length):
    r = 1
    k=length-r
    while 2 ** r - r - 1 < k:
        r += 1
        k -= 1
    return k,r

def addNoise(srcStr):
    k=len(srcStr)
    pos=random.randint(0,k-1)
    return srcStr[:pos]+str(1-int(srcStr[pos]))+srcStr[pos+1:]


#Hamming matrix H:r*(r+k) 2*r以及包含该分量处为1,H*x=0
def HammingEncode(srcStr):
    k=len(srcStr)
    r=calc_r(k)

    result=['0']*(r+k)
    rCount=0
    idx=0
    for i in range(r+k):
        if(2**rCount==i+1):
            rCount=rCount+1
            continue
        result[i]=srcStr[idx]
        idx=idx+1
    H=[[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
       [0,1,1,0,0,1,1,0,0,1,1,0,0,1,1],
       [0,0,0,1,1,1,1,0,0,0,0,1,1,1,1],
       [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]]
    idx=0
    while(idx<r):
        tmp=list(map(int, result))
        bitresult=0
        for i in range(r+k):
            bitresult=bitresult^(tmp[i]*H[idx][i]) 
        result[2**idx-1]=str(bitresult)
        idx=idx+1
    return ''.join(result)

def HammingDecode(encodeStr):
    k,r=calc_k_r(len(encodeStr))

    result=['0']*(k)
    rCount=0
    idx=0
    for i in range(r+k):
        if(2**rCount==i+1):
            rCount=rCount+1
            continue
        result[idx]=encodeStr[i]
        idx=idx+1
    return ''.join(result)

def HammingCheck(encodeStr):
    k,r=calc_k_r(len(encodeStr))
    H=[[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
       [0,1,1,0,0,1,1,0,0,1,1,0,0,1,1],
       [0,0,0,1,1,1,1,0,0,0,0,1,1,1,1],
       [0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]]
    idx=r-1
    checks=0
    tmp=list(map(int, encodeStr))
    while(idx>=0):       
        bitresult=0
        for i in range(r+k):
            bitresult=bitresult^(tmp[i]*H[idx][i]) 
        checks=2*checks+bitresult
        idx=idx-1
    
    if(checks!=0):
        encodeStr=encodeStr[:checks-1]+str(1-int(encodeStr[checks-1]))+encodeStr[checks:]
    result=HammingDecode(encodeStr)
    return ''.join(result),checks==0

def preTreatment(srcStr):
    i=0
    result=''
    while(srcStr[i]=='0' and i<len(srcStr)):
        i=i+1
        if(i==len(srcStr)):
            return False,''
    
    while(i<len(srcStr)):
        if(srcStr[i]<'0' or srcStr[i]>'1'):
            return False,''
        result=result+srcStr[i]
        i=i+1
    return True,result

class HammingGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600,400)
        self.grid=QGridLayout()
        self.initialGUI()
                
    def initialGUI(self):
        self.grid.setSpacing(10)
        
        self.srcCodeText=QLabel('编码前')
        self.encodeText=QLabel('编码后')
        self.wrongText=QLabel('随机1bit错误')
        self.decodeText=QLabel('解码后')
        
        self.encodeAct=QPushButton('编码')
        self.wrongAct=QPushButton('噪声')
        self.decodeAct=QPushButton('解码')
        self.resetAct=QPushButton('重置')
        
        
        self.srcCode=QLineEdit()
        self.srcCode.setAlignment(Qt.AlignCenter)
        self.srcCode.setPlaceholderText('二进制字符串，最长11')
        self.srcCode.setMaxLength(11)
        
        self.encode=QLineEdit()
        self.encode.setReadOnly(True)
        self.encode.setText('')
        self.encode.setPlaceholderText('未收到原始数据')
        self.encode.setAlignment(Qt.AlignCenter)
        
        self.wrong=QLineEdit()
        self.wrong.setReadOnly(True)
        self.wrong.setText('')
        self.wrong.setPlaceholderText('未收到编码后数据')
        self.wrong.setAlignment(Qt.AlignCenter)
        
        self.decode=QLineEdit()
        self.decode.setReadOnly(True)
        self.decode.setText('')
        self.decode.setPlaceholderText('未收到编码后数据')
        self.decode.setAlignment(Qt.AlignCenter)
        
        self.encodeAct.clicked.connect(self.encodeClick)
        self.decodeAct.clicked.connect(self.decodeClick)
        self.resetAct.clicked.connect(self.resetClick)
        self.wrongAct.clicked.connect(self.wrongClick)
        
        self.grid.addWidget(self.srcCodeText, 1, 0)
        self.grid.addWidget(self.srcCode, 1, 1)
        self.grid.addWidget(self.encodeAct, 1, 2)
        
        self.grid.addWidget(self.encodeText, 2, 0)
        self.grid.addWidget(self.encode, 2, 1)
        self.grid.addWidget(self.wrongAct, 2, 2)
        
        self.grid.addWidget(self.wrongText, 3, 0)
        self.grid.addWidget(self.wrong, 3, 1)
        self.grid.addWidget(self.decodeAct, 3, 2)
        
        self.grid.addWidget(self.decodeText, 4, 0)
        self.grid.addWidget(self.decode, 4, 1)
        self.grid.addWidget(self.resetAct, 4, 2)
                
        self.setLayout(self.grid)
        
    def refresh(self):
        self.srcCode.setText('')
        self.encode.setText('')
        self.wrong.setText('')
        self.decode.setText('')
               
    def encodeClick(self):
        preSrcCodeText=self.srcCode.text()
        if(len(preSrcCodeText)==0):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入2进制字符串，最长为11！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        flag,srcCodeText=preTreatment(preSrcCodeText)
        if(flag==False):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入2进制字符串，最长为11！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
                
        encodeText=HammingEncode(srcCodeText)
        self.wrong.setText(encodeText)
        self.encode.setText(encodeText)
                
    def wrongClick(self):
        encodeText=self.wrong.text()
        if(len(encodeText)==0):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入2进制字符串，最长为11！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        newencodeText=addNoise(encodeText)
        self.wrong.setText(newencodeText)
                
    def decodeClick(self):
        encodeText=self.wrong.text()
        if(len(encodeText)==0):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入2进制字符串，最长为11！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        
        decodeText,flag=HammingCheck(encodeText)
        
        if(flag):
            self.decode.setText('校验结果为'+decodeText+'，正确')
        else:
            self.decode.setText('校验出错且纠错结果为'+decodeText)
        
        
    def resetClick(self):
        self.refresh()
        

class CRCGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600,400)
        self.grid=QGridLayout()
        self.initialGUI()
        
    def initialGUI(self):
        self.grid.setSpacing(10)
        
        self.srcCodeText=QLabel('编码前')
        self.ponyText=QLabel('生成多项式')
        self.encodeText=QLabel('编码后')    
        self.wrongText=QLabel('随机1bit错误')    
        self.decodeText=QLabel('解码后')
        
        self.encodeAct=QPushButton('编码')
        self.wrongAct=QPushButton('噪声')
        self.decodeAct=QPushButton('解码')
        self.resetAct=QPushButton('重置')
        
        
        self.srcCode=QLineEdit()
        self.srcCode.setAlignment(Qt.AlignCenter)
        self.srcCode.setText('')
        self.srcCode.setPlaceholderText('二进制字符串，最长11')
        self.srcCode.setMaxLength(11)
        
        self.pony=QLineEdit()
        self.pony.setText('')
        self.pony.setPlaceholderText('二进制字符串，最长11')
        self.pony.setAlignment(Qt.AlignCenter)
        self.pony.setMaxLength(11)
        
        self.encode=QLineEdit()
        self.encode.setReadOnly(True)
        self.encode.setText('')
        self.encode.setPlaceholderText('未收到原始数据')
        self.encode.setAlignment(Qt.AlignCenter)
        
        self.wrong=QLineEdit()
        self.wrong.setReadOnly(True)
        self.wrong.setText('')
        self.wrong.setPlaceholderText('未收到编码后数据')
        self.wrong.setAlignment(Qt.AlignCenter)
        
        self.decode=QLineEdit()
        self.decode.setReadOnly(True)
        self.decode.setText('')
        self.decode.setPlaceholderText('未收到编码后数据')
        self.decode.setAlignment(Qt.AlignCenter)
        
        self.encodeAct.clicked.connect(self.encodeClick)
        self.wrongAct.clicked.connect(self.wrongClick)
        self.decodeAct.clicked.connect(self.decodeClick)
        self.resetAct.clicked.connect(self.resetClick)
        
        self.grid.addWidget(self.srcCodeText, 1, 0)
        self.grid.addWidget(self.srcCode, 1, 1)     
        
                
        self.grid.addWidget(self.ponyText, 2, 0)
        self.grid.addWidget(self.pony, 2, 1)
        self.grid.addWidget(self.encodeAct, 2, 2)
        
        
        self.grid.addWidget(self.encodeText, 3, 0)
        self.grid.addWidget(self.encode, 3, 1)
        self.grid.addWidget(self.wrongAct, 3, 2)
        
        self.grid.addWidget(self.wrongText, 4, 0)
        self.grid.addWidget(self.wrong, 4, 1)
        self.grid.addWidget(self.decodeAct, 4, 2)
        
        
        self.grid.addWidget(self.decodeText, 5, 0)
        self.grid.addWidget(self.decode, 5, 1)
        self.grid.addWidget(self.resetAct, 5, 2)
                
        self.setLayout(self.grid)
        
    def refresh(self):
        self.srcCode.setText('')
        self.encode.setText('')
        self.pony.setText('')
        self.pony.setReadOnly(False)
        self.decode.setText('')
    
    def encodeClick(self):
        preSrcCodeText=self.srcCode.text()
        prePonyText=self.pony.text()
        if(len(preSrcCodeText)==0):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入合法2进制字符串！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        elif(len(prePonyText)<=1):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入合法生成多项式！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
            
        flag1,srcCodeText=preTreatment(preSrcCodeText)
        flag2,ponyText=preTreatment(prePonyText)
        if(flag1==False):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入合法2进制字符串！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        elif(flag2==False):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入合法生成多项式！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return    
        _,r=CRCencode(srcCodeText, ponyText) 
        codeText=srcCodeText+r
        self.encode.setText(codeText)
        self.wrong.setText(codeText)
        self.pony.setReadOnly(True)
        
    def decodeClick(self):
        encodeText=self.wrong.text()
        prePonyText=self.pony.text()
        if(len(encodeText)==0 or len(prePonyText)==0):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入合法进制字符串与生成多项式！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        _,r=sequeceDivision(encodeText,prePonyText)
        if(r.count('0')!=len(r)):
            self.decode.setText('校验结果为'+r+',有误')
        else:
            self.decode.setText('校验结果为'+r+',正确')
        
    def wrongClick(self):
        encodeText=self.wrong.text()
        if(len(encodeText)==0):
            errInfo=QMessageBox.critical(self, '输入错误', '请输入2进制字符串，最长为11！', QMessageBox.Yes)
            if(errInfo==QMessageBox.Yes):
                self.refresh()
                return
        newencodeText=addNoise(encodeText)
        self.wrong.setText(newencodeText)    
        
    def resetClick(self):
        self.refresh()

class mainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.Horizon=QHBoxLayout()
        self.initialGUI()
        self.resize(700,400)
        self.setWindowIcon(QIcon('icon.jpg'))
        self.setWindowTitle('计网实验')
        
    def initialGUI(self):
        self.stkwindow=QWidget()
        self.choosewindow=QWidget()
        
        self.choose=QVBoxLayout()
        self.stk=QStackedLayout()
        
        self.HammingAct=QPushButton('哈明编码')
        self.HammingAct.setObjectName('Hamming')
        self.CRCAct=QPushButton('CRC解码')
        self.CRCAct.setObjectName('CRC')
        
        self.HammingContent=HammingGUI()
        self.CRCContent=CRCGUI()
        
        self.choose.addWidget(self.HammingAct)
        self.choose.addWidget(self.CRCAct)
        self.choosewindow.setLayout(self.choose)
        
        self.stk.addWidget(self.HammingContent)
        self.stk.addWidget(self.CRCContent)
        self.stkwindow.setLayout(self.stk)
        
        self.Horizon.addWidget(self.choosewindow)
        self.Horizon.addWidget(self.stkwindow)
        
        self.HammingAct.clicked.connect(self.chooseAlg)
        self.CRCAct.clicked.connect(self.chooseAlg)
        
        self.setLayout(self.Horizon)
        
        self.stk.setCurrentWidget(self.HammingContent)
        
    def chooseAlg(self):
        dic={'Hamming':0,'CRC':1}
        select=dic[self.sender().objectName()]
        if(select==0):
            self.stk.setCurrentWidget(self.HammingContent)
        else:
            self.stk.setCurrentWidget(self.CRCContent)
        
             
if __name__ == '__main__':
    app = QApplication([])
    
    w = mainGUI()
    w.show()
    
    sys.exit(app.exec_())