import matplotlib.pyplot as plt
import numpy as np

plt.style.use('_mpl-gallery')

# make data
x = np.arange(25)
RasRuneeee = np.array([0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1])
jsonreboot = np.array([0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0])
deleteeeee = np.array([0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0])
# y_mob_post = np.array([0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,,0,0,0,0,0,0])
startrmsss = np.array([0,1,0,1,0,1,0,1,0,1,0,0,0,0,0,0,0,0,1,0,1,0,1,0,1])

# plot
plt.subplot(4,1,1)
plt.step(x, RasRuneeee, linewidth=6)
plt.ylabel('Rasberry pi')
# fig1, a1 = plt.subplots()
# a1.set(xlim=(0, 25), xticks=np.arange(1, 25), ylim=(0, 1), yticks=np.arange(1, 1))

plt.subplot(4,1,2)
plt.step(x, jsonreboot, linewidth=6)
# fig1, a2 = plt.subplots()
# a2.set(xlim=(0, 25), xticks=np.arange(1, 25), ylim=(0, 1), yticks=np.arange(1, 1))
plt.subplot(4,1,3)
plt.step(x, deleteeeee, linewidth=6)
plt.subplot(4,1,4)
plt.step(x, startrmsss, linewidth=6)
# plt.subplot(5,1,5)
# plt.step(x, startrmsss, linewidth=6)

plt.show()