if self.lose and self.iterations > 0:
    self.draw_text_middle("You Lost Total Score", 40, (255, 255, 255), self.screen)
    pygame.display.update()
    pygame.time.delay(500)
    self.iterations = self.iterations - 1
    self.main()

    x, y = pygame.mouse.get_pos()
    print(x, y)


    def start_up(self):
        go = True
        self.iterations = 100
        while go:
            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.start_button.isover(pos):
                        print("Start")
                        go = False
                if event.type == pygame.MOUSEMOTION:
                    if self.start_button.isover(pos):
                        self.start_button.color = (61, 97, 128)
                    else:
                        self.start_button.color = (147, 150, 153)
            self.screen.fill((0, 0, 0))
            self.start_button.draw(self.screen)
            pygame.display.update()
        self.main(True)