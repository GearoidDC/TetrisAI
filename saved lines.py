if self.lose and self.iterations > 0:
    self.draw_text_middle("You Lost Total Score", 40, (255, 255, 255), self.screen)
    pygame.display.update()
    pygame.time.delay(500)
    self.iterations = self.iterations - 1
    self.main()