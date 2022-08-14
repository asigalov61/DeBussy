# -*- coding: utf-8 -*-
"""DeBussy_Maker.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/asigalov61/DeBussy/blob/main/Training-Code/DeBussy_Maker.ipynb

# DeBussy Maker (ver. 2.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

Credit for GPT2-RGA code used in this colab goes out @ Sashmark97 https://github.com/Sashmark97/midigen and @ Damon Gwinn https://github.com/gwinndr/MusicTransformer-Pytorch

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2022

***

# (Setup Environment)
"""

#@title nvidia-smi gpu check
!nvidia-smi

#@title Install all dependencies (run only once per session)

!git clone https://github.com/asigalov61/DeBussy

!pip install torch

!pip install tqdm
!pip install matplotlib

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os
import random
import secrets
from collections import OrderedDict

from tqdm import tqdm

import matplotlib.pyplot as plt

from torchsummary import summary

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

print('Loading TMIDIX module...')
os.chdir('/content/DeBussy')

import TMIDIX
from GPT2RGAX import *

os.chdir('/content/')

"""# (FROM SCRATCH) Download and process MIDI dataset"""

#@title ALL-Piano Dataset
!wget --no-check-certificate -O 'ALL-Piano.zip' "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118569&authkey=AAYVqXUlxXmpFqk"
!unzip ALL-Piano.zip

"""# (Process MIDIs)"""

#@title Process MIDIs with TMIDIX MIDI Processor
full_path_to_MIDI_dataset_directory = "/content/ALL-Piano/" #@param {type:"string"}
sorted_or_random_file_loading_order = False #@param {type:"boolean"}
dataset_ratio = 1 #@param {type:"slider", min:0.1, max:1, step:0.1}
full_path_to_save_processed_MIDIs = "/content/DeBussy_Processed_MIDIs" #@param {type:"string"}

print('TMIDIX MIDI Processor')
print('Starting up...')
###########

files_count = 0

gfiles = []

melody_chords_f = []

###########

print('Loading MIDI files...')
print('This may take a while on a large dataset in particular.')

dataset_addr = full_path_to_MIDI_dataset_directory

filez = list()

for (dirpath, dirnames, filenames) in os.walk(dataset_addr):
    filez += [os.path.join(dirpath, file) for file in filenames]
print('=' * 70)

if filez == []:
    print('Could not find any MIDI files. Please check Dataset dir...')
    print('=' * 70)

if sorted_or_random_file_loading_order:
    print('Sorting files...')
    filez.sort()
    print('Done!')
    print('=' * 70)
else:
    print('Randomizing file list...')
    random.shuffle(filez)

print('Processing MIDI files. Please wait...')
for f in tqdm(filez[:int(len(filez) * dataset_ratio)]):
    try:
        fn = os.path.basename(f)
        fn1 = fn.split('.')[0]

        files_count += 1

        #print('Loading MIDI file...')
        score = TMIDIX.midi2ms_score(open(f, 'rb').read())

        events_matrix1 = []

        itrack = 1

        while itrack < len(score):
            for event in score[itrack]:         
                if event[0] == 'note' and event[3] != 9:
                    events_matrix1.append(event)
            itrack += 1
    
        # final processing...

        events_matrix1.sort(key=lambda x: x[4], reverse=True) # Sort by pitch H -> L
        events_matrix1.sort(key=lambda x: x[1]) # Then sort by start-times

        if len(events_matrix1) > 0:

            # recalculating timings

            for e in events_matrix1:
                e[1] = int(e[1] / 10) # Time-shift
                e[2] = int(e[2] / 10) # Duration

            melody_chords = []

            pe = events_matrix1[0]

            cho = []

            for e in events_matrix1:

                if  e[1]-pe[1] == 0:
                  cho.append([e[1]-pe[1], e[2], e[4], e[5]])
                else:
                  melody_chords.append(cho)
                  
                  cho = []
                
                  cho.append([e[1]-pe[1], e[2], e[4], e[5]])


                pe = e
        melody_chords_f.append(melody_chords)

        gfiles.append(f)

    except KeyboardInterrupt:
        print('Saving current progress and quitting...')
        break  

    except:
        print('Bad MIDI:', f)
        continue
        
