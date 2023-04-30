import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import tkinter.messagebox as mbox
import os
import numpy as np
from numpy.random import uniform
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio
import RPi.GPIO as rg
import time
from threading import Thread

#####################
#                   #
#     Sample Pi     #
#                   #
#   Basic Sampler   #
#     In Python     #
#                   #
#####################

# This Project is about 


# Class for GPIO LED
# Class {Led} supports multithreading GPIO 
# LEDs are dimming when keyboard inputs are given
class Led:
  def __init__(self):
    self.ledPlusPin = [17, 27, 22]
    
    # Frequency for pwm
    # this could affect optimization!!!
    self.pwm_frequency = 60
    rg.setmode(rg.BCM)
    rg.setup(self.ledPlusPin, rg.OUT)
    self.pwm = [rg.PWM(self.ledPlusPin[0], 120), 
                rg.PWM(self.ledPlusPin[1], 120), 
                rg.PWM(self.ledPlusPin[2], 120)]
    
    self.target_duty_cycle = [0, 0, 0]
    self.current_duty_cycle = [0, 0, 0]
    
    # When Led class instantiated, 3 threads are generated
    self.isrunning = True
    self.threads = []
    for i in range(0, 3):
      t = Thread(target=self.dimming, args=(i,))
      t.start()
      self.threads.append(t)

  # This function changes target_duty_cycle
  # Called from Key Pressed Event and Key Released Event
  def change_target_duty_cycle(self, led, duty_cycle):
    if duty_cycle < 0:
      duty_cycle = 0
    elif duty_cycle > 100:
      duty_cycle = 100
    self.target_duty_cycle[led] = duty_cycle

  # Dimming, duty cycle goes toward target_duty_cycle slowly, asyncronously
  def dimming(self, led):    
    try:
        self.pwm[led].start(100)
        while self.isrunning:
          cur = self.current_duty_cycle[led]
          tar = self.target_duty_cycle[led]
          if cur < tar:
            cur += 1
          elif cur > tar:
            cur -= 1
          self.pwm[led].ChangeDutyCycle(cur)
          self.current_duty_cycle[led] = cur
          time.sleep(1/self.pwm_frequency)
    finally:
        self.pwm[led].stop()
    
  def __del__(self):
    self.isrunning = False
    for t in self.threads:
      t.join()
    for p in self.pwm:
      p.stop()
    rg.cleanup()

# tkinter Press and Release event error fixing
os.system('xset r off')

# dictionary between keycode => note
dic_key_note = {24:'C5', 25:'D5', 26:'E5', 27:'F5', 28:'G5', 29:'A5', 30:'B5', 
                31:'C6', 32:'D6', 33:'E6', 34:'F6', 35:'G6', 
                11:'C#5', 12:'D#5', 14:'F#5', 15:'G#5', 16:'A#5', 18:'C#6', 19:'D#6', 21:'F#6',
                52:'C4', 53:'D4', 54:'E4', 55:'F4', 56:'G4', 57:'A4',58:'B4',59:'C5', 60:'D5', 61:'E5',
                39:'C#4', 40:'D#4', 42:'F#4', 43:'G#4', 44:'A#4', 46:'C#5', 47:'D#4',
                113:'Prev', 114:'Next'}

#dictionary between note => index in pitched_sample[current_sample]
dic_note_idx = {'C4':0, 'C#4':1, 'D4':2, 'D#4':3, 'E4':4, 'F4':5, 'F#4':6, 'G4':7, 'G#4':8, 'A4':9, 'A#4':10, 'B4':11,
                'C5':12, 'C#5':13, 'D5':14, 'D#5':15, 'E5':16, 'F5':17, 'F#5':18, 'G5':19, 'G#5':20, 'A5':21, 'A#5':22, 'B5':23, 
                'C6':24,'C#6':25, 'D6':26, 'D#6':27, 'E6':28, 'F6':29, 'F#6':30, 'G6':31}


### About sampling (Especially, pitch shifting) and storing


# List of original audio file as AudioSegment
sample_list = []

# idx of current sample
current_sample = -1

# Current Octave number
current_octave = 5

# Temporarily pitch shifted samples are stored here
pitched_sample = []

# List of notes what I`m pressing currently
dic_current_playing_note_player = {}


### Functions about sampleing


