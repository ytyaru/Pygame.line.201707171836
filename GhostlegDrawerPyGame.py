import sys, copy, pygame
import Ghostleg
import LinesAnimation
import Screen
import CalcSize
class Main:
    @staticmethod
    def Run(method, title=None):
        pygame.init()
        if title: pygame.display.set_caption(title)
        clock = pygame.time.Clock()
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit();
            method()
            pygame.display.flip()
            clock.tick(60) # 60 FPS

# あみだくじを描画する
class GhostlegDrawerPyGame:
    def __init__(self, ghostleg):
        self.__leg = None
        self.__ghostleg = ghostleg
        self.__screen = Screen.Screen()
        self.__width = 8
        self.__color = (255,255,255)
        self.__to_goal_pointlist = None # ゴールまでの頂点リスト（self.__legから生成する）
        self.__select_line_color = (255,0,0)
        self.__select_line_width = 2
        self.__linesanim = None
        self.__CalcSize = CalcSize.CalcSize(self.__ghostleg, self.__screen)
#        print(pygame.font.get_fonts()) # 使えるフォント名

    def Select(self, select_line_index):
        if len(self.__ghostleg.Ghostleg) < select_line_index: raise Exception('select_line_indexは {} 以下にして下さい。'.format(len(self.__ghostleg.Ghostleg)))
        self.__create_to_goal_pointlist(select_line_index)
        self.__linesanim = LinesAnimation.LinesAnimation(self.__to_goal_pointlist, self.__select_line_color, self.__select_line_width)
    
    # あみだくじを描画する
    def Draw(self):
        self.__screen.Fill()
        self.__draw_vartical_lines()
        self.__draw_horizon_lines()
        self.__draw_goals()
        self.__draw_select_lines()

    def __draw_vartical_lines(self):
        for xi in range(len(self.__ghostleg.Ghostleg)+1):
            start = self.__get_pos(xi, 0)
            end = self.__get_last_pos(xi)
            pygame.draw.line(self.__screen.Screen, self.__color, start, end, self.__width)

    def __draw_goals(self):
        font = pygame.font.Font("/usr/share/fonts/truetype/migmix/migmix-1m-regular.ttf", 12)
#        print('font.size():', font.size())
        for i in range(len(g.Goals)):
            self.__screen.Screen.blit(font.render(g.Goals[i], False, self.__color), self.__get_last_pos(i))

    def __draw_horizon_lines(self):
        for yi in range(len(self.__ghostleg.Ghostleg[0])):
            for xi in range(len(self.__ghostleg.Ghostleg)):
                if 1 == self.__ghostleg.Ghostleg[xi][yi]:
                    start = self.__get_pos(xi, yi+1)
                    end = self.__get_pos(xi+1, yi+1)
                    pygame.draw.line(self.__screen.Screen, self.__color, start, end, self.__width)

    # 選択肢からゴールまでの頂点リストを生成する
    def __create_to_goal_pointlist(self, select_line_index):
        self.__to_goal_pointlist = None
        self.__to_goal_pointlist = []
        now_line_index = select_line_index
        x = self.__get_leg_index_first_horizon_line(now_line_index, 0)
        self.__to_goal_pointlist.append([self.__CalcSize.StartPoint[0] + now_line_index * self.__CalcSize.WidthInterval, self.__CalcSize.StartPoint[1]])
        for y in range(len(self.__ghostleg.Ghostleg[0])):
            if 0 == now_line_index:
                if 1 == self.__ghostleg.Ghostleg[now_line_index][y]: # └
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index+1, y+1)
                    now_line_index += 1
                else: # │
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index, y+2)
            elif len(self.__ghostleg.Ghostleg) == now_line_index:
                if 1 == self.__ghostleg.Ghostleg[now_line_index-1][y]: # ┘
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index-1, y+1)
                    now_line_index += -1
                else: # ｜
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index, y+2)
            else:
                if 1 == self.__ghostleg.Ghostleg[now_line_index][y]: # └
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index+1, y+1)
                    now_line_index += 1
                elif 1 == self.__ghostleg.Ghostleg[now_line_index-1][y]: # ┘                
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index-1, y+1)
                    now_line_index += -1
                else: # ｜
                    self.__set_pointlist_value(now_line_index, y+1)
                    self.__append_point(now_line_index, y+2)
        self.__to_goal_pointlist.append([self.__to_goal_pointlist[-1][0], self.__screen.Size[1] - (self.__CalcSize.FontPixcelSize * self.__CalcSize.GoalStrMaxLen)])
        print(self.__to_goal_pointlist)
        return self.__to_goal_pointlist

    # 1つ前のと同じ座標ならセットしない
    def __set_pointlist_value(self, now_line_index, y):
        if (self.__to_goal_pointlist[-1][0] != self.__CalcSize.StartPoint[0] + now_line_index * self.__CalcSize.WidthInterval
            or self.__to_goal_pointlist[-1][1] != self.__CalcSize.StartPoint[1] + (y * self.__CalcSize.HeightInterval)):
            self.__append_point(now_line_index, y)

    def __append_point(self, now_line_index, y):
        self.__to_goal_pointlist.append(self.__get_pos(now_line_index, y))

    def __get_pos(self, xi, yi): return [self.__CalcSize.StartPoint[0] + xi * self.__CalcSize.WidthInterval, self.__CalcSize.StartPoint[1] + yi * self.__CalcSize.HeightInterval]
    
    def __get_last_pos(self, xi): return [self.__CalcSize.StartPoint[0] + xi * self.__CalcSize.WidthInterval, self.__screen.Size[1] - self.__CalcSize.FontPixcelSize * self.__CalcSize.GoalStrMaxLen]

    def __get_leg_index_first_horizon_line(self, now_line_index, horizon_start_index):
        if 0 == now_line_index: return now_line_index
        elif len(self.__ghostleg.Ghostleg) == now_line_index: return now_line_index-1
        else:
            for h in range(horizon_start_index, len(self.__ghostleg.Ghostleg[0])):
                if 1 == self.__ghostleg.Ghostleg[now_line_index][h]:return now_line_index
                elif 1 == self.__ghostleg.Ghostleg[now_line_index-1][h]: return now_line_index-1
            return now_line_index # 左右のlegとも横線が1本もない場合
    def __draw_select_lines(self):
        if self.__to_goal_pointlist:
            if self.__linesanim: self.__linesanim.draw(self.__screen.Screen)


g = Ghostleg.Ghostleg()
g.Create()
drawer = GhostlegDrawerPyGame(g)
for i in range(len(g.Goals)): print(i, g.GetGoal(i))
drawer.Select(0)
main = Main()
main.Run(drawer.Draw, title="あみだくじ描画")
