# Find that Meme

A meme retrieval engine.  
http://findthatmeme.herokuapp.com/

## Working
This project uses scrapy to scrape memes from imgflip.com. Scraped meme items go through a scrapy pipeline which recognizes the text in the meme using tesseract-ocr. Binary thresholding is done on the image before the text is recognized by pytesseract. If the the text is recognized the meme is pushed to mongodb instance hosted at mlab.com else the item is dropped.

The `build_index.py` script calculates tf-idf values for each meme and stores them in the db.

Tornado web app queries db to fetch scores and calculate cosine similarity between query and stored scores.

## Usage
#### Downloading corpora for nltk
`python -m nltk.downloader stopwords`  
`python -m textblob.download_corpora`
#### Running the spider
`scrapy crawl memes -L INFO`
#### Build index and run the server
```
python build_index.py
python server.py
```
visit: localhost:8080

### Resources
tesseract trained data - https://github.com/johnlinp/meme-ocr

----
python version - 3.5.2
