import pygame
import os.path



class Mainloop:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        icon = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/game_icon.png')

        pygame.display.set_icon(icon)
        self.running = True
        self.in_menu = True
        self.main_menu()
        self.game_loop()

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            if self.in_menu:
                self.main_menu()

            pygame.display.update()
            self.clock.tick(60)

    def display(self):
        pass

    def main_menu(self):
        self.menu_bg = pygame.image.load(os.path.dirname(os.path.abspath(__file__))+'/../static/crappy_bg.png')
        self.screen.blit(self.menu_bg, (0,0))


class Car():
    def __init__(self):
        pass



if __name__ == "__main__":

    Mainloop()