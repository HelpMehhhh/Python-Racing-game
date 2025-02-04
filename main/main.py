import pygame



class Mainloop:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280,720))
        self.clock = pygame.time.Clock()

    def game_loop(self):
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