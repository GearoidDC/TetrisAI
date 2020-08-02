def cleared(grid):
    # need to see if row is clear the shift every other row above down one
    inc = 0

    array = []
    for i in range(len(grid) - 1, -1, -1):

        row = grid[i]
        if (0, 0, 0) not in row:
            # add positions to remove from locked
            array.append(i)
            inc += 1
            for j in range(len(row)):
                grid[i][j] = (0, 0, 0)
    if inc > 0:
        for x in range(len(array) - 1, -1, -1):

            for i in range(array[x], 0, -1):
                for j in range(len(grid[array[x]])):
                    grid[i][j] = grid[i - 1][j]
                    grid[i - 1][j] = (0, 0, 0)

    return inc, grid


def bumpiness_and_height(grid):
    array_of_bump_heights = [19, 19, 19, 19, 19, 19, 19, 19, 19, 19]
    average_bumps = 0
    for j in range(10):
        for i in range(20):
            if grid[i][j] != (0, 0, 0):
                array_of_bump_heights[j] = i
                break
    for i in range(0, 9):
        average_bumps = average_bumps + abs(array_of_bump_heights[i] - array_of_bump_heights[i + 1])

    height = sum(array_of_bump_heights)
    return average_bumps, height


def holes(grid):
    number_of_holes = 0
    for j in range(len(grid[0])):
        for i in range(len(grid)):
            if grid[i][j] != (0, 0, 0):
                for k in range(i+1, 20):
                    if grid[k][j] == (0, 0, 0):
                        number_of_holes = number_of_holes + 1
                break
    return number_of_holes

