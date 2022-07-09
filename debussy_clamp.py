# -*- coding: utf-8 -*-
"""DeBussy_CLaMP.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wMRuaRDiyjmNEeRj0_Bb740eUtstbUFj

# DeBussy CLaMP (ver. 1.0)

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

!git clone https://github.com/asigalov61/tegridy-tools

!pip install torch

!pip install tqdm
!pip install matplotlib
!pip install torch-summary

!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio
!pip install pretty_midi

#@title Import all needed modules

print('Loading needed modules. Please wait...')
import os
import random
from collections import OrderedDict

from tqdm import tqdm

import matplotlib.pyplot as plt

from torchsummary import summary

if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

print('Loading TMIDIX module...')
os.chdir('/content/tegridy-tools/tegridy-tools')
import TMIDIX

os.chdir('/content/tegridy-tools/tegridy-tools')
from GPT2RGAX import *

from midi2audio import FluidSynth
import pretty_midi
import librosa.display
from IPython.display import Audio

os.chdir('/content/')

"""# (FROM SCRATCH) Download and process MIDI dataset"""

# Commented out IPython magic to ensure Python compatibility.
#@title Solo Piano CLaMP MIDI Dataset
# %cd /content/Dataset/
!wget https://github.com/asigalov61/Tegridy-MIDI-Dataset/raw/master/CLMP/CLMP-Middle-Solo-Piano.zip
!unzip CLMP-Middle-Solo-Piano.zip
!rm CLMP-Middle-Solo-Piano.zip 
# %cd /content/

"""# (Process MIDIs)"""

#@title Process MIDIs with TMIDIX MIDI Processor
full_path_to_MIDI_dataset_directory = "/content/Dataset/" #@param {type:"string"}
sorted_or_random_file_loading_order = False #@param {type:"boolean"}
dataset_ratio = 1 #@param {type:"slider", min:0.1, max:1, step:0.1}
full_path_to_save_processed_MIDIs = "/content/DeBussy_Processed_MIDIs" #@param {type:"string"}

print('TMIDIX MIDI Processor')
print('Starting up...')
###########

files_count = 0

gfiles = []

melody_chords_f = []

nocs = []
times = []
durs = []
pitches = []

wk = [0, 2, 4, 5, 7, 9, 11] # White Notes
bk = [1, 3, 6, 8, 10] # Black Notes

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

        if len(events_matrix1) > 0:

            # recalculating timings
        
            for e in events_matrix1:
                # e[1] = int(e[1] / 2) # Time-shift
                e[2] = int(e[2] / 2) # Duration

            events_matrix1.sort(key=lambda x: x[4], reverse=True) # Sort by pitch H -> L
            events_matrix1.sort(key=lambda x: x[1]) # Then sort by start-times
            
            noc = 254 # Note or Chord (noc)
            color = 0 # Note color (ptc+0 or ptc+128)

            melody_chords = []

            pe = events_matrix1[0]
            
            for i in range(len(events_matrix1)-1):

                time = max(0, min(253, events_matrix1[i][1]-pe[1])) # Time-shift
                dur = max(0, min(253, events_matrix1[i][2])) # Duration
                ptc = max(0, min(127, events_matrix1[i][4])) # Pitch

                if events_matrix1[i][1] > pe[1] and events_matrix1[i+1][1] != events_matrix1[i][1]:
                  # noc = 254 # Single Note
                  # ptc+0 - White Note
                  # ptc+128 - Black Note

                  noc = 254

                  nr = [ptc % 12]
                  if nr in wk:
                    color = 0     
                  else:
                    color = 128

                if events_matrix1[i][1] >= pe[1] and events_matrix1[i+1][1] == events_matrix1[i][1]:
                  # noc = 255 # Chord
                  # ptc+0 - White Chord Note
                  # ptc+128 - Black Chord Note

                  noc = 255

                  cr = [ptc % 12]
                  if cr in wk:
                    color = 0     
                  else:
                    color = 128
                
                if events_matrix1[i][1] == pe[1] and events_matrix1[i+1][1] != events_matrix1[i][1]:
                  # noc = 255 # Chord
                  # ptc+0 - White Chord Note
                  # ptc+128 - Black Chord Note

                  noc = 255

                  cr = [ptc % 12]
                  if cr in wk:
                    color = 0     
                  else:
                    color = 128

                melody_chords.append([noc, time, dur, ptc+color])

                # Stats

                nocs.append(noc)
                times.append(time)
                durs.append(dur)
                pitches.append(ptc)

                pe = events_matrix1[i]

            melody_chords_f.append([fn1, melody_chords])

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

