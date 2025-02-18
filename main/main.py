import pygame
import os.path
pygame.init()

class Mainloop:
    def __init__(self):
        self.SCREEN_WIDTH = pygame.display.Info().current_w
        self.SCREEN_HEIGHT = pygame.display.Info().current_h
        self.clock = pygame.time.Clock()

        icon = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/game_icon.png')
        pygame.display.set_icon(icon)

        self.running = True
        self.menu_bg = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.fullscreen = True
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.game_states = [self.main_menu]
        self.state = self.game_states[0]
        self.game_loop()



    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.state(3)

                elif event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.VIDEOEXPOSE:
                    self.state(2)

            pygame.display.update()
            self.clock.tick(60)



    def main_menu(self, change = 1):
        #change, 1 = normal display, 2 = resize, 3 = fullscreen/not full

        if change == 1:
            self.screen.blit(self.menu_bg, (0,0))

        if change == 2:
            self.menu_bg = pygame.transform.scale(self.menu_bg, self.screen.get_size())
            self.screen.blit(self.menu_bg, (0,0))
            pygame.display.update()

        if change == 3:
            if self.fullscreen:
                self.screen = pygame.display.set_mode((self.SCREEN_WIDTH / 2, self.SCREEN_HEIGHT / 2), pygame.RESIZABLE)
                self.fullscreen = False
            else:
                self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                self.fullscreen = True




class Car():
    def __init__(self):
        pass



if __name__ == "__main__":
    Mainloop()