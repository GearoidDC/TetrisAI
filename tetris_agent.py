# Returns how many lines have been cleared and the new grid
def cleared(grid):
    # If a row is cleared the shift every other row above down one
    lines_cleared = 0
    array = []
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            # add positions to remove from locked
            array.append(i)
            lines_cleared += 1
            for j in range(len(row)):
                grid[i][j] = (0, 0, 0)
    if lines_cleared > 0:
        for x in range(len(array) - 1, -1, -1):
            for i in range(array[x], 0, -1):
                for j in range(len(grid[array[x]])):
                    grid[i][j] = grid[i - 1][j]
                    grid[i - 1][j] = (0, 0, 0)
    return lines_cleared, grid


# Returns the average bumps of the grid and total height
def bumpiness_and_height(grid):
    array_of_bump_heights = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]
    average_bumps = 0
    height = 0
    for j in range(10):
        for i in range(20):
            if grid[i][j] != (0, 0, 0):
                array_of_bump_heights[j] = i
                break
    for i in range(0, 9):
        average_bumps = average_bumps + abs(array_of_bump_heights[i] - array_of_bump_heights[i + 1])
    for i in range(0, 10):
        height = height + abs(array_of_bump_heights[i] - 20)
    return average_bumps, height


# Returns how many holes are in the grid
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

