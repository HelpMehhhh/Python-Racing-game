import pygame
import os.path



class Mainloop:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280,720))
        self.clock = pygame.time.Clock()
        icon = pygame.image.load(os.path.dirname(''))

        pygame.display.set_icon(icon)
        self.running = True
        self.main_menu()
        self.game_loop()

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            pygame.display.flip()
            self.clock.tick(60)

    def display(self):
        pass

    def main_menu(self):
        pass

class Car():
    def __init__(self):
        pass



if __name__ == "__main__":

    Mainloop()