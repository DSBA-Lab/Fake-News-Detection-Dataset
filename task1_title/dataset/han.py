from .build_dataset import FakeDataset

import torch
import os


class HANDataset(FakeDataset):
    def __init__(self, datadir, split, tokenizer, max_word_len, max_sent_len, saved_data_path=False):
        super(HANDataset, self).__init__(datadir=datadir, split=split, tokenizer=tokenizer)

        self.max_word_len = max_word_len
        self.max_sent_len = max_sent_len

        # load data
        self.saved_data_path = saved_data_path
        if self.saved_data_path:
            self.data = torch.load(os.path.join(saved_data_path, f'{split}.pt'))

    def transform(self, sent_list):
        sent_list = sent_list[:self.max_sent_len]
        doc = [self.tokenizer.encode(sent)[:self.max_word_len] for sent in sent_list] 
        
        return doc
    
    def padding(self, doc):
        num_pad_doc = self.max_sent_len - len(doc)
        num_pad_sent = [max(0, self.max_word_len - len(sent)) for sent in doc]

        doc = [sent + [self.tokenizer.pad_token_id] * num_pad_sent[idx] for idx, sent in enumerate(doc)]
        doc = doc + [[self.tokenizer.pad_token_id] * self.max_word_len for i in range(num_pad_doc)]
            
        return doc

    def __getitem__(self, i):

        if self.saved_data_path:
            doc = {}
            for k in self.data['doc'].keys():
                doc[k] = self.data['doc'][k][i]

            label = self.data['label'][i]

            return doc, label
        
        else:
            news_idx = self.data_info.iloc[i]
            news_info = self.data[str(news_idx['id'])]
        
            # label
            label = 1 if news_idx['label']=='fake' else 0
        
            # input
            sent_list = [news_info['title']] + news_info['text']
            
            # transform and padding
            doc = self.transform(sent_list)
            doc = self.padding(doc)

            doc = {'input_ids':torch.tensor(doc)}

            return doc, label


    def __len__(self):
        if self.saved_data_path:
            return len(self.data['doc']['input_ids'])
        else:
            return len(self.data)
