import en_core_web_sm
import pandas as pd
import os
from nltk import tokenize
import re

desired_width = 700
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 10)


def read_document(file_name):
    file = open(file_name, "r", encoding='utf-8', errors= 'ignore').read()
    # print(file)
    file_clean = file.replace('\r', ' ')
    return file_clean


def get_filename(name):
    return name.replace('_extracted', '').replace('.txt', '') + '.pdf'


def extract_entities(text, package):
    nlp = package.load()
    text = text.replace('\n', ' ')
    # print('-' * 40)
    doc = nlp(text)
    for ent in doc.ents:
        print(ent.text, ent.label_)


def extract_entities_split(text, package):
    # sentence_list = text.split('\n')

    sentence_list = tokenize.sent_tokenize(text)
    entity_dict = {}
    entity_list = []
    person_list = "||"
    norp_list = "||"
    fac_list = "||"
    org_list = "||"
    gpe_list = "||"
    loc_list = "||"
    date_list = "||"
    event_list = "||"
    product_list = "||"

    ignored_entities = ['CARDINAL', 'ORDINAL']
    nlp = package.load()
    nlp.max_length = 4000000
    # print('-'*40)
    # print('split')
    for sentence in sentence_list:
        # print(sentence)
        sentence = sentence.strip()
        # sentence = re.sub(r"[^A-Za-z0-9., -]+", '', sentence)
        if sentence != '' and sentence != ' ':
            # print(sentence)

            doc = nlp(sentence)
            for ent in doc.ents:

                entity_str = ent.text.strip()
                entity_str = " ".join(entity_str.split())
                if entity_str.split():
                    entity_len = len(max(entity_str.split(), key=len))
                # entity_str = entity_str.replace('\n', ' ').replace('\t', ' ')
                # entity_str = re.sub(' +', ' ', entity_str)
                if ent.label_ not in ignored_entities and entity_str != '' and entity_len>2:
                    # print(sentence)
                    # entity_dict[ent.text] = ent.label_
                    # entity_list.append(entity_str)
                    if ent.label_ == 'PERSON' and entity_str not in person_list.split('||'):
                        person_list += entity_str+'||'
                    if ent.label_ == 'NORP' and entity_str not in norp_list.split('||'):
                        norp_list += entity_str+'||'
                    if ent.label_ == 'FAC' and entity_str not in fac_list.split('||'):
                        fac_list += entity_str+'||'
                    if ent.label_ == 'ORG' and entity_str not in org_list.split('||'):
                        org_list += entity_str+'||'
                    if ent.label_ == 'GPE' and entity_str not in gpe_list.split('||'):
                        gpe_list += entity_str+'||'
                    if ent.label_ == 'LOC' and entity_str not in loc_list.split('||'):
                        loc_list += entity_str+'||'
                    if ent.label_ == 'DATE' and entity_str not in date_list.split('||'):
                        date_list += entity_str+'||'
                    if ent.label_ == 'EVENT' and entity_str not in event_list.split('||'):
                        event_list += entity_str+'||'
                    if ent.label_ == 'PRODUCT' and entity_str not in product_list.split('||'):
                        product_list += entity_str+'||'
                # print(ent.text, ent.label_)
                # print(entity_list)

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


def create_dataframe_of_data(name, ls_dict):
    ls_df = []
    ls_df.insert(0, name)
    for key, value in ls_dict.items():
        ls_df.append(value)
    return ls_df


def read_text_files(directory, metadata_dataframe):
    path = directory
    # column_names = ['accessMasterFilename', 'PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'DATE', 'EVENT']
    column_names = ['Date (Machine Generated)', 'Event (Machine Generated)',
                    'Facility (Machine Generated)', 'Geo-Political Entity (Machine Generated)',
                    'Location (Machine Generated)', 'Nationalities, Religious, or Political Groups (Machine Generated)',
                    'Organization (Machine Generated)', 'Person (Machine Generated)', 'Product (Machine Generated)']
    # df = pd.DataFrame(columns=column_names)
    checklist = ['1106026_1_Alexander_1967_1970_extracted', '1106026_17_Junk_extracted', 'Wiener_b4_fl59_1941_extracted'
                 , 'McCulloch_7_Fahnestock_1949-1950', '1106026_3_Blum_1964_73']
    data_list = []

    for item in os.listdir(path):
        if item.endswith(".txt"):
            filepath = path + '/' + item
            file_text = read_document(filepath)
            score = extract_entities_split(file_text, en_core_web_sm)
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
            print('Completed file '+str(filename))

        else:
            sub_path = directory + '/' + item
            file_text = ''
            for file in os.listdir(sub_path):
                if file.endswith(".txt"):
                    filepath = sub_path + '/' + file
                    # print(item)
                    file_text = file_text + '\n' + read_document(filepath)
            score = extract_entities_split(file_text, en_core_web_sm)
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
            print('Completed file '+str(filename))

    # df = pd.DataFrame(data_list, columns=column_names)
    return metadata_dataframe


metadata_df = pd.read_csv('results/Cybernetics_20190503_SA.tsv', delimiter='\t')

final_df = read_text_files('TXTFiles_new', metadata_df)
# df1.to_csv('results/entity_test.tsv', sep='\t', index=False)
print(final_df)
'''
df2 = read_text_files('aggregate_new')
print(df2)

entity_df = pd.concat([df1, df2], ignore_index=True)
if not os.path.exists('results'):
    os.makedirs('results')

final_df = metadata_df.merge(entity_df, on='accessMasterFilename', how='left')
df1.to_csv('results/entity_text_new.tsv', sep='\t', index=False)
'''
final_df.to_csv('results/Cybernetics_20190503_SA_NER.tsv', sep='\t', index=False)


# displacy.serve(doc, style="ent")
'''
nlp1 = en_core_web_sm.load()
nlp2 = en_core_web_md.load()
nlp3 = en_core_web_lg.load()

doc1 = nlp1(text_data)
doc2 = nlp2(text_data)
doc3 = nlp3(text_data)

print('en_core_web_sm')
print('-'*40)
for ent in doc1.ents:
    print(ent.text, ent.label_)

print('-'*40)
print('en_core_web_md')
print('-'*40)
for ent in doc2.ents:
    print(ent.text, ent.label_)

print('-'*40)
print('en_core_web_lg')
print('-'*40)
for ent in doc3.ents:
    print(ent.text, ent.label_)

print('-'*40)

'''

