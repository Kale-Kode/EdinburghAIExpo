from youtube_transcript_api import YouTubeTranscriptApi
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer
from flask import Flask, request, jsonify
from flask_cors import CORS

# LOAD PEGASUS MODEL OUTSIDE THE ENDPOINTS
model_name = "google/pegasus-xsum"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

bert_tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
splitter = TextSplitter.from_huggingface_tokenizer(bert_tokenizer, (512, 1024))

# DEFINE FUNCTIONS

# extract transcript from video_url
def extract_transcript(video_url):
  video_id = video_url.split("=")[1] # retrieve id by splitting the url by '='
  transcript = YouTubeTranscriptApi.get_transcript(video_id) # get the video transcript
  return transcript

# split transcript into chunks/chapters
def split_into_chunks(transcript):
  full_text = ' '.join([line['text'] for line in transcript])

  size = len(full_text.split(' ')) # use the length/size of our input data to determine a suitable range for max_tokens in the next step
  max_tokens = (int(size/4), int(size/2)) # determine a suitable range depending on input data size, so that it produces roughly 4-6 chunks? 
  # splitter = TextSplitter.from_huggingface_tokenizer(bert_tokenizer, max_tokens)
  chunks = splitter.chunks(full_text) # splits the text into chunks using the BERT model above
  return chunks

def timestamp_chunks(chunks, transcript):
   timestamped_chunks = []
   i = 0
   for chunk in chunks:
      # store starting timestamp of this chunk
      timestamp = transcript[i]['start']
      # x will keep track of what position in the chunk we are at corresponding to the lines of transcript
      x = len(chunk)
      # minus each line from x
      while x > 0 and i < len(transcript):
         # update x
         x -= len(transcript[i]['text'])
         i += 1
      # Check if we've exhausted the transcript
      if i > len(transcript):
          break
      # when end of chunk reached, assign original timestamp to this chunk
      timestamped_chunks.append({
          'chunk': chunk,
          'timestamp': timestamp
      })
      # and repeat for the next chunk

   return timestamped_chunks

def summarise_chunks(chunks):
  full_summary = []
  
  batch = tokenizer([chunk['chunk'] for chunk in chunks], truncation=True, padding="longest", return_tensors="pt").to(device)
  translated = model.generate(**batch, min_length=30, num_beams=4, early_stopping=True)
  summaries = tokenizer.batch_decode(translated, skip_special_tokens=True)

  title_batch = tokenizer(summaries, truncation=True, padding="longest", return_tensors="pt").to(device)
  title_translated = model.generate(**title_batch, max_length=20, num_beams=4, early_stopping=True)
  titles = tokenizer.batch_decode(title_translated, skip_special_tokens=True)

  for i, chunk in enumerate(chunks):
        full_summary.append({
            "title": titles[i],
            "text": summaries[i],
            "timestamp": chunk['timestamp']
        })
    
  return full_summary

# DEFINE ENDPOINTS
def summarise(url):
  
  transcript = extract_transcript(url) # Extract transcript and summarize
  chunks = split_into_chunks(transcript)
  chunks = timestamp_chunks(chunks, transcript)
  summary = summarise_chunks(chunks)
  print(summary)

summarise('https://www.youtube.com/watch?v=h6skw_h7Wg8')