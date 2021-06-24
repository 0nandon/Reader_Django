import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Dense, Concatenate, Activation, Flatten, Dropout
from tensorflow.keras.regularizers import l2
from tensorflow.keras.optimizers import SGD

from sklearn.utils import shuffle
import pandas as pd
import numpy as np
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from book.models import Book


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
P_embedding = Embedding(M, K, embeddings_regularizer=l2(), name='user_vec')(user)
Q_embedding = Embedding(N, K, embeddings_regularizer=l2(), name='book_vec')(item)
user_bias = Embedding(M, 1, embeddings_regularizer=l2())(user)
item_bias = Embedding(N, 1, embeddings_regularizer=l2())(item)

P_embedding = Flatten()(P_embedding)
Q_embedding = Flatten()(Q_embedding)
user_bias = Flatten()(user_bias)
item_bias = Flatten()(item_bias)

R = Concatenate()([P_embedding, Q_embedding, user_bias, item_bias])
R = Dense(2048)(R)
R = Activation('relu')(R)
R = Dropout(0.3)(R)
R = Dense(256)(R)
R = Activation('relu')(R)
R = Dense(1)(R)

model = Model(inputs=[user, item], outputs=R)
model.load_weights('/workspace/Reader/recommendation/model_weights/model_weight.h5')

#  ================ end model ================  #


def train_model():
    u_cols = ['user_id', 'book', 'rating']
    ratings = pd.read_csv('/workspace/Reader/recommendation/data/user_rating.csv', sep=',', names=u_cols, encoding='latin-1')

    TRAIN_SIZE = 0.75
    ratings = shuffle(ratings, random_state=1)
    cut_off = int(len(ratings) * TRAIN_SIZE)
    ratings_train = ratings[:cut_off]
    ratings_test = ratings[cut_off:]

    model.compile(
        loss=RMSE,
        optimizer=SGD(),
        metrics=[RMSE]
    )

    results = model.fit(
        x=[ratings_train['user_id'].values, ratings_train['book'].values],
        y=ratings_train['rating'].values - mu,
        epochs=65,
        batch_size=512,
        validation_data=(
            [ratings_test['user_id'].values, ratings_test['book'].values],
            ratings_test['rating'].values - mu
        )
    )

    return results


class Recommend:
    def __init__(self, book, score):
        self.book = book
        self.score = score


def recommend(user_id):
    cache_key = 'books_'
    books = cache.get(cache_key, None)
    if books is None:
        books = pd.read_csv('/workspace/Reader/recommendation/data/book_1000.csv', sep=',', index_col='id', encoding='latin-1')
        cache.set(cache_key, books, 60 * 60)

    cache_key = 'recommends' + str(user_id)
    recommends = cache.get(cache_key, None)
    if recommends is None:
        book_ids = np.array(books.index)
        user_ids = np.array([user_id] * 1000)

        # 사용자에 대한 도서 예상 평점 계산
        predictions = model.predict([user_ids, book_ids]) + mu
        predictions = predictions.reshape(-1)
        sort_idx = np.argsort(predictions)[::-1]
        recommend_books = book_ids[sort_idx][:70]
        score = predictions[sort_idx][:70]

        # 예상 도서 평점 중 가장 높은 도서 70권 중 랜덤으로 10권을 뽑아 추출
        idx = np.random.permutation(range(70))
        recommend_books = recommend_books[idx][:10]
        score = score[idx][:10]

        recommends = [
            Recommend(get_object_or_404(Book, key=iid), round(score_,2))
            for iid, score_ in zip(recommend_books, score)
        ]
        cache.set(cache_key, recommends, 60 * 60)

    return recommends




