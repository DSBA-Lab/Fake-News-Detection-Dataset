from .build_dataset import FakeDataset

import json 
import pandas as pd
import numpy as np
import torch
import os
import random

from tqdm.auto import tqdm

class KoBERTSegDataset(FakeDataset):
    def __init__(self, datadir, split, window_size, tokenizer, vocab, max_word_len=512):
        super(KoBERTSegDataset, self).__init__(
            datadir      = datadir, 
            split        = split, 
            tokenizer    = tokenizer, 
            vocab        = vocab, 
            window_size  = window_size,
            max_word_len = max_word_len
        )

        self.preprocessor()
        
    
    def tokenize(self, src):
        # length
        src = self.length_processing(src)

        src_subtokens = [[self.vocab.cls_token] + sent + [self.vocab.sep_token] for sent in src]
        src_token_ids = [self.tokenizer.convert_tokens_to_ids(s) for s in src_subtokens]
        
        segments_ids = self.get_token_type_ids(src_token_ids)
        segments_ids = sum(segments_ids,[])
        
        src_token_ids = [x for sublist in src_token_ids for x in sublist]
        cls_ids = self.get_cls_index(src_token_ids)
        
        src_token_ids, segments_ids, cls_ids, mask_src, mask_cls = self.padding_bert(
            src_token_ids = src_token_ids,
            segments_ids  = segments_ids,
            cls_ids       = cls_ids
        )
        
        return src_token_ids, segments_ids, cls_ids, mask_src, mask_cls

    
    def __getitem__(self, i, return_txt=False, return_fake_label=False):
        
        doc, target = self.datasets[i], self.targets[i]
        doc_txt = doc
        
        # tokenizer
        src_subtoken_idxs, segments_ids, cls_ids, mask_src, mask_cls = self.tokenize(doc_txt)

        inputs = {
            'src': src_subtoken_idxs,
            'segs': segments_ids,
            'clss': cls_ids,
            'mask_src': mask_src,
            'mask_cls': mask_cls,
        }

        return_values = (inputs, target)

        if return_txt:
            src_txt = self.docs[i]
            return_values = return_values + (src_txt,)

        if return_fake_label:
            src_fake_label = self.fake_labels[i]
            return_values = return_values + (src_fake_label,)
        
        return return_values
    
    def __len__(self):
        return len(self.datasets)