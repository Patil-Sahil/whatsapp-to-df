import re
import numpy as np
import pandas as pd



def raw_to_df(file, chat_owner_name):
    with open(file, 'r', encoding = 'utf-8') as f:  #read the raw text
        text = f.read()
        
    user_messages = re.split('\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s', text)[2:]  #aggregating users and messages, starting from 3rd element as its relevant messg (this regexcan be different for different mobiles)
    dates = re.findall('\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}', text)[1:]  #aggregaing dates, starting from 2nd as it corresponds to real messages ( this regex can be different for different mobiles)
    
    df= pd.DataFrame({'dates': dates,'user_messg':user_messages})  #df of above collected things
    df['messg_type'] = df.user_messg.apply(lambda x: 'notification' if ':' not in x else 'normal')  #labelling messages as [normal,notification]
    df['user'] = df.loc[df.messg_type == 'normal','user_messg'].apply(lambda x: re.findall("(.+?):",x)[0])  #getting users
    df['messg'] = df.loc[df.messg_type == 'normal','user_messg'].apply(lambda x: re.findall(":(.+)",x)[0])  #getting normal messages
    df.loc[pd.isnull(df.messg),'messg'] = df.loc[pd.isnull(df.messg),'user_messg'].apply(lambda x: re.findall('.+',x)[0])  #getting notificatio messages
    df.drop('user_messg',axis=1,inplace=True)  #dropping redundant col
    
    me = chat_owner_name
    users = [x for x in df.user.unique() if type(x) != np.float]
    users = re.sub(me,'You',"/".join(users)).split('/')
    
    def notif_name_extractor(x, users = users):   #func to extraxt user names
        x = ' '.join(x.split()[:3])
        for name in users:
            if name not in x:
                pass
            else:
                return name

        return 'System'
    
    df.loc[(df.messg_type == 'notification') & (pd.isnull(df.user)),'user'] = df.loc[(df.messg_type == 'notification') & (pd.isnull(df.user)),'messg'].apply(notif_name_extractor)  #applying notif_name_extrator
    
    df.user.replace('You',me,inplace=True)  #replacing 'You' with chat_owners name
    df.loc[df.messg_type == 'notification','messg_type'] = df.loc[df.messg_type == 'notification','messg'].apply(lambda x: 'name_change' if 'changed the subject from' in x else 'notification')  ##splitting notification into [name_change,notification]
    
    df['dates'] = pd.to_datetime(df['dates'], format='%m/%d/%y, %H:%M') # converting dates col to datetime format
    df = df.sort_values('dates').reset_index(drop=True)
    return df



chat_df = raw_to_df('data/chat.txt','Sahil Patil')