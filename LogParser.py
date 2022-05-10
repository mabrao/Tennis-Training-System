import matplotlib.pyplot as plt
import numpy as np
import math
import os


def graph(f, filename,smooth=True):
    #dictionaries for acceleration and gyroscope:
    acc = {'x':[], 'y':[], 'z':[]}
    gyr = {'x':[], 'y':[], 'z':[]}
    search = '.'

    def store_data(axis, l, type):
        dot_id_one = l.find(search)
        type[axis].append(float(l[1:dot_id_one+3])) #found value position
        l = l[dot_id_one+2:] #remove stored part from string
        return l

    def smooth_data(data):
        smoothed = []
        k=3 #size of smoothing
        for i in range(k, len(data)-1):
            smoothed.append(np.mean(data[i-k:i])) 
                        
        return smoothed


    for line in f:
        if line[0] == 'a':
            line = store_data('x', line, acc)
            line = store_data('y', line, acc)
            line = store_data('z', line, acc)

        elif line[0] == 'g':
            line = store_data('x', line, gyr)
            line = store_data('y', line, gyr)
            line = store_data('z', line, gyr)

    #preparing for plotting:
    time_acc = [i for i in range(0, len(acc['x']))]
    time_gyr = [i for i in range(0, len(gyr['x']))]

    time_acc_smoothed = [i for i in range(0, len(smooth_data(acc['x'])))]
    time_gyr_smoothed = [i for i in range(0, len(smooth_data(gyr['x'])))]

    #create a list of resultant vectors for acceleration
    resultant_acceleration = []
    for x,y,z in zip(acc['x'],acc['y'],acc['z']):
        # print(x,y,z) #debug
        resultant_acceleration.append(math.sqrt((x**2) + (y**2) + (z**2)))

    #create a list of resultant vectors for gyroscope
    resultant_gyroscope = []
    for x,y,z in zip(gyr['x'],gyr['y'],gyr['z']):
        # print(x,y,z) #debug
        resultant_gyroscope.append(math.sqrt((x**2) + (y**2) + (z**2)))

    fig, axs = plt.subplots(2)

    if smooth:
        acc_components = axs[0].plot(time_acc_smoothed,smooth_data(acc['x']), time_acc_smoothed,smooth_data(acc['y']), time_acc_smoothed,smooth_data(acc['z']), time_acc_smoothed,smooth_data(resultant_acceleration))
        axs[0].legend(iter(acc_components), ('x', 'y', 'z', 'resultant acceleration'))
        axs[0].set_title(f'{filename[:-4]} Acceleration')
        axs[0].set(xlabel='Number of Readings', ylabel='Acceleration')

        gyr_components = axs[1].plot(time_gyr_smoothed,smooth_data(gyr['x']), time_gyr_smoothed,smooth_data(gyr['y']), time_gyr_smoothed,smooth_data(gyr['z']), time_gyr_smoothed,smooth_data(resultant_gyroscope))
        axs[1].legend(iter(gyr_components), ('x', 'y', 'z', 'resultant gyroscope'))
        axs[1].set_title(f'{filename[:-4]} Angular Velocity')
        axs[1].set(xlabel='Number of Readings', ylabel='Angular Velocity')

        plt.show() #run to show graphs
        #plt.savefig(f'./sensor_graphs/{filename[:-4]}.png') #run to save graphs
    else:
        #without smoothing of the data
        acc_components = axs[0].plot(time_acc,acc['x'], time_acc,acc['y'], time_acc,acc['z'], time_acc,resultant_acceleration)
        axs[0].legend(iter(acc_components), ('x', 'y', 'z', 'resultant acceleration'))
        axs[0].set_title('Acceleration Components vs Number of Readings')
        axs[0].set(xlabel='Number of Readings', ylabel='Acceleration')

        gyr_components = axs[1].plot(time_gyr,gyr['x'], time_gyr,gyr['y'], time_gyr,gyr['z'], time_gyr,resultant_gyroscope)
        axs[1].legend(iter(gyr_components), ('x', 'y', 'z', 'resultant gyroscope'))
        axs[1].set_title('Angular Velocity Components vs Number of Readings')
        axs[1].set(xlabel='Number of Readings', ylabel='Angular Velocity')
        plt.show()
        #plt.savefig(f'./sensor_graphs/{filename[:-4]}.png')
        


if __name__ == '__main__':
    for file in os.listdir('./sensor_data'):
        if 'serve' in file: #use this line to filter what ground stroke to graph
            f = open(f'./sensor_data/{file}', 'r')
            print(file) # use this to know which file are you currently graphing
            graph(f, file)