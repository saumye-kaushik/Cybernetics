import pandas as pd
import os

import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import en_core_web_sm

import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

from bs4 import BeautifulSoup

import dateutil.parser as dparser


def read_document(file_name, type):
    file = open(file_name, "r", encoding='utf-8', errors='ignore').read()
    # print(file)
    if type == 'SA':
        file = file.lower()
        file_clean = file.replace('\n', ' ').replace('\r', ' ')
    if type == 'ER':
        file_clean = file.replace('\r', ' ')
    return file_clean


def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text


def extract_text_from_html(html_path):
    html_doc = open(html_path)
    soup = BeautifulSoup(html_doc, 'html.parser')
    text_full = soup.get_text().strip().replace('\n', ' ').replace('\t', ' ')
    text_clean = ' '.join(text_full.split())
    text_final = re.sub('<!--(.*?)-->', '', text_clean)
    return text_final


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


def get_filename(name, accessmasterfilepath=''):
    masterfilepath_txt = accessmasterfilepath + str(name)
    # masterfilepath_pdf = masterfilepath_txt.replace('text', 'pdfs').replace('txt', 'pdf').replace('TXT', 'PDF')
    return masterfilepath_txt


def check_string_valid(entity_name):
    val_check = re.match(r".*[!@#$%^&*()_+={}:;<.>?≤,\-]{2,}", entity_name)
    return not(bool(val_check))


def check_date_valid(entity_date):
    try:
        date_ent = dparser.parse(entity_date)
        return True

    except:
        return False


def extract_entities_split(text):

    sentence_list = tokenize.sent_tokenize(text)
    entity_dict = {}
    person_list = "||"
    norp_list = "||"
    fac_list = "||"
    org_list = "||"
    gpe_list = "||"
    loc_list = "||"
    date_list = "||"
    event_list = "||"
    product_list = "||"

    package = en_core_web_sm
    ignored_entities = ['CARDINAL', 'ORDINAL']
    nlp = package.load()
    nlp.max_length = 4000000

    for sentence in sentence_list:
        # print(sentence)
        sentence = sentence.strip()
        if sentence != '' and sentence != ' ':
            # print(sentence)

            doc = nlp(sentence)
            for ent in doc.ents:

                entity_str = ent.text.strip()
                entity_str = " ".join(entity_str.split())
                if entity_str.split():
                    entity_len = len(max(entity_str.split(), key=len))

                if ent.label_ not in ignored_entities and entity_str != '' and \
                        (entity_len > 2 and not bool(re.match(r'[^A-Za-z0-9]+$', entity_str))):

                    if ent.label_ == 'PERSON' and entity_str not in person_list.split('||') and \
                            check_string_valid(entity_str):
                        person_list += entity_str+'||'
                    if ent.label_ == 'NORP' and entity_str not in norp_list.split('||') and \
                            check_string_valid(entity_str):
                        norp_list += entity_str+'||'
                    if ent.label_ == 'FAC' and entity_str not in fac_list.split('||') and \
                            check_string_valid(entity_str):
                        fac_list += entity_str+'||'
                    if ent.label_ == 'ORG' and entity_str not in org_list.split('||') and \
                            check_string_valid(entity_str):
                        org_list += entity_str+'||'
                    if ent.label_ == 'GPE' and entity_str not in gpe_list.split('||') and \
                            check_string_valid(entity_str):
                        gpe_list += entity_str+'||'
                    if ent.label_ == 'LOC' and entity_str not in loc_list.split('||') and \
                            check_string_valid(entity_str):
                        loc_list += entity_str+'||'
                    if ent.label_ == 'DATE' and entity_str not in date_list.split('||') and \
                            check_date_valid(entity_str):
                        date_list += entity_str+'||'
                    if ent.label_ == 'EVENT' and entity_str not in event_list.split('||') and \
                            check_string_valid(entity_str):
                        event_list += entity_str+'||'
                    if ent.label_ == 'PRODUCT' and entity_str not in product_list.split('||') and \
                            check_string_valid(entity_str):
                        product_list += entity_str+'||'

            entity_dict['Date (Machine Generated)'] = date_list[2:-2]
            entity_dict['Event (Machine Generated)'] = event_list[2:-2]
            entity_dict['Facility (Machine Generated)'] = fac_list[2:-2]
            entity_dict['Geo-Political Entity (Machine Generated)'] = gpe_list[2:-2]
            entity_dict['Location (Machine Generated)'] = loc_list[2:-2]
            entity_dict['Nationalities, Religious, or Political Groups (Machine Generated)'] = norp_list[2:-2]
            entity_dict['Date (Machine Generated)'] = date_list[2:-2]
            entity_dict['Organization (Machine Generated)'] = org_list[2:-2]
            entity_dict['Person (Machine Generated)'] = person_list[2:-2]
            entity_dict['Product (Machine Generated)'] = product_list[2:-2]

    return entity_dict


