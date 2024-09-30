from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data= pd.read_csv("/Users/seonggyu.park/Documents/studies/bedload_dataset.csv")
print(data)

# dataset essencial info
print(data.info(),"\n")
    
# remove rows that contains at least one NaN value
print(data.dropna(inplace=True))

# verify that all NaN values were removed
for column in data.columns.to_list():
    print(column,":",data[column].isnull().any())
    
# verify final shape of the dataset  
print(data.shape)



# visualize scatter of the features 
host = host_subplot(111, axes_class=AA.Axes)
plt.subplots_adjust(right=0.75)

# plot visualization parameters
labels = data.columns[0:5].tolist()
colors = ["crimson", "purple", "limegreen", "gold", "blue"]
width=0.5

# iterate on features of the dataset (i.e. column names)
for i, l in enumerate(labels):
    if i ==0:
        ax = host
        ax.set_ylabel(labels[i])
    else:        
        ax = host.twinx()
        new_fixed_axis = ax.get_grid_helper().new_fixed_axis
        ax.axis["right"] = new_fixed_axis(loc="right",
                                            axes=ax,
                                            offset=(60*(i-1), 0))
        ax.axis["right"].toggle(all=True)
        ax.set_ylabel(labels[i])

    x = np.ones(data.shape[0])*i + (np.random.rand(data.shape[0])*width-width/2.)
    ax.scatter(x, data[data.columns[i]],color=colors[i])
    mean = data[f"{data.columns[i]}"].mean()
    std = np.std(data[data.columns[i]])
    ax.plot([i-width/2., i+width/2.], [mean, mean], color="k")
    ax.plot([i,i], [mean-2*std, mean+2*std], color="k")

ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)

plt.draw()
plt.show()