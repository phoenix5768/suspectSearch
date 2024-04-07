import os
from PIL import Image
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import numpy
from loguru import logger
from sketch import models


# Current idea of a search algorithm
# 1. Normalise data (So each metric will have the same weight)
# Example:
#          normalized_nose_length = (nose_length - min_nose_length) / (max_nose_length - min_nose_length)
# 2. Concatenate metrics into a single feature vector (np.array() or pd.Series())
# 3. Compare feature vectors and choose the closest objects (like within 10%)
# Comparing by calculating distances. Possible techniques: Euclidean distance or cosine similarity. Or maybe even KNN
# linera or logistic regression

# First attempt with Euclidean distance apporach
def euclidean_distance(vec1, vec2):
    """Calculate the Euclidean distance between two vectors."""
    return np.sqrt(np.sum((vec1 - vec2) ** 2))


def closest_match(new_vector, feature_vectors):
    """Find the index of the closest match to the new vector."""
    distances = [euclidean_distance(new_vector, vec) for vec in feature_vectors]
    closest_index = np.argmin(distances)
    return closest_index


# Second Attempt with Cosine Similarity
def find_closest_match(new_feature_vector, X_train):
    # Calculate cosine similarity between new feature vector and all feature vectors in X_train
    similarities = cosine_similarity(new_feature_vector, X_train)

    # Find the index of the feature vector in X_train with highest similarity
    closest_indexes = np.argsort(-similarities)[0][:20]
    return closest_indexes


# Third attempt with Linear Regression
def linear_regression(new_obj, initial_objs, threshold=0.1, num_results=1):
    similarities = []

    for obj in initial_objs:
        similarity_score = sum((new_obj[key] - obj[key]) ** 2 for key in new_obj)
        similarities.append(similarity_score)

    most_similar_indices = numpy.argsort(similarities)[:num_results]
    similar_objs = []

    for idx in most_similar_indices:
        if similarities[idx] <= threshold:
            similar_objs.append((idx, initial_objs[idx]))

    if similar_objs:
        logger.info(similar_objs)
        return similar_objs
    else:
        return "No similarities found within the threshold."


# Last and the best attempt with K-nearest neighbours
def knn(new_obj, initial_objs, threshold=0.1, num_results=1):
    X = numpy.array([list(obj.values()) for obj in initial_objs])
    k = NearestNeighbors(n_neighbors=len(initial_objs))
    k.fit(X)
    new_features = numpy.array([list(new_obj.values())])
    distances, indices = k.kneighbors(new_features)
    similar_objs = []

    for dist, idx in zip(distances[0], indices[0]):
        if dist <= threshold:
            similar_objs.append((idx, initial_objs[idx]))

    similar_objs.sort(key=lambda x: x[0])
    return similar_objs[:num_results]


def search_criminal(data: dict) -> list:
    result = []
    initial_objs = []
    iins = []

    criminals = models.CriminalsImage.objects.all()
    for criminal in criminals:
        initial_objs.append(json.loads(criminal.normalized_feature))
        iins.append(criminal.iin)

    potential_suspects = knn(data, initial_objs, threshold=0.4, num_results=3)

    for suspect in potential_suspects:
        result.append(iins[suspect[0]])

    return result
