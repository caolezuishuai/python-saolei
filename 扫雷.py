#coding: utf-8
 
__author__ = "小冰|lovingxiaobing"
__email__ = "865741184@qq.com|[email]lovingxiaobing@qq.com[/email]"
__note__ = """
* 扫雷小游戏
* 需要python3.x以上
* 需要安装PyQt5
* pip install PyQt5
"""
 
import sys
 
try:
    import PyQt5
except ImportError:
    import tkinter
    from tkinter import messagebox
    err_str = "请安装PyQt5后再打开: pip install PyQt5"
    messagebox.showerror("模块错误!", err_str)
    raise ImportError(err_str)
    sys.exit()
 
 
from random import randint
from PyQt5.QtWidgets import \
    QApplication,           \
    QWidget,                \
    QPushButton,            \
    QLCDNumber,             \
    QDesktopWidget,         \
    QMessageBox
from PyQt5.QtCore import Qt
 
 
class Mine(object):
    mine = 9
    no_mine = 0
    n_mine = 10
    width = 10
    height = 10
 
    def __init__(self, width=10, height=10, nMines=10):
        self.map = []
        for _ in range(height):
            t_line = []
            for _ in range(width):
                t_line.append(self.no_mine)
            self.map.append(t_line)
         
        self.width = width
        self.height = height
        self.n_mine = nMines
 
        self.remix()
     
    # 打乱布局重新随机编排
    def remix(self):
 
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = self.no_mine
 
        def add_mark(x, y):
            # 如果不是雷的标记就+1
            if self.map[y][x]+1 < self.mine:
                self.map[y][x] += 1
         
        mine_count = 0
 
        while mine_count < self.n_mine:
            x = randint(0, self.width-1)
            y = randint(0, self.height-1)
 
            if self.map[y][x] != self.mine:
                self.map[y][x] = self.mine
                 
                mine_count += 1
 
                # 雷所在的位置的8个方位的数值+1
                ## 上下左右
                if y-1 >= 0: add_mark(x, y-1)
                if y+1 < self.height: add_mark(x, y+1)
                if x-1 >= 0: add_mark(x-1, y)
                if x+1 < self.width: add_mark(x+1, y)
                ## 四个角: 左上角、左下角、右上角、右下角
                if x-1 >= 0 and y-1 >=1: add_mark(x-1, y-1)
                if x-1 >= 0 and y+1 < self.height: add_mark(x-1, y+1)
                if x+1 < self.width and y-1 >= 1: add_mark(x+1, y-1)
                if x+1 < self.width and y+1 < self.height: add_mark(x+1, y+1)
     
    def __getitem__(self, key):
        return self.map[key]
 
    def __str__(self):
        format_str = ""
        for y in range(self.height):
            format_str += str(self[y]) + "\n"
        return format_str
    __repr__ = __str__
 
class LCDCounter(QLCDNumber):
    __counter = 0
    def __init__(self, start=0, parent=None):
        super().__init__(4, parent)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setStyleSheet("background: black; color: red")
        self.counter = start
     
    @property
    def counter(self):
        return self.__counter
    @counter.setter
    def counter(self, value):
        self.__counter = value
        self.display(str(self.__counter))
     
    def inc(self):
        self.counter += 1
    def dec(self):
        self.counter -= 1
 
