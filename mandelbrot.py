import numpy as np
import matplotlib.pyplot as plt

from matplotlib import animation, rc

rc('animation', html='html5')  

fig = plt.figure(figsize=(10, 10))
max_frames = 200
max_zoom = 300
images = []

pmin, pmax, qmin, qmax = -2.5, 1.5, -2, 2 # инициализиация
# пусть c = p + iq и p меняется в диапазоне от pmin до pmax,
# а q меняется в диапазоне от qmin до qmax

ppoints, qpoints = 200, 200 # число точек по горизонтали и вертикали
max_iterations = 300 # максимальное количество итераций
infinity_border = 4
image = np.zeros((ppoints, qpoints))

def mandelbrot():
    for ip, p in enumerate(np.linspace(pmin, pmax, ppoints)):
        for iq, q in enumerate(np.linspace(qmin, qmax, qpoints)):
            c = p + 1j * q
        
            z = 0
            for k in range(max_iterations):
                z = z**2 + c
            
                if abs(z) > infinity_border:                
                    image[ip,iq] = k
                # находимся вне M: отметить точку как белую
                    break
                
if __name__ == "__main__":
    mandelbrot()
    plt.xticks([]) # выкл метки на осях
    plt.yticks([])
    plt.imshow(-image.T, cmap='flag')
    plt.show()
