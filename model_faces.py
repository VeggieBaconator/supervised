#!/usr/bin/env python3
"""
Using PCA and an MLP to model the faces dataset.
Quick exploration of using T-SNE to visualize.

"""
import numpy as np
import seaborn as sns
from matplotlib import pyplot
from sklearn.manifold import TSNE
import os


from mlp import MLP
from pca import PCA

np.set_printoptions(suppress=True)

##################################################

directory = os.path.join(os.path.dirname(__file__), 'datasets', 'faces')

def load_image_vector(subject, instance):
    return pyplot.imread(directory+"/images/subject{0}_img{1}.pgm".format(subject, instance)).flatten() / 255.0

def show_image_vector(vector, ax=None):
    if ax is None:
        ax = pyplot
    ax.imshow(vector.reshape(50, 50), interpolation="bicubic", cmap="Greys")

##################################################

samples_train = []
samples_test = []

labels_train = []
labels_test = []

with open(directory+"/genders.csv", 'r') as genders:
    for i, l in enumerate(genders):
        gender = l.strip().split(',')[1]

        samples_train.append(load_image_vector(i+1, 1))
        labels_train.append(gender)

        samples_test.append(load_image_vector(i+1, 2))
        labels_test.append(gender)

        samples_test.append(load_image_vector(i+1, 3))
        labels_test.append(gender)

samples_train = np.array(samples_train)
samples_test = np.array(samples_test)

##################################################

classes = np.unique(labels_train)

embedding = {}
for i, c in enumerate(classes):
    onehot = np.zeros(len(classes), dtype=float)
    onehot[i] = 1.0
    embedding[c] = onehot

targets_train = np.array([embedding[label] for label in labels_train])
targets_test = np.array([embedding[label] for label in labels_test])

##################################################

dimensions = [20, 100, 50, 2]

name = "faces_results/faces_model"
for d in dimensions[:-1]:
    name += '_' + str(d)
print(name)

##################################################

pca = PCA()
new_pca = False

if new_pca:
    eigs = pca.analyze(samples_train)
    pca.save("faces_results/faces")
else:
    pca.load("faces_results/faces")

samples_train_compressed = pca.compress(samples_train, dimensionality=dimensions[0])
samples_test_compressed = pca.compress(samples_test, dimensionality=dimensions[0])

##################################################

mlp = MLP(dimensions)
new_mlp = False

if new_mlp:
    mlp.train(samples_train_compressed,
              targets_train,
              max_epochs=200,
              step=0.1,
              gain=0.9)
    mlp.save(name)
else:
    mlp.load(name)

##################################################

cm_train = mlp.evaluate(samples_train_compressed,
                        labels_train,
                        classes)

print("==================================================")
print("Training Confusion Matrix")
print(cm_train)
print("Accuracy: {0}".format(np.sum(np.diag(cm_train))))
print("==================================================")

cm_valid = mlp.evaluate(samples_test_compressed,
                        labels_test,
                        classes)

print("==================================================")
print("Validation Confusion Matrix")
print(cm_valid)
print("Accuracy: {0}".format(np.sum(np.diag(cm_valid))))
print("==================================================")

##################################################

print("Plotting PCA projection of data-set and classifier.")

fig = pyplot.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_title('MLP-Classification of the Faces Data-Set', fontsize=16)

ax.set_xlim([-10.0, 10.0])
ax.set_xlabel("PCA Component 0", fontsize=12)
ax.set_ylim([-10.0, 10.0])
ax.set_ylabel("PCA Component 1", fontsize=12)

XX, YY = np.meshgrid(np.arange(*ax.get_xlim(), 0.05),
                     np.arange(*ax.get_ylim(), 0.05))
XY = np.vstack((XX.ravel(), YY.ravel())).T
XY = np.column_stack((XY, np.zeros((len(XY), dimensions[0]-2), dtype=float)))
ZZ = np.argmax(mlp.predict(XY), axis=1).reshape(XX.shape)
ax.contourf(XX, YY, ZZ+1e-6, alpha=0.2)

labels_train = np.array(labels_train)
ax.scatter(samples_train_compressed[labels_train=="male", 0], samples_train_compressed[labels_train=="male", 1], c='b', edgecolors='k', label="male")
ax.scatter(samples_train_compressed[labels_train=="female", 0], samples_train_compressed[labels_train=="female", 1], c='r', edgecolors='k', label="female")
ax.legend()

print("Close plots to finish...")
pyplot.show()

perplexities = [10, 15, 30]
for perplexity in perplexities:
    features_tsne = TSNE(n_components=2, perplexity=perplexity, n_iter=100000).fit_transform(samples_train_compressed)
    fig = pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)
    sns.scatterplot(features_tsne[:,0], features_tsne[:,1], hue=labels_train, legend='full')
    ax.set_title("T-SNE on Iris Data-Set with Perplexity {0}".format(perplexity), fontsize=16)

pyplot.show()