# Select wav file in my PC, Load the selected sound and pitched sound too.
def load_sample_export_pitched_wav():
  wav_ext = r"*.wav"
  
  # Read file
  ### You should use only 16bit wav file!!!
  ### OtherWise, big noise would be included in audio
  file = filedialog.askopenfilenames(filetypes=(("WAV file", wav_ext),("all files", "*.*")), initialdir=os.getcwd)
  en_filepath.config(state="normal")
  en_filepath.delete(0,tk.END)
  if not file or file == '':
    return
  
  # Display filename on GUI entry
  filename = os.path.basename(file[0]).split('/')[-1]
  en_filepath.insert(tk.END, filename)
  en_filepath.config(state="readonly")
  
  # Load original sound
  sound = AudioSegment.from_wav(file[0])
  
  sample_list.append(sound)
  change_current_sample(len(sample_list)-1)

  current_pitched_sample = []
  
  # Re-pitch the sound and store them into pitched_sample
  for octaves in np.linspace(-1, 2, 37):
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    hipitch_sound = sound._spawn(sound.raw_data, 
                      overrides={'frame_rate':new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(44100)
    hipitch_sound.set_sample_width(2)
    current_pitched_sample.append(hipitch_sound)
    
  pitched_sample.append(current_pitched_sample)

# Change the current selected sample
# This function called when new sample is loaded or change sample to previous loaded sample
def change_current_sample(idx):
    global current_sample
    current_sample = idx
    for player in dic_current_playing_note_player.values():
      player.stop()
    dic_current_playing_note_player.clear()

# Select chord at combobox and click Play button
# Then this function called
# Play the chord you selected (multiple play possible)
def play_chord():
  note = com_note.get()
  chord = com_chord.get()
  
  idx = dic_note_idx[note+str(current_octave)]
  if chord == 'Maj':
    idx_list = [idx, idx + 4, idx + 7]
  elif chord == 'Min':
    idx_list = [idx, idx + 3, idx + 7]
  elif chord == 'Sus2':
    idx_list = [idx, idx + 2, idx + 7]
  elif chord == 'Sus4':
    idx_list = [idx, idx + 5, idx + 7]
  elif chord == 'Dim':
    idx_list = [idx, idx + 3, idx + 6]
  elif chord == 'Aug':
    idx_list = [idx, idx + 4, idx + 8]
  elif chord == 'Single Note':
    idx_list = [idx]
  
  for i in range(0, len(idx_list)):
    sound_of_note = pitched_sample[current_sample][idx_list[i]]
    sound_of_note.set_sample_width(2)
    player = simpleaudio.play_buffer(sound_of_note.raw_data, 2, 2, 44100)
  return

# This function would be called in Event handler
# Helps dimming of LED by changing duty_cycle 
# The value of duty_cycle is associated with currently pressed notes on keyboard
def change_target_duty_by_count_dic():
  cnt = [0, 0, 0]
  for note in dic_current_playing_note_player:
    oct = int(note[-1]) - 4
    cnt[oct] += 1
  for i in range(3):
    num = cnt[i]
    if num == 0:
      my_led.change_target_duty_cycle(i, 0)
    else:
      my_led.change_target_duty_cycle(i, 88+num)
  return

# When the key pressed, play each mapped note
def key_press_handler(event):
  if event.keycode not in dic_key_note or current_sample < 0:
    return
  if event.keycode == 113 or event.keycode == 114:
    return
  note = dic_key_note[event.keycode]
  idx = dic_note_idx[note]
  sound_of_note = pitched_sample[current_sample][idx]
  sound_of_note.set_sample_width(2)
  player = simpleaudio.play_buffer(sound_of_note.raw_data, 2, 2, 44100)
  
  dic_current_playing_note_player[note] = player
  change_target_duty_by_count_dic()

# When the key released, stop that note
def key_release_handler(event):
  if event.keycode not in dic_key_note or current_sample < 0:
    return
  note = dic_key_note[event.keycode]
  player = dic_current_playing_note_player[note]
  player.stop()
  del dic_current_playing_note_player[note]
  change_target_duty_by_count_dic()


### Actually this Helper function didn`t used in this project
### But, I leave this function for the extension
# Compare which note is higher
# 1 for left < right, -1 for left > right
# 0 for same
def compare_note(n1, n2):
  if n1 == n2:
    return 0
  if int(n1[-1]) < int(n2[-1]):
    return 1
  if int(n1[-1]) > int(n2[-1]):
    return -1
  if n1[0] < n2[0]:
    return 1
  if n1[0] > n2[0]:
    return -1
  return 1 if len(n2) > len(n1) else -1


### Main Process ###


if __name__ == "__main__":
  app = tk.Tk()
  app.title('Pi Sampler')

  # Frames
  ### First Line Frame
  fr_load = tk.Frame(app)
  fr_load.pack(fill="x", padx=1, pady=1)
  ### Second Line Frame
  fr_chordplay = tk.Frame(app)
  fr_chordplay.pack(fill="x", padx=1, pady=1)

  # First Line
  ### Load sample Button
  bt_load = tk.Button(fr_load, text="Load Sample", width=10, command= load_sample_export_pitched_wav)
  bt_load.pack(side="left", padx=1, pady=1)

  ### Entry that loaded file name written
  ### If wav file successfully loaded, file name would appear on this component
  en_filepath = tk.Entry(fr_load, width=50, state="disabled")
  en_filepath.pack(side="left", padx=5, pady=1)

  # Second Line
  ### Combobox for selecting root note
  com_note = ttk.Combobox(fr_chordplay, textvariable=tk.StringVar(), width=10, state="readonly")
  com_note.pack(side="left", padx=1, pady=1)
  com_note["values"] = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
  com_note.current(0)

  ### Combobox for selecting chord
  com_chord = ttk.Combobox(fr_chordplay, textvariable=tk.StringVar(), width=10, state="readonly")
  com_chord.pack(side="left", padx=5, pady=1)
  com_chord["values"] = ["Single Note", "Maj", "Min", "Sus2", "Sus4", "Dim", "Aug"]
  com_chord.current(0)

  ### Play Button
  bt_play = tk.Button(fr_chordplay, text="Play", width=10, command= play_chord)
  bt_play.pack(side="right", padx=1, pady=1)

  ### Event Binding
  app.bind("<KeyPress>",key_press_handler)
  app.bind("<KeyRelease>",key_release_handler)
  
  # Multi-Threading Led class
  my_led = Led()

  # tkinter main loop
  app.mainloop()