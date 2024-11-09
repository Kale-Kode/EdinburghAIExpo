from youtube_transcript_api import YouTubeTranscriptApi
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch

video_url = "https://www.youtube.com/watch?v=wjZofJX0v4M"
video_id = video_url.split("=")[1] # retrieve id by splitting the url by '='

transcript = YouTubeTranscriptApi.get_transcript(video_id) # get the video transcript
full_transcript = ' '.join([line['text'] for line in transcript]).replace('  ', ' ') # merge lines into a full transcript
size = len(full_transcript.split(' ')) # use the length/size of our input data to determine a suitable range for max_tokens in the next step

from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer

max_tokens = (int(size/4), int(size/2)) # determine a suitable range depending on input data size, so that it produces roughly 4-6 chunks? 
# This is one of the most important parts of this project:
#   we need to find an optimal way of determining how many chunks to produce
#   to find a balance between covering all the topics covered in the video, while also not having too many

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
splitter = TextSplitter.from_huggingface_tokenizer(tokenizer, max_tokens)
chunks = splitter.chunks(full_transcript) # splits the text into chunks using the BERT model above

# code from before for loading pre-trained pegasus-xsum model
model_name = "google/pegasus-xsum"
device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)

for i, chunk in enumerate(chunks): # now we can summarise each chunk produced by the semantic text splitter
  batch = tokenizer(chunk, truncation=True, padding="longest", return_tensors="pt").to(device)
  translated = model.generate(**batch)
  summary = tokenizer.batch_decode(translated, skip_special_tokens=True)
  print(f"Chunk {i}: {chunk}\nSummary: {summary}")