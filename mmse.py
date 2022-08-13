
import calendar
from datetime import datetime
from datetime import timedelta
from PIL import Image
from nltk.corpus import wordnet as wn
import io
import base64
import numpy as np
import cv2 as cv
import tensorflow as tf
from tensorflow import keras
from keras import Model
import logging
import sys
import os
import json


def parse_question(key, dict):
    q = dict[key]
    q_ans = q[0]
    q_time = q[1]
    if key == "Q14":
        q_ans = q[0]
        classi = q[1]
        q_time = q[2]
        return q_ans, classi, q_time
    return q_ans, q_time


def parse_Udate_strs(q_time):
    # splitting date into date and time
    date_list = q_time.split()
    date_ymd = date_list[0]
    universal_time_hms = date_list[1]
    # splitting lists
    date_ymd = date_ymd.split("-")
    universal_time_hms = universal_time_hms.split(":")
    # getting params
    year, month, day = date_ymd
    hours, minutes, seconds = universal_time_hms
    return year, month, day, hours, minutes, seconds[0:2]


def parse_Udate_str_ymd(q_time):
    # splitting date into date and time
    date_list = q_time.split()
    date_ymd = date_list[0]
    return date_ymd


def parse_Udate_datetime(q_time):
    year, month, day, hours, minutes, seconds = parse_Udate_strs(q_time)
    tmp = year + "-" + month + "-" + day + "-" + \
        hours + "-" + minutes + "-" + seconds
    # getting date for any further manipulation
    date = datetime.strptime(tmp, '%Y-%m-%d-%H-%M-%S')
    return date


def parse_Udate_date(q_time):
    year, month, day, _, _, _ = parse_Udate_strs(q_time)
    tmp = year + "-" + month + "-" + day
    # getting date for any further manipulation
    date = datetime.strptime(tmp, '%Y-%m-%d').date()
    return date


def get_weekday(q_time):
    weekday = calendar.day_name[parse_Udate_date(q_time).weekday()]
    return weekday


def calc_score_season(ans, month):
    myseason = json.load(open('seasons.json'))
    for currseason in myseason[month]:
        if ans == currseason:
            del myseason
            return 1
    del myseason
    return 0


def calc_score_bool(con):
    if con is True or con == "true":
        return 1
    else:
        return 0


def calc_score_bool_list(ans_list):
    ans_list = cut_paren(ans_list)
    anss = ans_list.split(",")
    score = 0
    for ans in anss:
        score += calc_score_bool(ans)
    return score


def cut_paren(ans):
    return ans[1:-1]


def validate_ans_idk(ans):
    if ans == "I don't know":
        return True


def round_score(score_in, misses):
    return round(score_in*30/(30-misses))


def stringToRGB(ans):
    ans = cut_paren(ans)
    anst = ans.split(",")
    base64_string = anst[1]
    imgdata = base64.b64decode(str(base64_string))
    img = Image.open(io.BytesIO(imgdata))
    opencv_img = cv.cvtColor(np.array(img), cv.COLOR_BGR2RGB)
    return opencv_img


