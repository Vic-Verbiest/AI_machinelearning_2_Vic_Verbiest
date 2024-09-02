import matplotlib.pyplot as plt
import numpy as np

def plot():
    # Open het bestand en lees de tweede regel
    with open('fitness.txt', 'r') as file:
        # Lees alle regels van het bestand
        lines = file.readlines()

    min = []
    max = []
    mid = []

    for i in range(len(lines)):
        line = lines[i].replace(' ', '')
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.split(',')
        array = [int(num) for num in line] 
        #print(array)
        min.append(np.min(array))
        max.append(np.max(array))
        mid.append(np.mean(array))
    print(min)
    print(max)
    print(mid)

    x = []
    for i in range(len(min)):
        x.append(i+1)

    print(x)

    plt.plot(x, max, label = "line max")
    plt.plot(x, mid, label = "line gemiddelde")
    plt.plot(x, min, label = "line min")

    plt.xlabel('generation')
    plt.ylabel('fitness')
    plt.title('evolution of fitness')

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    plt.show()