# Dataset stats...
print('Generating dataset stats...')

tavg = sum(times) / len(times)
davg = sum(durs) / len(durs)
pavg = sum(pitches) / len(pitches)
print('Done!')
print('=' * 70)

print('Single notes count', nocs.count(254))
print('Chords notes count', nocs.count(255))
print('Average time-shift', tavg)
print('Average duration', davg)
print('Average pitch', pavg)
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

def str2ints(string):

    ints = [385] 
    ints += [ord(y)+(256) for y in string]
    ints += [256] * (63 - len(ints))
    ints += [385]

    return ints

def ints2string(ints):
    return ''.join([chr(y-256) for y in ints if y > 256 and y < 385])

train_data1 = []

for chords_list in tqdm(melody_chords_f):
    train_data1.extend(str2ints(chords_list[0]))
    for i in chords_list[1][:240]:
      
      train_data1.extend([i[0], i[1], i[2], i[3]]) # [noc, time, dur, ptc]

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

def ints2string(ints):
    return ''.join([chr(y-256) for y in ints if y > 256 and y < 385])

if len(out) != 0:
    
    song = out
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0
    son = [254]
    for s in song[1:]:
      if s < 256:

        if s < 254:
          son.append(s)

        else:
          if len(son) == 3:
            time += son[0]

            dur = ((son[1]) * 2) + 2
            
            channel = 0 # Piano

            if son[2] // 128 != 0:
              pitch = son[2]-128
            else:
              pitch = son[2]
            
            # Velocities for notes and chords:
            if s == 254:
              vel = son[2] # Note velocity == note pitch value

            else:
              vel = son[2] + 20 # Chord velocity == chord pitch values + 20
                               
            song_f.append(['note', time, dur, channel, pitch, vel ])
            
          son = []

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'DeBussy CLaMP',  
                                                        output_file_name = '/content/DeBussy-CLaMP-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

print('Displaying resulting composition...')
fname = '/content/DeBussy-Music-Composition'

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# (TRAIN)"""

#@title Load processed INTs dataset

SEQ_LEN = max_seq

BATCH_SIZE = 16 # Change this to your specs

# DO NOT FORGET TO ADJUST MODEL PARAMS IN GPT2RGAX module to your specs

print('=' * 50)
print('Loading training data...')

data_train, data_val = torch.LongTensor(train_data1[:-(SEQ_LEN * BATCH_SIZE)]), torch.LongTensor(train_data1[-(SEQ_LEN * BATCH_SIZE)-1:])