def create_model():
    num_classes = 7
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Resizing(64, 64))
    model.add(tf.keras.layers.RandomFlip("horizontal_and_vertical")),
    model.add(tf.keras.layers.RandomRotation(0.2)),
    model.add(tf.keras.layers.Rescaling(1./255))
    model.add(tf.keras.layers.Conv2D(64, 3, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D())
    model.add(tf.keras.layers.Conv2D(64, 3, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D())
    model.add(tf.keras.layers.Conv2D(64, 3, activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D())
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(units=128, activation='relu'))
    model.add(tf.keras.layers.Dropout(0.2))
    model.add(tf.keras.layers.Dense(num_classes))
    model.compile(optimizer='adam',
                  loss=tf.losses.SparseCategoricalCrossentropy(
                      from_logits=True),
                  metrics=[tf.metrics.SparseCategoricalAccuracy()])

    return model


def calc_q01(ans, q_time_str):
    actual_date = parse_Udate_date(q_time_str)
    ans = cut_paren(ans)
    if validate_ans_idk(ans):
        return 0
    ans_date = datetime.strptime(ans, '%m/%d/%Y').date()
    scorei = 0
    days_diff = abs(actual_date - ans_date)
    if days_diff.days < 2:
        scorei += 1
    if actual_date.month == ans_date.month:
        scorei += 1
    if actual_date.year == ans_date.year:
        scorei += 1
    return scorei


def calc_q02(ans, q_time_str):
    ans = cut_paren(ans)
    if validate_ans_idk(ans):
        return 0
    _, month, _, _, _, _ = parse_Udate_strs(q_time_str)
    return calc_score_season(ans, month)


def calc_q03(ans, q_time_str):
    ans = cut_paren(ans)
    if validate_ans_idk(ans):
        return 0
    return calc_score_bool(ans == get_weekday(q_time_str))


def calc_q045(ans, user_profile_dict):
    ans = cut_paren(ans)
    if validate_ans_idk(ans):
        return 0
    ans = ans.split(",")
    score = 0
    if user_profile_dict["countryId"] == ans[0]:
        score += 1
    if user_profile_dict["state"] == ans[1]:
        score += 1
    return score


def calc_q06070809101112(ans_list):
    ans_list = cut_paren(ans_list)
    anss = ans_list.split(",")
    score = 0
    for ans in anss:
        score += calc_score_bool(ans)
    return score


def calc_q13(ans):
    ans = cut_paren(ans)
    words = ans.split()
    verbs = 0
    nouns = 0
    pos_all = dict()
    for w in words:
        pos_l = set()
        for tmp in wn.synsets(w):
            if tmp.name().split('.')[0] == w:
                pos_l.add(tmp.pos())
        pos_all[w] = pos_l
    for i in range(len(words)):
        for lingo in pos_all[words[i]]:
            if lingo == 'n':
                nouns += 1
                if verbs > 0 and nouns > 0:
                    return 1
            if lingo == 'v':
                verbs += 1
                if verbs > 0 and nouns > 0:
                    return 1
    return 0

def calc_q14(ans, img_class):
    # get preds
    model = create_model()
    img = stringToRGB(ans)
    model.load_weights('./checkpoints/my_checkpoint.index')
    img = tf.expand_dims(img, 0)  # Create batch axis
    tf_scores = model.predict(img)

    tf_class_scores = dict()
    tf_class_scores_top = list()
    tf_score_list_top = list()

    classes = ["angleCross", "ellipse", "hexagon",
               "line", "square", "straightCross", "triangle"]
    for i in range(len(classes)):
        s = tf_scores[0][i]/tf_scores[0].max()*100
        tf_class_scores[classes[i]] = s
        tf_score_list_top.append(s)
    tf_score_list_top.sort(reverse=True)
    tf_score_list_top = tf_score_list_top[0:3]
    for iclass in tf_class_scores:
        if tf_class_scores[iclass] in tf_score_list_top:
            tf_class_scores_top.append(iclass)
    if img_class in tf_class_scores_top:
        return 1
    return 0


def calc_fun(uuidjson):
    uuidjsons = json.load(uuidjson)
    mmse_data = uuidjsons[""]
    user_profile = uuidjsons[""]

    q01_ans, start_time = parse_question("Q1", mmse_data)
    q02_ans, _ = parse_question("Q2", mmse_data)
    q03_ans, _ = parse_question("Q3", mmse_data)
    q045_ans, _ = parse_question("Q4", mmse_data)
    q06_ans, _ = parse_question("Q6", mmse_data)
    q07_ans, _ = parse_question("Q7", mmse_data)
    q08_ans, _ = parse_question("Q8", mmse_data)
    q09_ans, _ = parse_question("Q9", mmse_data)
    q10_ans, _ = parse_question("Q10", mmse_data)
    q11_ans, _ = parse_question("Q11", mmse_data)
    q12_ans, _ = parse_question("Q12", mmse_data)
    q13_ans, _ = parse_question("Q13", mmse_data)
    q14_ans, classi, end_time = parse_question("Q14", mmse_data)

    score = 0
    score += calc_q01(ans=q01_ans, q_time_str=start_time)
    score += calc_q02(ans=q02_ans, q_time_str=start_time)
    score += calc_q03(ans=q03_ans, q_time_str=start_time)
    score += calc_q045(ans=q045_ans, user_profile_dict=user_profile)
    score += calc_q06070809101112(ans_list=q06_ans)
    score += calc_q06070809101112(ans_list=q07_ans)
    score += calc_q06070809101112(ans_list=q08_ans)
    score += calc_q06070809101112(ans_list=q09_ans)
    score += calc_q06070809101112(ans_list=q10_ans)
    score += calc_q06070809101112(ans_list=q11_ans)
    score += calc_q06070809101112(ans_list=q12_ans)
    score += calc_q13(ans=q13_ans)
    score += calc_q14(ans=q14_ans, img_class=classi)
    score = round_score(score_in=score, misses=3)
    print(score)
