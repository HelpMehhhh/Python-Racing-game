import pygame
pygame.init()

ScreenSizeMinx = pygame.display.Info().current_w / 2
ScreenSizeMiny = pygame.display.Info().current_h / 2

Ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
FullScreen = True

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if FullScreen:
                    Ekran = pygame.display.set_mode((ScreenSizeMinx, ScreenSizeMiny))
                    FullScreen = False
                else:
                    Ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    FullScreen = True
        if event.type == pygame.QUIT:
            run = False

    Ekran.fill('red')                           # <---
    pygame.display.update()

pygame.quit()
quit()