class MineButton(QPushButton):
    # 按钮类型
    MINE = Mine.mine        # 雷
    NOTMINE = Mine.no_mine  # 不是雷
    m_type = None
 
    # 按钮状态
    mark = False    # 是否是标记状态(默认: 未被标记)
 
    s_flag = '&#9873;'   # 标记
    s_mine = '&#9760;'  # 雷
    s_success = '&#128076;'
 
    # 按钮是否按下(默认False: 未按下)
    __pushed = False
 
    # 按钮对应map的位置
    m_x = 0
    m_y = 0
 
    def __init__(self, map_pos, m_type, parent):
        super().__init__(parent)
        self.m_type = m_type
        self.pushed = False
        self.m_x = map_pos[0]
        self.m_y = map_pos[1]
     
    @property
    def pushed(self):
        return not self.__pushed
    @pushed.setter
    def pushed(self, value):
        self.__pushed = not value
        self.setEnabled(self.__pushed)
 
    ## 按钮上的鼠标按下事件
    def mousePressEvent(self, e):
        #print("m_x:%d"%self.m_x, "m_y:%d"%self.m_y, "m_type:%d"%self.m_type)
 
        p = self.parent()
        # 记录鼠标单击次数
        p.nwap_lcd_clicked.counter += 1
 
        # 左键扫雷
        if e.buttons() == Qt.LeftButton:
            # 踩中雷, 全部雷都翻起来
            if self.m_type == self.MINE:
                for t_line_btn in p.btn_map:
                    for btn in t_line_btn:
                        if btn.m_type == btn.MINE:
                            btn.setText(btn.s_mine)
                        else:
                            if btn.mark != True:
                                if btn.m_type != btn.NOTMINE:
                                    btn.setText(str(btn.m_type))
                        btn.pushed = True
                # 苦逼脸
                p.RestartBtn.setText('&#128547;')
                QMessageBox.critical(self, "失败!", "您不小心踩到了雷! " + self.s_mine)
                return None
            elif self.m_type == self.NOTMINE:
                self.AutoSwap(self.m_x, self.m_y)
            else:
                self.setText(str(self.m_type))
             
            p.mine_counter -= 1
            self.pushed = True
        # 右键添加标记
        elif e.buttons() == Qt.RightButton:
            if self.mark == False:
                self.setText(self.s_flag)
                self.mark = True
            else:
                self.setText("")
                self.mark = False
         
        self.setFocus(False)
     
 
    ## 当按下的位置是NOTMINE时自动扫雷
    def AutoSwap(self, x, y):
        p = self.parent()
        map_btn = p.btn_map
         
        def lookup(t_line, index):
            # 向左扫描
            i = index
            while i >= 0 and not t_line[i].pushed and t_line[i].m_type != MineButton.MINE:
                if t_line[i].m_type != MineButton.NOTMINE:
                    t_line[i].setText(str(t_line[i].m_type))
                t_line[i].pushed = True
                p.mine_counter -= 1
                p.nwap_lcd_counter.counter = p.mine_counter
                i -= 1
                if t_line[i].m_type != MineButton.NOTMINE:
                    break
            # 向右扫描
            i = index + 1
            while i < p.mine_map.width and not t_line[i].pushed and t_line[i].m_type != MineButton.MINE:
                if t_line[i].m_type != MineButton.NOTMINE:
                    t_line[i].setText(str(t_line[i].m_type))
                t_line[i].pushed = True
                p.mine_counter -= 1
                p.nwap_lcd_counter.counter = p.mine_counter
                i += 1
                if t_line[i].m_type != MineButton.NOTMINE:
                    break
         
        # 向上扫描
        j = y
        while j >= 0:
            lookup(map_btn[j], x)
            j -= 1
        # 向下扫描
        j = y + 1
        while j < p.mine_map.height:
            lookup(map_btn[j], x)
            j += 1
         
 
         
 
class MineWindow(QWidget):
 
    def __init__(self):
        super().__init__()
        self.mine_map = Mine(nMines=16)
        self.InitGUI()
        #print(self.mine_map)
         
    def InitGUI(self):
         
        w_width = 304
        w_height = 344
 
        self.resize(w_width, w_height)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("曹乐做")
 
        ## 窗口居中于屏幕
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.x(), qr.y())
 
 
        l_start_x = 2
        l_start_y = 40
        l_x = l_start_x
        l_y = l_start_y
        l_width = 30
        l_height = 30
 
        # 雷区按钮
        self.btn_map = []
        for h in range(self.mine_map.height):
            l_x = l_start_x
            self.btn_map.append(list())
            for w in range(self.mine_map.width):
                self.btn_map[h].append(MineButton([w, h], self.mine_map[h][w], self))
                self.btn_map[h][w].resize(l_width, l_height)
                self.btn_map[h][w].move(l_x, l_y)
                self.btn_map[h][w].show()
                l_x += l_width
            l_y += l_height
 
        r_width = 30
        r_height = 30
 
        # 恢复按钮
        self.RestartBtn = QPushButton('&#128522;', self)
        self.RestartBtn.clicked.connect(self.restart_btn_event)
        self.RestartBtn.resize(r_width, r_height)
        self.RestartBtn.move((w_width-r_width)//2, 6)
 
        ## 计数器
        self.__mine_counter = self.mine_map.width * self.mine_map.height - self.mine_map.n_mine
 
        ## 两个LCD显示控件
        # 操作次数
        self.nwap_lcd_clicked = LCDCounter(0, self)
        self.nwap_lcd_clicked.move(44, 8)
 
        # 无雷块个数
        self.nwap_lcd_counter = LCDCounter(self.mine_counter, self)
        self.nwap_lcd_counter.move(204, 8)
         
    def restart_btn_event(self):
        self.mine_map.remix()
        #QMessageBox.information(self, "look up", str(self.mine_map))
        for y in range(len(self.btn_map)):
            for x in range(len(self.btn_map[y])):
                self.btn_map[y][x].pushed = False
                self.btn_map[y][x].setText("")
                self.btn_map[y][x].m_type = self.mine_map[y][x]
         
        self.mine_counter = self.mine_map.width * self.mine_map.height - self.mine_map.n_mine
        self.RestartBtn.setText('&#128522;')
        self.nwap_lcd_clicked.counter = 0
        self.nwap_lcd_counter.counter = self.mine_counter
     
    ### 计数器
    @property
    def mine_counter(self):
        return self.__mine_counter
    @mine_counter.setter
    def mine_counter(self, value):
        self.__mine_counter = value
        self.nwap_lcd_counter.dec()
        if self.mine_counter == 0:
            for t_line_btn in self.btn_map:
                for btn in t_line_btn:
                    if btn.m_type == btn.MINE:
                        btn.setText(btn.s_success)
                        btn.pushed = True
            QMessageBox.information(self, "恭喜!", "您成功扫雷! " + MineButton.s_success)
 
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MineWindow()
    w.show()
    sys.exit(app.exec_())
