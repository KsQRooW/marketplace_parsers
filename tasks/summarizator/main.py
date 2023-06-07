from transformers import pipeline

from functions.timer import timer


@timer
def summarize(text):
    summarizer_bart_cnn = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    result = summarizer_bart_cnn(text, max_length=150, min_length=50, do_sample=False)
    return result[0]["summary_text"]
