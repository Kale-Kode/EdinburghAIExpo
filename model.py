from youtube_transcript_api import YouTubeTranscriptApi
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer
from flask import Flask, request, jsonify
from flask_cors import CORS

# FLASK APP
app = Flask(__name__)
CORS(app)

# LOAD PEGASUS MODEL OUTSIDE THE ENDPOINTS
model_name = "google/pegasus-xsum"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

bert_tokenizer = Tokenizer.from_pretrained("bert-base-uncased")


# DEFINE FUNCTIONS

# extract transcript from video_url
def extract_transcript(video_url):
  #video_url = "https://www.youtube.com/watch?v=wjZofJX0v4M"
  video_id = video_url.split("=")[1] # retrieve id by splitting the url by '='
  transcript = YouTubeTranscriptApi.get_transcript(video_id) # get the video transcript
  return transcript
  # full_transcript = ' '.join([line['text'] for line in transcript]).replace('  ', ' ') # merge lines into a full transcript
  # return full_transcript

# split transcript into chunks/chapters
def split_into_chunks(transcript):
  full_text = ' '.join([line['text'] for line in transcript])

  # # extract timestamps and map them to their position in the text
  # timestamps = {}
  # index = 0
  # for line in transcript:
  #    timestamp = line['start']
  #    timestamps[index] = timestamp
  #    index += len(line['text']) + 1

  size = len(full_text.split(' ')) # use the length/size of our input data to determine a suitable range for max_tokens in the next step
  max_tokens = (int(size/4), int(size/2)) # determine a suitable range depending on input data size, so that it produces roughly 4-6 chunks? 
  splitter = TextSplitter.from_huggingface_tokenizer(bert_tokenizer, max_tokens)
  chunks = splitter.chunks(full_text) # splits the text into chunks using the BERT model above
  return chunks

  # timestamped_chunks = {}
  # pos = 0
  # for chunk in chunks:
  #    pos += len(chunk)+1
  #    timestamped_chunks[timestamps[pos]] = chunk
  # return timestamped_chunks # returns a list of chunks mapped to there start timestamp in the video

def summarise_chunks(chunks):
  full_summary = []
  for chunk in chunks: # summarise each chunk produced by the semantic text splitter
    batch = tokenizer(chunk, truncation=True, padding="longest", return_tensors="pt").to(device)
    translated = model.generate(**batch, min_length=30, num_beams=5, early_stopping=True)
    summary = tokenizer.batch_decode(translated, skip_special_tokens=True)
  
    title_batch = tokenizer(summary, truncation=True, padding="longest", return_tensors="pt").to(device)
    title_translated = model.generate(**title_batch, max_length=20, num_beams=5, early_stopping=True)
    title = tokenizer.batch_decode(title_translated, skip_special_tokens=True)[0]

    full_summary.append({
            "title": title,
            "text": summary
        })
    
  return full_summary
  # full_summary = {}
  # for timestamp, chunk in chunks.values(): # summarise each chunk produced by the semantic text splitter
  #   batch = tokenizer(chunk, truncation=True, padding="longest", return_tensors="pt").to(device)
  #   translated = model.generate(**batch)
  #   summary = tokenizer.batch_decode(translated, skip_special_tokens=True)
  
  #   title_batch = tokenizer(chunk, truncation=True, padding="longest", return_tensors="pt").to(device)
  #   title_translated = model.generate(**title_batch, max_length=20, num_beams=5, early_stopping=True)
  #   title = tokenizer.batch_decode(title_translated, skip_special_tokens=True)[0]

  #   full_summary[timestamp] = {
  #           "title": title,
  #           "text": summary
  #       }
    
  # return full_summary # returns a dictionary of chunks, with their title and summary text mapped to their starting timestamp


# DEFINE ENDPOINTS
@app.route('/summarise', methods=['POST'])
def summarise():
  data = request.json
  print("Received data:", data)  # Debugging line
  url = data.get("video_url")
  if not url:
        return jsonify({"error": "URL is required"}), 400
  
  transcript = extract_transcript(url) # Extract transcript and summarize
  if not transcript:
      return jsonify({"error": "Transcript not found"}), 404

  chunks = split_into_chunks(transcript)
  summary = summarise_chunks(chunks)
  return jsonify({"summary": summary})

# MAIN
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)