print('=' * 70)
print('Done!')   
print('=' * 70)

print('Saving...')
TMIDIX.Tegridy_Any_Pickle_File_Writer(melody_chords_f, full_path_to_save_processed_MIDIs)
print('Done!')   
print('=' * 70)

"""# (PROCESS)"""

#@title Process and prep INTs...
randomize_dataset = True #@param {type:"boolean"}

print('=' * 70)
print('Prepping INTs dataset...')

if randomize_dataset:
    print('=' * 70)
    print('Randomizing the dataset...')
    random.shuffle(melody_chords_f)
    print('Done!')
    
print('=' * 70)
print('Processing the dataset...')

train_data1 = []

for melody_chords in tqdm(melody_chords_f):

  train_data1.extend([0, 0, 0, 0]) # Zero / Intro Tokens

  for m in melody_chords:
    if len(m) == 1:
      noc = 638 # Note
    else:
      noc = 639 # Chord

    chord = [noc]

    chord.extend([max(1, min(253, m[0][0]))])
    chord.extend([max(1, min(253, m[0][1]))+256])

    for mm in m:
      if mm[2]+512 not in chord:
        chord.append(mm[2]+512)

    train_data1.extend(chord)

print('Done!')        
print('=' * 70)
        
print('Total INTs:', len(train_data1))
print('Minimum INT:', min(train_data1))
print('Maximum INT:', max(train_data1))
print('Unique INTs:', len(set(train_data1)))
print('=' * 70)

#@title Save INTs
TMIDIX.Tegridy_Any_Pickle_File_Writer(train_data1, '/content/DeBussy_INTS')

#@title Test the resulting INTs dataset...

print('Sample INTs:', train_data1[:15])

out = train_data1[:1600]

if len(out) != 0:
    
    song = out
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0
    son = [song[0]]
    for s in song[1:]:

        if s < 638:
          son.append(s)

        else:
          if len(son) > 2:

            time += son[1] * 10

            dur = (son[2] - 256) * 10
            
            channel = 0 # Piano

            if son[0] == 638:

                vel = 80
            else:
                vel = 110

            for ss in son[3:]:
              pitch = ss - 512
                              
              song_f.append(['note', time, dur, channel, pitch, vel ])
            
            son = []
            son.append(s)

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'DeBussy',  
                                                        output_file_name = '/content/DeBussy-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

"""# (TRAIN)"""

#@title Load processed INTs dataset

SEQ_LEN = max_seq

BATCH_SIZE = 16 # Change this to your specs

# DO NOT FORGET TO ADJUST MODEL PARAMS IN GPT2RGAX module to your specs

print('=' * 50)
print('Loading training data...')

data_train, data_val = torch.LongTensor(train_data1), torch.LongTensor(train_data1)

