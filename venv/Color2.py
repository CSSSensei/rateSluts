def color_calculate(avg):
    whole = avg // 2
    fract = (avg % 2) / 2
    if whole <= 2:
        fract2 = (avg % 4) / 4
        red = 1.0
        green = fract2
        blue = 0.0
    if whole == 2:
        red = 1.0 - fract
        green = 1.0
        blue = 0.0
    if whole == 3:
        red = 0.0
        green = 1.0 - fract
        blue = fract
    if whole == 4:
        red = fract
        green = 0.0
        blue = 1.0
    if whole >= 5:
        red = 1.0
        green = 0.0
        blue = 1.0 - fract
    return (red, green, blue)
