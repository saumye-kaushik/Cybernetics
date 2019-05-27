from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import pandas as pd
import numpy as np
import os
import re
from textblob import TextBlob

desired_width = 700
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 10)


def read_document(file_name):
    file = open(file_name, "r", encoding='utf-8', errors='ignore').read()
    # print(file)
    file = file.lower()
    file_clean = file.replace('\n', ' ').replace('\r', ' ')
    return file_clean


def text_clean_up(text, keyword):
    if re.compile(r'\b({0})\b'.format(keyword), flags=re.IGNORECASE).search(text) is None:
        cleaned_up_text = text
    else:
        split_text = text.split(" ")
        # print(split_text)
        keyword_index = split_text.index(keyword)
        # print(keyword_index)
        text_after_keyword = split_text[keyword_index:]
        cleaned_up_text = list_to_string(text_after_keyword)
    return cleaned_up_text


def list_to_string(string_list):
    return " ".join(string_list)


def get_polarity_scores_tb(text):
    score_tb = TextBlob(text).sentiment
    return score_tb.polarity


def split_text_in_sentences(text):
    sia = SentimentIntensityAnalyzer()
    sentence_list = tokenize.sent_tokenize(text)
    sentiments = {'Overall Sentiment (Machine Generated)': 0.0, 'Percent Positive Sentiment (Machine Generated)': 0.0,
                  'Percent Negative Sentiment (Machine Generated)': 0.0,
                  'Percent Neutral Sentiment (Machine Generated)': 0.0}

    for sentence in sentence_list:
        vs = sia.polarity_scores(sentence)
        sentiments['Overall Sentiment (Machine Generated)'] += vs['compound']
        sentiments['Percent Negative Sentiment (Machine Generated)'] += vs['neg']
        sentiments['Percent Neutral Sentiment (Machine Generated)'] += vs['neu']
        sentiments['Percent Positive Sentiment (Machine Generated)'] += vs['pos']

    if len(sentence_list) > 0:
        sentiments['Overall Sentiment (Machine Generated)'] = \
            sentiments['Overall Sentiment (Machine Generated)'] / len(sentence_list)
        sentiments['Percent Positive Sentiment (Machine Generated)'] = \
            sentiments['Percent Positive Sentiment (Machine Generated)'] / len(sentence_list) * 100
        sentiments['Percent Negative Sentiment (Machine Generated)'] = \
            sentiments['Percent Negative Sentiment (Machine Generated)'] / len(sentence_list)*100
        sentiments['Percent Neutral Sentiment (Machine Generated)'] = \
            sentiments['Percent Neutral Sentiment (Machine Generated)'] / len(sentence_list)*100

    return sentiments


def get_polarity_scores(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)


def create_dataframe_of_data(name, ls_score):
    ls_df = []
    ls_df.insert(0, name)
    for key, value in ls_score.items():
        ls_df.append(value)
    return ls_df


def get_filename(name):
    return name.replace('_extracted', '').replace('.txt', '') + '.pdf'


def read_text_files(directory, metadata_dataframe):
    path = directory
    '''
    column_names = ['accessMasterFilename', 'Overall Sentiment (Machine Generated)',
                    'Percent Positive Sentiment (Machine Generated)', 'Percent Negative Sentiment (Machine Generated)',
                    'Percent Neutral Sentiment (Machine Generated)']
    '''
    column_names = ['Overall Sentiment (Machine Generated)', 'Percent Positive Sentiment (Machine Generated)',
                    'Percent Negative Sentiment (Machine Generated)', 'Percent Neutral Sentiment (Machine Generated)']
    # df = pd.DataFrame(columns=column_names)
    data_list = []
    checklist = ['1106026_1_Alexander_1967_1970_extracted', '1106026_17_Junk_extracted', 'Wiener_b4_fl59_1941_extracted'
                 'McCulloch_7_Fahnestock_1949-1950', '1106026_3_Blum_1964_73']

    for item in os.listdir(path):
        if item.endswith(".txt"):
            filepath = path + '/' + item
            file_text = read_document(filepath)
            score = split_text_in_sentences(file_text)
            filename = get_filename(item)
            if item in checklist:
                print('-'*40)
                print(item)
                print(score)
                print('-' * 40)
            # data_list.append(create_dataframe_of_data(filename, score))
            for column in column_names:
                metadata_dataframe.loc[metadata_dataframe.accessMasterFilename == filename, column] = \
                    score.get(column, '')
            print('Completed file ' + str(filename))

        else:
            sub_path = directory + '/' + item
            file_text = ''
            for file in os.listdir(sub_path):
                if file.endswith(".txt"):
                    filepath = sub_path + '/' + file
                    # print(item)
                    file_text = file_text + '\n' + read_document(filepath)
            score = split_text_in_sentences(file_text)
            filename = get_filename(item)
            if item in checklist:
                print('-'*40)
                print(item)
                print(score)
                print('-' * 40)
            # data_list.append(create_dataframe_of_data(filename, score))
            for column in column_names:
                metadata_dataframe.loc[metadata_dataframe.accessMasterFilename == filename, column] = \
                    score.get(column, '')
            print('Completed file ' + str(filename))

    # df = pd.DataFrame(data_list, columns=column_names)
    return metadata_dataframe


metadata_df = pd.read_csv('MetadataFile/Cybernetics_20190503.tsv', delimiter='\t')
# print(metadata_df)
# metadata_df['accessMasterFilename'] = metadata_df['accessMasterFilename'].astype(str)
# print(metadata_df.dtypes)
final_df = read_text_files("TXTFiles_new", metadata_df)
print(final_df[['accessMasterFilename', 'Overall Sentiment (Machine Generated)',
                'Percent Positive Sentiment (Machine Generated)', 'Percent Negative Sentiment (Machine Generated)',
                'Percent Neutral Sentiment (Machine Generated)']])
# df2 = read_text_files("aggregate_new")

# print(df2)
# sentiment_df = pd.concat([df1, df2], ignore_index=True)
# sentiment_df = df1
# sentiment_df['accessMasterFilename'] = sentiment_df['accessMasterFilename'].astype(str)
# print(sentiment_df.dtypes)
final_df.to_csv('results/Cybernetics_20190503_SA.tsv', sep='\t', index=False)

'''
final_df = metadata_df.merge(sentiment_df, on='accessMasterFilename', how='left')
# print(sentiment_df)

if not os.path.exists('results'):
    os.makedirs('results')

final_df.to_csv('results/Cybernetics_20190503_SA.tsv', sep='\t', index=False)
accessMasterFilename
# print(read_text_files("TXTFiles_new"))
# data = read_document("aggregate_new/McCulloch_2_Avakian_1956-1968/McCulloch_2_Avakian_1956-1968-page-001.txt")
# print(data)
# data_clean = text_clean_up(data, "dear")
# scores = get_polarity_scores(data_clean)
'''
