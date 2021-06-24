import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten
from tensorflow.keras.regularizers import l2

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache


K = 200
mu = 3.8453003369350527
M = 999
N = 24093


# loss function
def RMSE(y_true, y_pred):
    return tf.sqrt(tf.reduce_mean(tf.square(y_true - y_pred)))


#  ================ deep learning model ================  #

user = Input(shape=(1,))
item = Input(shape=(1,))
P_embedding = Embedding(M, K, embeddings_regularizer=l2())(user)
Q_embedding = Embedding(N, K, embeddings_regularizer=l2(), name='book_vec')(item)

R = layers.dot([P_embedding, Q_embedding], axes=2)
R = Flatten()(R)

model = Model(inputs=[user, item], outputs=R)
model.load_weights('/workspace/Reader/recommendation/model_weights/model_weight_embedding.h5')

#  ================ end model ================  #


# 연관 도서 추출 함수
def related_books(book_id):
    related_cache_key = 'related_' + str(book_id)
    related_books = cache.get(related_cache_key)

    if related_books is None:
        cache_key = 'books_'
        books = cache.get(cache_key, None)
        if books is None:
            books = pd.read_csv('/workspace/Reader/recommendation/data/book_1000.csv', sep=',', index_col='id', encoding='latin-1')
            cache.set(cache_key, books, 60 * 60)

        books = books.index
        book_vec = model.get_layer('book_vec').weights

        cosine_dic = {}
        v1 = np.array(book_vec[0][book_id]).reshape(1, -1)

        # 코사인 유사도를 기반으로 가장 유사도가 높은 도서 추출
        for book in books:
            if book == book_id:
                continue
            v2 = np.array(book_vec[0][book]).reshape(1, -1)
            cosine_dic[book] = float(cosine_similarity(v1, v2))
        cosine_dic = sorted(cosine_dic.items(), reverse=True, key=lambda x: x[1])
        related_books = cosine_dic[:4]
        cache.set(related_cache_key, related_books, 60 * 60)
    return related_books




