import os
import json
import urllib
from urllib.request import urlopen, Request
from urllib.parse import quote  
from textblob import TextBlob
import sys
import random
import time

dir_path = os.path.dirname(os.path.realpath(__file__))

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'
          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104'
          'Safari/537.36 Core/1.53.3357.400 QQBrowser/9.6.11858.400'}

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)

with open(dir_path + '\\banned.txt', 'r') as lang, open(dir_path + '\\amount.txt', 'r') as am:
    banned_languaches = lang.read()
    amount = am.read().splitlines()
    amount = list(map(int, amount))

def load_data(url):
    req = urllib.request.Request(url, data=None, headers=header,
                              origin_req_host=None, unverifiable=False,
                              method=None)
    read = urllib.request.urlopen(req).read()
    data = json.loads(read)
    return data

def filter_lang(tags, banned_languaches):
    filtered = []
    for tag in tags:
        blob = TextBlob(tag)
        if blob.detect_language() not in banned_languaches:
            filtered.append(word)
    return filtered

def search_tags(text, tags, banned_languaches, non_bmp_map):
    local_tags = []
    for word in text:
        if word.startswith('#') and word.count('#') == 1 and len(word) > 2:
            word = word.translate(non_bmp_map)
            if word not in tags:
                local_tags.append(word)
    try:
        blob = TextBlob('test')
        blob.detect_language()
        local_tags = filter_lang(local_tags, banned_languaches)
    except:
        pass
    return local_tags

def from_top(tag, tags, amount, banned_languaches, non_bmp_map, header):
    url = 'https://www.instagram.com/explore/tags/' + quote(tag) + '/?__a=1'
    data = load_data(url)
    posts_count = int(data['graphql']['hashtag']['edge_hashtag_to_media']['count'])
    if posts_count > 0 and (posts_count < amount[0] or posts_count > amount[3]):
        print('The amount of posts is ', posts_count, '. Should I continue?\nPress y for "Yes" or n for "No"')
        answer = input()
        while answer is not 'y' and answer is not 'n':
            print('Enter "y" or "n"')
            answer = input()
        if answer is 'n':
            return 1
    elif posts_count == 0:
        return 0
    moretags = []
    codes = []
    for i in range(0,len(data['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges'])):
        try:
            text = data['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges'][i]['node']['edge_media_to_caption']['edges'][0]['node']['text'].split()
        except:
            code = data['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges'][i]['node']['shortcode']
            print(code)
            codes.append(code)
            continue
        
        local_tags = search_tags(text, tags, banned_languaches, non_bmp_map)
        print('len ', len(local_tags))    
        if len(local_tags) < 30:
            code = data['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges'][i]['node']['shortcode']
            print(code)
            codes.append(code)

        for tag in local_tags:
            if tag not in moretags:
                moretags.append(tag)
    return(moretags,codes)

def from_first_comment(code, header, tags, banned_languaches, non_bmp_map):
    url = 'https://www.instagram.com/p/' + code + '/?__a=1'
    data = load_data(url)
    coments_count = data['graphql']['shortcode_media']['edge_media_to_comment']['count']
    if coments_count > 0:
        first_comment = data['graphql']['shortcode_media']['edge_media_to_comment']['edges'][0]['node']['text']
        local_tags = search_tags(first_comment, tags, banned_languaches, non_bmp_map)
    else:
        local_tags = []
    return local_tags

def is_personal(): #check if the tag used as personal tag
    pass

def is_banned(): #if tag contains banned components
    pass

def masssearch(): #search for all themes in file
    pass

def sort_by_frequency(tags, amount):
    low, middle, high = [], [], []
    i = len(tags) - 1
    while i > 0:
        pause = random.randrange(1,4,1)
        time.sleep(pause*0.1)
        url = 'https://www.instagram.com/explore/tags/' + quote(tags[i][1:]) + '/?__a=1'
        try:
            data = load_data(url)
        except:
            i -= 1
            continue
        posts_count = int(data['graphql']['hashtag']['edge_hashtag_to_media']['count'])
        if posts_count < amount[0] or posts_count > amount[3]:
            del tags[i]
        elif posts_count > amount[0] and posts_count < amount[1]:
            low.append(tags[i])
        elif posts_count > amount[1] and posts_count < amount[2]:
            middle.append(tags[i])
        elif posts_count > amount[2] and posts_count < amount[3]:
            high.append(tags[i])
        i -= 1
        print('.', end = ' ')
    return low, middle, high


while True:
    print('Enter the word "new" followed by some tag (two words separated by whitespace, without "#" sign)'
          ' to search by new user-defined tag..\n\n'
          '\n\nEnter "q" to quit.')
    tags_and_codes = []
    command = input().split()
    if len(command) == 2:
        if command[0] == 'new' and '#' not in command[1]:
            try:
                with open(dir_path + '\\' + command[1] + '.txt', 'r') as t:
                    tags = t.read()
            except:
                tags = []
            tags_and_codes = from_top(command[1], tags, amount, banned_languaches, non_bmp_map, header)
            print('THE RESULT: ', tags_and_codes)
            if tags_and_codes == 0:
                print('There are no posts with such tag. Use anoher one.')
                continue
            elif tags_and_codes == 1:
                continue
            else:
                if len(tags_and_codes[1])>0:
                    for code in tags_and_codes[1]:
                        more_tags = from_first_comment(code, header, tags_and_codes[1], banned_languaches, non_bmp_map)
                        tags_and_codes[0].extend(more_tags)

            print ('\nIs sorting by frequency needed? Enter "y" for Yes or any other letter for No.')
            ifsort = input()
            if ifsort == 'y':
                k = 9
                num = len(tags_and_codes[0])//k
                print('TOTAL ', len(tags_and_codes[0]))
                low, middle, high = [],[],[]
                for i in range (0,k-1):
                    tags = tags_and_codes[0][num*i:num*(i+1)]
                    L,M,H = sort_by_frequency(tags, amount)
                    low.extend(L)
                    middle.extend(M)
                    high.extend(H)
                    print(i+1, '/', k , 'sorted')
                    time.sleep(60)
                tags = tags_and_codes[0][num*(k-1):len(tags_and_codes[0])]
                L,M,H = sort_by_frequency(tags, amount)
                low.extend(L)
                middle.extend(M)
                high.extend(H)

                filename = command[1] + '_sbf.txt'
                f = open(filename, 'a+', encoding='utf8')
                f.write('Low frequency tags:\n\n')
                for tag in low:
                    f.write('%s\n' % tag)
                f.write('\nMiddle frequency tags:\n\n')
                for tag in middle:
                    f.write('%s\n' % tag)
                f.write('\nHigh frequency tags:\n\n')
                for tag in high:
                    f.write('%s\n' % tag)            
                f.close()

            filename = command[1] + '.txt'
            f = open(filename, 'a+', encoding='utf8')
            for tag in tags_and_codes[0]:
                f.write("%s\n" % tag)
            f.close()

    elif command == ['q']:
        print('here I am')
        break
    else:
        print('Wrong command form, please enter the command again.')