def read_files(directory, accessmasterfile_path, metadata_dataframe=None, has_metadata_file=False, choice='3'):
    path = directory
    column_names_sa = ['Overall Sentiment (Machine Generated)', 'Percent Positive Sentiment (Machine Generated)',
                    'Percent Negative Sentiment (Machine Generated)', 'Percent Neutral Sentiment (Machine Generated)']
    column_names_er = ['Date (Machine Generated)', 'Event (Machine Generated)',
                    'Facility (Machine Generated)', 'Geo-Political Entity (Machine Generated)',
                    'Location (Machine Generated)', 'Nationalities, Religious, or Political Groups (Machine Generated)',
                    'Organization (Machine Generated)', 'Person (Machine Generated)', 'Product (Machine Generated)']

    try:

        for item in os.listdir(path):
            filepath = path + '/' + item
            if item.lower().endswith(".txt"):
                print('Started file: ' + str(filepath))
                if choice != '2':
                    file_text = read_document(filepath, 'SA')
                    score = split_text_in_sentences(file_text)
                    filename = get_filename(item, accessmasterfile_path)
                    if has_metadata_file:
                        for column in column_names_sa:
                            metadata_dataframe.loc[metadata_dataframe.accessMasterPathname == filename, column]\
                                = score.get(column, '')

                if choice != '1':
                    file_text = read_document(filepath, 'ER')
                    score = extract_entities_split(file_text)
                    filename = get_filename(item, accessmasterfile_path)
                    if has_metadata_file:
                        for column in column_names_er:
                            metadata_dataframe.loc[metadata_dataframe.accessMasterPathname == filename, column]\
                                = score.get(column, '')
                print('Completed file ' + str(filename))

            elif item.lower().endswith(".pdf"):
                print('Started file: ' + str(filepath))
                file_text = extract_text_from_pdf(filepath, accessmasterfile_path)
                if choice != '2':
                    score = split_text_in_sentences(file_text)
                    filename = get_filename(item, accessmasterfile_path)
                    if has_metadata_file:
                        for column in column_names_sa:
                            metadata_dataframe.loc[metadata_dataframe.accessMasterPathname == filename, column]\
                                = score.get(column, '')

                if choice != '1':
                    score = extract_entities_split(file_text)
                    filename = get_filename(filepath, accessmasterfile_path)
                    if has_metadata_file:
                        for column in column_names_er:
                            metadata_dataframe.loc[metadata_dataframe.accessMasterPathname == filename, column]\
                                = score.get(column, '')

                print('Completed file ' + str(filename))

            elif item.lower().endswith(".html") or item.lower().endswith(".htm"):
                print('Started file: ' + str(filepath))
                file_text = extract_text_from_html(filepath)
                if choice != '2':
                    score = split_text_in_sentences(file_text)
                    filename = get_filename(filepath, accessmasterfile_path)
                    if has_metadata_file:
                        for column in column_names_sa:
                            metadata_dataframe.loc[metadata_dataframe.accessMasterPathname == filename, column]\
                                = score.get(column, '')

                if choice != '1':
                    score = split_text_in_sentences(file_text)
                    filename = get_filename(filepath, accessmasterfile_path)
                    if has_metadata_file:
                        for column in column_names_er:
                            metadata_dataframe.loc[metadata_dataframe.accessMasterPathname == filename, column] \
                                = score.get(column, '')
                print('Completed file ' + str(filename))

            elif os.path.isdir(filepath):
                read_files(filepath, metadata_dataframe, True)
    except KeyError:
        print(filepath)

    return metadata_dataframe


def main():

    metadatafilepath_ip = input('Enter the full path of the metadata file:\n')
    allfilespath_ip = input('Enter the directory where all files are located:\n')
    accessmasterfilepath_ip = input('Enter the master access file path:\n')
    finalmetadatapath_ip = input('Enter the path with the name of the updated metadata file:\n')
    choice_ip = input('Enter 1 for sentiment analysis, 2 for entity extraction, 3 for both:\n')

    metadata_df = pd.read_csv(metadatafilepath_ip, delimiter='\t')

    final_df = read_files(allfilespath_ip, accessmasterfilepath_ip, metadata_df, True, choice_ip)

    final_df.to_csv(finalmetadatapath_ip, sep='\t', index=False)


if __name__ == '__main__':
    main()
