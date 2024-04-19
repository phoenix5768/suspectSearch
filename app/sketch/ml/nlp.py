import os
import fasttext

from app import settings
from scipy.spatial.distance import cosine


model = fasttext.load_model(f'{os.path.join(settings.BASE_DIR)}/cc.en.300.bin')


def compr(wrd):
    alp_ar = ['small', 'thin', 'short', 'little', 'medium', 'thick', 'big', 'long', 'extensive', 'massive']
    rating = [0.1,      0.2,    0.3,     0.4,      0.5,      0.6,     0.7,   0.8,    0.9,         1.0]
    #w1 = model.get_sentence_vector('giant') #massive
    #w1 = model.get_sentence_vector('narrow') #thin
    #w1 = model.get_sentence_vector('moderate') #medium
    #w1 = model.get_sentence_vector('tiny') #small
    #w1 = model.get_sentence_vector('miniscule') #small
    #w1 = model.get_sentence_vector('stubby') #short
    #w1 = model.get_sentence_vector('bulky') #thick
    #w1 = model.get_sentence_vector('chunky') #thick
    #w1 = model.get_sentence_vector('meaty') #thick
    #w1 = model.get_sentence_vector('prolonged') #long
    #w1 = model.get_sentence_vector('lengthy') #long
    w1 = model.get_sentence_vector(wrd)
    max = 0
    index = 0

    for i in range(len(alp_ar)):
        w2 = model.get_sentence_vector(alp_ar[i])
        res = 1-cosine(w1, w2)
        if res > max:
            max = res
            index = rating[i]

    return index


def nlp(prompt: str):
    nose_l = 0.5
    mouth = 0.5
    nose_size = 0.5
    right_brow = 0.5
    left_brow = 0.5
    eyes = 0.5

    pr_l = prompt.split()

    for i in range(len(pr_l)):
        if pr_l[i] == 'nose':
            if pr_l[i + 1] == 'length':
                nose_l = compr(pr_l[i - 1])
                print(pr_l[i - 1])
            else:
                nose_size = compr(pr_l[i - 1])
                print(pr_l[i - 1])
        if pr_l[i] == 'lips':
            mouth = compr(pr_l[i - 1])
            print(pr_l[i - 1])
        if pr_l[i] == 'brows':
            right_brow = compr(pr_l[i - 1])
            left_brow = compr(pr_l[i - 1])
        if pr_l[i] == 'brow':
            if pr_l[i - 1] == 'right':
                right_brow = compr(pr_l[i - 2])
                print(pr_l[i - 2])
            if pr_l[i - 1] == 'left':
                left_brow = compr(pr_l[i - 2])
                print(pr_l[i - 2])
        if pr_l[i] == 'eyes':
            eyes = compr(pr_l[i - 1])
            print(pr_l[i - 1])

    feats = [nose_l, right_brow, left_brow, eyes, eyes, nose_size, mouth]

    response = {
        'nose_height': feats[0],
        'right_brow': feats[1],
        'left_brow': feats[2],
        'left_eye': feats[3],
        'right_eye': feats[4],
        'nose_size': feats[5],
        'mouth': feats[6],
        'gender': 'both'
    }

    return response
    # print(feats)