class MusicSamplerDataset(Dataset):
    def __init__(self, data, seq_len):
        super().__init__()
        self.data = data
        self.seq_len = seq_len

    def __getitem__(self, index):

        rand = secrets.randbelow((self.data.size(0)-(self.seq_len)) // (self.seq_len)) * (self.seq_len)

        x = self.data[rand: rand + self.seq_len].long()
        trg = self.data[(rand+1): (rand+1) + self.seq_len].long()
        
        return x, trg

    def __len__(self):
        return self.data.size(0)

train_dataset = MusicSamplerDataset(data_train, SEQ_LEN)
val_dataset   = MusicSamplerDataset(data_val, SEQ_LEN)
train_loader  = DataLoader(train_dataset, batch_size = BATCH_SIZE)
val_loader    = DataLoader(val_dataset, batch_size = BATCH_SIZE)

print('=' * 50)
print('Total INTs in the dataset', len(train_data1))
print('Total unique INTs in the dataset', len(set(train_data1)))
print('Max INT in the dataset', max(train_data1))
print('Min INT in the dataset', min(train_data1))
print('=' * 50)
print('Length of the dataset:',len(train_dataset))
print('Number of batched samples per epoch:', len(train_data1) // max_seq // BATCH_SIZE)
print('=' * 50)
print('Sample train dataset:', train_dataset[0])
print('Sample val dataset:', val_dataset[0])
print('=' * 50)
print('Train loader length:', len(train_loader))
print('Val loader length:', len(val_loader))
print('=' * 50)
print('Done! Enjoy! :)')
print('=' * 50)

#@title Train the model

DIC_SIZE = 640

# DO NOT FORGET TO ADJUST MODEL PARAMS IN GPT2RGAX module to your specs

config = GPTConfig(DIC_SIZE, 
                   max_seq,
                   dim_feedforward=512,
                   n_layer=16, 
                   n_head=16, 
                   n_embd=512,
                   enable_rpr=True,
                   er_len=max_seq)

# DO NOT FORGET TO ADJUST MODEL PARAMS IN GPT2RGAX module to your specs

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = GPT(config)

model = nn.DataParallel(model) # Multi-GPU training...

model.to(device)

#=====

init_step = 0
lr = LR_DEFAULT_START
lr_stepper = LrStepTracker(d_model, SCHEDULER_WARMUP_STEPS, init_step)
eval_loss_func = nn.CrossEntropyLoss(ignore_index=DIC_SIZE)
train_loss_func = eval_loss_func

opt = Adam(model.parameters(), lr=lr, betas=(ADAM_BETA_1, ADAM_BETA_2), eps=ADAM_EPSILON)
lr_scheduler = LambdaLR(opt, lr_stepper.step)


#===

best_eval_acc        = 0.0
best_eval_acc_epoch  = -1
best_eval_loss       = float("inf")
best_eval_loss_epoch = -1
best_acc_file = '/content/gpt2_rpr_acc.pth'
best_loss_file = '/content/gpt2_rpr_loss.pth'
loss_train, loss_val, acc_val = [], [], []

for epoch in range(0, epochs):
    new_best = False
    
    loss = train(epoch+1, 
                 model, train_loader, 
                 train_loss_func, 
                 opt, 
                 lr_scheduler, 
                 num_iters=-1, 
                 save_checkpoint_steps=1000)
    
    loss_train.append(loss)
    
    eval_loss, eval_acc = eval_model(model, val_loader, eval_loss_func, num_iters=-1)
    loss_val.append(eval_loss)
    acc_val.append(eval_acc)
    
    if(eval_acc > best_eval_acc):
        best_eval_acc = eval_acc
        best_eval_acc_epoch  = epoch+1
        torch.save(model.state_dict(), best_acc_file)
        new_best = True

    if(eval_loss < best_eval_loss):
        best_eval_loss       = eval_loss
        best_eval_loss_epoch = epoch+1
        torch.save(model.state_dict(), best_loss_file)
        new_best = True
    
    if(new_best):
        print("Best eval acc epoch:", best_eval_acc_epoch)
        print("Best eval acc:", best_eval_acc)
        print("")
        print("Best eval loss epoch:", best_eval_loss_epoch)
        print("Best eval loss:", best_eval_loss)

#@title Eval funct to eval separately if needed

#=====

init_step = 0
lr = LR_DEFAULT_START
lr_stepper = LrStepTracker(d_model, SCHEDULER_WARMUP_STEPS, init_step)
eval_loss_func = nn.CrossEntropyLoss(ignore_index=DIC_SIZE)
train_loss_func = eval_loss_func

opt = Adam(model.parameters(), lr=lr, betas=(ADAM_BETA_1, ADAM_BETA_2), eps=ADAM_EPSILON)
lr_scheduler = LambdaLR(opt, lr_stepper.step)


eval_loss, eval_acc = eval_model(model, val_loader, eval_loss_func, num_iters=-1)

"""# (MODEL SAVE/LOAD)"""

#@title Save the model

print('Saving the model...')
full_path_to_model_checkpoint = "/content/DeBussy-Trained-Model.pth" #@param {type:"string"}
torch.save(model.state_dict(), full_path_to_model_checkpoint)
print('Done!')

"""# Congrats! You did it! :)"""