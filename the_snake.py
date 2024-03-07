from random import randint

import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

clock = pygame.time.Clock()


class GameObject():
    """Базовый класс для объектов."""

    def __init__(self, body_color=(0, 0, 0)):
        """Иннициализация базового класса."""
        self.body_color = body_color
        self.position = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]

    def draw(self):
        """Заглушка метода рисования объекта."""
        # Я постарался это сделать, но оно вроде не работает
        # не понимаю почему
        raise NotImplementedError('Определите draw в подклассе',
                                  (self.__class__.__name__))


class Apple(GameObject):
    """Описание яблока."""

    def __init__(self, body_color=(255, 0, 0)):
        """Иннициализация дочернего класса "Apple" от "GameObject"."""
        super().__init__(body_color)
        self.position = Apple.randomize_position(self)

    def randomize_position(self):
        """
        Рандомизация положения яблока, с учетом,
        что бы оно не попало на позиции змейки.
        """
        position = ((randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                     randint(0, GRID_HEIGHT - 1) * GRID_SIZE))

        while position in Snake.positions:
            position = ((randint(0, GRID_WIDTH) * GRID_SIZE,
                        randint(0, GRID_HEIGHT) * GRID_SIZE))
        return position

    def draw(self, surface):
        """Метод для отрисовки яблока на экране."""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Описание самой змейки."""

    # Начальная позиция змейки
    positions = [((GRID_WIDTH // 2) * GRID_SIZE,
                  (GRID_HEIGHT // 2) * GRID_SIZE)]

    def __init__(self, body_color=(0, 255, 0), direction=RIGHT,
                 positions=[((GRID_WIDTH // 2) * GRID_SIZE,
                             (GRID_HEIGHT // 2) * GRID_SIZE)],
                 length=1, next_direction=None):
        """Иннициализация дочернего класса "Snake" от "GameObject"."""
        self.direction = direction
        self.positions = positions
        self.last = self.positions[0]
        self.length = length
        self.next_direction = next_direction
        super().__init__(body_color)

    def update_direction(self):
        """Метод обновления направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None
        return self.direction

    def move(self, apple):
        """
        Метод, обрабатывающий движение змейки, посредством
        добавления новой координаты в массив и удаления последней.
        """
        # Получение направления движения змейки
        direction = self.update_direction()

        # Получение позиции головы змейки
        head_position = self.get_head_position()

        # Если змейка не съела яблоко добавление и удаление сегмента
        if head_position != apple.position:
            self.positions.append(
                (self.positions[-1][0] + (direction[0] * GRID_SIZE),
                 self.positions[-1][1] + (direction[1] * GRID_SIZE)))

            del self.positions[0]

        # Если змейка съела яблоко добавление сегмента и удлинение змейки
        # для последующего добавления счетчика
        else:
            self.positions.append(
                (self.positions[-1][0] + (direction[0] * GRID_SIZE),
                 self.positions[-1][1] + (direction[1] * GRID_SIZE)))
            apple.position = apple.randomize_position()
            self.length += 1

        # Проверка на переход границы экрана:
        normalized_positions = self.normalize_positions()

        # Присваивание нового значения позиций змейки после проверки
        self.positions = normalized_positions

        return self.length

    def normalize_positions(self):
        """
        Метод проверяющий и осуществляющий переход змейки на
        противоположную часть экрана через границу.
        """
        # Размер экрана + еще одна ячейка - для осуществления перехода змейки
        # через границу на противоположную часть экрана
        max_rigth_grid = SCREEN_WIDTH + GRID_SIZE
        max_bottom_grid = SCREEN_HEIGHT + GRID_SIZE

        normalized_positions = [(position[0] % (max_rigth_grid),
                                 position[1] % (max_bottom_grid))
                                for position in self.positions
                                ]
        return normalized_positions

    def draw(self, surface):
        """Метод для отрисовки яблока на экране."""
        for position in self.positions:
            rect = (
                pygame.Rect((position[0], position[1]), (GRID_SIZE, GRID_SIZE))
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[-1], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Метод для определения координат головы змейки."""
        head_position = self.positions[-1]
        return head_position

    def reset(self, apple):
        """Метод для сброса положения змейки при её столкновении."""
        if self.get_head_position() in self.positions[:-1]:
            # Заполнение экрана черным цветом
            screen.fill(BOARD_BACKGROUND_COLOR)

            # Стартовая позиция
            self.positions = [
                ((GRID_WIDTH // 2) * GRID_SIZE,
                 (GRID_HEIGHT // 2) * GRID_SIZE)]

            # Начальное напраление движения
            self.direction = RIGHT

            # Рандомизация положения яблока
            apple.position = apple.randomize_position()

            self.length = 1


def handle_keys(game_object):
    """Функция, обрабатывающая нажатие клавиш с клавиатуры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def save_result(length):
    """Функция для записи и обновлении рекорда."""
    with open('records.txt', 'r+', encoding='utf-8') as f:
        if length > int(f.readline()):
            f.seek(0)
            f.write(f'{length}\n')

        f.seek(0)
        return f.readline()


def main():
    """Основная функция игры."""
    # Добавления экземпляра в класс Snake
    snake = Snake(SNAKE_COLOR, RIGHT, [((GRID_WIDTH // 2) * GRID_SIZE,
                                        (GRID_HEIGHT // 2) * GRID_SIZE)]
                  )

    # Добавления экземпляра в класс Apple
    apple = Apple(APPLE_COLOR)

    while True:
        # Скорость обновления экрана (х в секунду раз)
        clock.tick(SPEED)

        # Отображение в панели инфы названия игры(змейка),
        # скорости, текущей длины, рекорд
        pygame.display.set_caption(f'Змейка!     Скорость игры: {SPEED}      '
                                   f'Текущая длина змейки: |{snake.length}|'
                                   f'     Рекорд: {save_result(snake.length)}')

        # Получение информации для движения с клавиатуры
        handle_keys(snake)

        # Крайний сегмент змейки
        # (мне проще было сделать его с начала,а не с конца)
        snake.last = snake.positions[0]

        # Активация функции движения змейки
        snake.move(apple)

        # Проверка не стукнулась ли змейка о себя саму
        snake.reset(apple)

        # Отрисовка яблока на экране
        apple.draw(screen)

        # Отрисовка змейки на экране
        snake.draw(screen)

        # Обновление экрана
        pygame.display.update()


if __name__ == '__main__':
    main()
