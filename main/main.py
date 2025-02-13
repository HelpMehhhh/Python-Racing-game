import pygame
import os.path


#test
class Mainloop:
    def __init__(self):
        pygame.init()
        self.SCREEN_WIDTH = 1920
        self.SCREEN_HEIGHT = 1080
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        icon = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/game_icon.png')

        pygame.display.set_icon(icon)
        self.running = True
        self.menu_bg = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.main_menu()
        self.game_loop()

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.RESIZABLE, pygame.FULLSCREEN)
                        pygame.display.update()



                elif event.type == pygame.VIDEORESIZE:
                    self.menu_bg = pygame.transform.scale(self.menu_bg, self.screen.get_size())
                    self.screen.blit(self.menu_bg, (0,0))

                    pygame.display.update()
                #elif event.type == pygame.VIDEOEXPOSE:  # handles window minimising/maximising
                 #   self.menu_bg = pygame.transform.scale(self.menu_bg, self.screen.get_size())
                  #  self.screen.blit(self.menu_bg, (0,0))
                   # pygame.display.update()


            pygame.display.update()
            self.clock.tick(60)

    def display(self):
        pass

    def main_menu(self):
        self.screen.blit(self.menu_bg, (0,0))


class Car():
    def __init__(self):
        pass



if __name__ == "__main__":

    Mainloop()