class MusicSamplerDataset(Dataset):
    def __init__(self, data, seq_len):
        super().__init__()
        self.data = data
        self.seq_len = seq_len

    def __getitem__(self, index):
        rand = random.randint(0, (self.data.size(0)-self.seq_len) // self.seq_len) * self.seq_len
        x = self.data[rand: rand + self.seq_len].long()
        trg = self.data[(rand+1): (rand+1) + self.seq_len].long()
        return x, trg

    def __len__(self):
        return self.data.size(0)

train_dataset = MusicSamplerDataset(data_train, SEQ_LEN)
val_dataset   = MusicSamplerDataset(data_val, SEQ_LEN)
train_loader  = DataLoader(train_dataset, batch_size = BATCH_SIZE)
val_loader    = DataLoader(val_dataset, batch_size = BATCH_SIZE)

print('Total INTs in the dataset', len(train_data1))
print('Total unique INTs in the dataset', len(set(train_data1)))
print('Max INT in the dataset', max(train_data1))
print('Min INT in the dataset', min(train_data1))
print('=' * 50)

print('Length of the dataset:',len(train_dataset))
print('Number of dataset samples:', (len(train_dataset) // SEQ_LEN))
print('Length of data loader',len(train_loader))
print('=' * 50)
print('Done! Enjoy! :)')
print('=' * 50)

#@title Train the model

DIC_SIZE = 256

# DO NOT FORGET TO ADJUST MODEL PARAMS IN GPT2RGAX module to your specs

config = GPTConfig(DIC_SIZE, 
                   max_seq,
                   dim_feedforward=512,
                   n_layer=8, 
                   n_head=8, 
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
                 save_checkpoint_steps=4000)
    
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
full_path_to_model_checkpoint = "/content/DeBussy-CLaMP-Trained-Model.pth" #@param {type:"string"}
torch.save(model.state_dict(), full_path_to_model_checkpoint)
print('Done!')

#@title Load/Reload the model

full_path_to_model_checkpoint = "/content/DeBussy-CLaMP-Trained-Model.pth" #@param {type:"string"}

print('Loading the model...')
config = GPTConfig(256, 
                   max_seq,
                   dim_feedforward=512,
                   n_layer=8, 
                   n_head=8, 
                   n_embd=512,
                   enable_rpr=True,
                   er_len=max_seq)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = GPT(config)

state_dict = torch.load(full_path_to_model_checkpoint, map_location=device)

new_state_dict = OrderedDict()
for k, v in state_dict.items():
    name = k[7:] #remove 'module'
    new_state_dict[name] = v

model.load_state_dict(new_state_dict)

model.to(device)

model.eval()

print('Done!')

summary(model)

"""# (GENERATE)"""

#@title CLaMP Generator

#@markdown NOTE: Please use only English letters without any other characters

CLaMP_prompt = "Can you feel the love tonight" #@param {type:"string"}
number_of_tokens_to_generate = 512 #@param {type:"slider", min:32, max:960, step:16}
temperature = 0.8 #@param {type:"slider", min:0.1, max:1, step:0.1}
show_stats = False #@param {type:"boolean"}

print('=' * 70)
print('DeBussy Notes/Chords Progressions Generator')
print('=' * 70)

print('Generating...')

tokens_range = 256

def str2ints(string):

    ints = [385] 
    ints += [ord(y)+(256) for y in string]
    ints += [256] * (63 - len(ints))
    ints += [385]

    return ints

def ints2string(ints):
    return ''.join([chr(y-256) for y in ints if y > 256 and y < 385])

out = str2ints(CLaMP_prompt)

rand_seq = model.generate(torch.Tensor(out), 
                          target_seq_length=number_of_tokens_to_generate,
                          temperature=temperature,
                          stop_token=tokens_range,
                          verbose=show_stats)
  
out1 = rand_seq[0].cpu().numpy().tolist()

print('=' * 70)
print('Done!')

if show_stats:
  print('=' * 70)
  print('Detokenizing output...')

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0
    son = [254]
    for s in song[1:]:
      if s < 256:
        
        if s < 254:
          son.append(s)

        else:
          if len(son) == 3:

            time += son[0]

            dur = ((son[1]) * 2) + 2
            
            channel = 0 # Piano

            if son[2] // 128 != 0:
              pitch = son[2]-128
            else:
              pitch = son[2]
            
            # Velocities for notes and chords:
            if s == 254:
              vel = son[2] # Note velocity == note pitch value

            else:
              vel = son[2] + 20 # Chord velocity == chord pitch values + 20
                               
            song_f.append(['note', time, dur, channel, pitch, vel ])
            
          son = []

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'DeBussy CLaMP',  
                                                        output_file_name = '/content/DeBussy-CLaMP-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)

    print('Done!')

else:
  print('Models output is empty! Check the code...')
  print('Shutting down...')


print('=' * 70)

print('Displaying resulting composition...')
fname = '/content/DeBussy-CLaMP-Music-Composition'

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title(fname)

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# Congrats! You did it! :)"""