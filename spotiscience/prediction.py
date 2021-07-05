"""
This module implements the main functionality  for data modelling using techniques of Topic Modelling, Mood Prediction and Song Similarity
Author: Cristóbal Veas
Linkedln: https://www.linkedin.com/in/cristobal-veas/
"""

__author__ = "Cristóbal Veas"
__email__ = "cristobal.veas.ch@gmail.com"
__status__ = "planning"


from collections import defaultdict
import numpy as np 
import spacy
from spacy.lang.en.stop_words import STOP_WORDS as SWE
from spacy.lang.es.stop_words import STOP_WORDS as SWS
import string
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import CountVectorizer
from collections import defaultdict
import joblib
import pkg_resources


class SpotiSciencePredicter():

    """
    Class for data modelling.
    Attributes
    ----------
    STOPWORDS: list - list of english stop words (words which are filtered out before or after processing of natural language text)
    NLP: object - natural language processing object used in spacy library
    PUNTUACTION: list - list of  text symbols 
    PATHMODEL: str  path for multi class classification model weights  using a random forest classifier
    """

    def __init__(self):
        self.STOPWORDSENGLISH = list(SWE)
        self.STOPWORDSSPANISH = list(SWS)

        self.NLPENGLISH = spacy.load('en_core_web_lg')
        self.NLPSPANISH = spacy.load('es_core_news_lg')
        self.PUNTUACTION = string.punctuation
        self.PATHMODEL = pkg_resources.resource_filename(__name__,"weights/mood.joblib")

    #----------------
    # TOPIC MODELLING
    #----------------
    def __inner__lyric_to_list(self,lyric):
        """
        Return a list Transform, clean and split sentences returning a list of  lyric's sentences
        Attributes
        ----------
        lyric: str - the lyric of the song
        """
        lyric = lyric.replace("EmbedShare Url:CopyEmbed:Copy","")
        lyric_list = lyric.split("\n")
        lyric_list = [sentence for sentence in lyric_list if len(sentence)>1]
        return lyric_list

    def __inner__spacy_tokenizer(self,lyric,lang):
        """
        Return a list with tokenize sentece of lyric list
        Attributes
        ----------
        lyric: str - the lyric of the song
        lang: the lenguage model used for tokenize (available are spanish and english)
        """
        if "english" in lang:
            mytokens = self.NLPENGLISH(lyric)
            mytokens = [ word.lemma_.lower() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens]
            mytokens = [ word for word in mytokens if word not in self.STOPWORDSENGLISH and word not in self.PUNTUACTION] 
        if "spanish" in lang:
            mytokens = self.NLPSPANISH(lyric)
            mytokens = [ word.lemma_.lower() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens]
            mytokens = [ word for word in mytokens if word not in self.STOPWORDSSPANISH and word not in self.PUNTUACTION] 
        
        mytokens = " ".join([i for i in mytokens])
        return mytokens

    def __inner__lyric_vectorizer(self,lyrics,stop_words,n_grams):
        """
        vectorize the lyrics returning the vectorizer object and a list with the vectorized lyrics
        Attributes
        ----------
        lyrics: list - a list with sentences of lyric.
        stop_words: str - the language used for vectorizer stop words 
        n_grams: tuple - the number of n-grams used for vectorizer  model  (1gram: (1,1) ,  1 or 2 gram (1,2))

        see more info about stop_words and n_grams parameters in sklearn documentation
        https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
        """
        vectorizer = CountVectorizer(min_df=1, max_df=0.9, stop_words=stop_words, token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}',ngram_range=n_grams)
        lyrics_vectorized = vectorizer.fit_transform(lyrics)
        return vectorizer,lyrics_vectorized

    def __train__model(self,lyrics_vectorized,modelname,num_topics):
        """
        train the topic modelling model
        Attributes
        ----------
        lyrics_vectorized: list -  the song lyrics vectorized 
        modelname: str - the name of the model used for Topic MOdelling (available options are "lda","nmf" and "lsi")
        num_topics: int - the number of topics for the model 
        """
    
        if "lda" in modelname:
            # Latent Dirichlet Allocation Model
            model = LatentDirichletAllocation(n_components=num_topics, max_iter=10, learning_method='online',verbose=False)
        if "nmf" in modelname:
        # Non-Negative Matrix Factorization Model
            model = NMF(n_components=num_topics)
        if "lsi" in modelname:
            # Latent Semantic Indexing Model using Truncated SVD
            model = TruncatedSVD(n_components=num_topics)
        model.fit(lyrics_vectorized)
        return model 

    def __inner__selected_topics(self,model, vectorizer, top_n):
        """
        Predict the topics using vectorizer model and topic modelling model 
        Attributes
        ----------
        model: object - the trained topic modelling model
        vectorizer: object -  the trained vectorizer model 
        top_n: int - the max number of words per topic
        """
        RESULTS = defaultdict(list)
        for idx, topic in enumerate(model.components_):
            n_topic = "Topic %d:" % (idx)
            topics = [(vectorizer.get_feature_names()[i], topic[i])
                            for i in topic.argsort()[:-top_n - 1:-1]]
            
            RESULTS[n_topic].append(topics)
        return RESULTS

    def predict_topic_lyric(self,lyric,model='lda',lang='english',stopwords=None,n_grams=(1,1),n_topics=1,top_n=10):
        """
        main method used to predict the topics of lyrics 
        Attributes
        ----------
        lyric: str - the lyrics of the song
        model: str - the name of the model used for Topic MOdelling (available options are "lda","nmf" and "lsi")
        lang: the language of the lyrics (available options are "spanish" and "english")
        stop_words: str - the language used for vectorizer stop words (default is None) 
        n_grams: tuple - the number of n-grams used for vectorizer  model  (1gram: (1,1) ,  1 or 2 gram (1,2)) (default is (1,1))
        n_topics: int - the number of topics for the model  (default is 10)
        top_n: int - the max number of words per topic

        to see more info about models and vectorizer attributes
        https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html
        https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html
        https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html
        https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html
        """
        lyric_list = self.__inner__lyric_to_list(lyric)
        processed_lyric = [self.__inner__spacy_tokenizer(lyric=sentence,lang=lang) for sentence in lyric_list]
        vectorizer, data_vectorized = self.__inner__lyric_vectorizer(processed_lyric,stop_words=stopwords,n_grams=n_grams)
        trained_model = self.__train__model(data_vectorized,modelname=model,num_topics=n_topics)
        topics = self.__inner__selected_topics(trained_model,vectorizer,top_n=top_n)
        return topics


    #---------------
    #Mood Prediction
    #---------------

    def predict_song_mood(self,song):
        """
        main method used to predict the mood of a song 
        Attributes
        ----------
        song: dict - the data of the song 
        """
        predictmodel = joblib.load(self.PATHMODEL)
        moods = {0:'calm',1:'energy',2:'happy',3:'sad'}
        song_features = np.array(list(song.values())[6:]).reshape(-1,1).T
        
        preds = predictmodel.predict(song_features)
        return moods[preds[0]]
        
    #---------------
    #Song Similarity
    #---------------
    def predict_similar_songs(self,object,target,distance='l2',n_features=6,top_n=10):
        """
        main method used to calculate most similar songs
        Attributes
        ----------
        object: str - the id or copy link of the song to analyze
        target: str - the id or copy of the object to search for similar songs (availabel objects are: song or album or playlist)
        distance: str - the type of distance used to predict similar words (available type are l1 or l2, default is l2)
        n_features: int - number of features of song used to predict similarity (default is 6)
                         - model is training with the following features [acousticness, length,danceability, energy, instrumentalness,liveness,valence,loudness,speechiness,tempo,key,time_signature]
        top_n: int - number of most similar songs returns as result (default is 10)

        for more information about features go to spotify song features
        https://developer.spotify.com/documentation/web-api/reference/#category-tracks
        """
        similarity = []
        similar_songs = defaultdict(list)

        object_feature = list(object.values())[n_features:]
        object_name = list(object.values())[1]

        for key in target.keys():
            for song in target[key]:
                target_feature = list(song.values())[n_features:]
                target_name = list(song.values())[1]
                target_artist = list(song.values())[2]

                if object_name not in target_name:
                    object_feature = np.array([float(i)/sum(object_feature) for i in object_feature])
                    target_feature = np.array([float(i)/sum(target_feature) for i in target_feature])
                    if "l2" in distance:
                        n_similarity = np.linalg.norm(object_feature-target_feature)
                    if "l1" in distance: 
                        n_similarity = np.linalg.norm(object_feature-target_feature,ord=1)
                    results = (target_name,target_artist,n_similarity)
                    similarity.append(results)
                    similarity = sorted(similarity ,key =lambda tup:tup[2])
                    similarity = [tup for tup in similarity if tup[2]>0]

            similar_songs[object_name] = similarity[0:top_n]
        return similar_songs