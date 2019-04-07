
def fc0(temp):
    if temp < 50:
        return 25
    if temp > 90:
        return 85
    return int(((temp ** 2) / 90) + 4)

def fc1(temp):
    if temp < 40:
        return 0

    if temp > 80:
        return 75
    if temp > 90:
        return 85
    return int(((temp ** 2) / 100) + 4)

fan_controls = {
    "[fan:0]": ("[gpu:0]", fc0),
    "[fan:1]": ("[gpu:1]", fc1)
}

interval = 5
