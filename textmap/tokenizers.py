from .utilities import flatten
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.tokenize import sent_tokenize, word_tokenize, MWETokenizer
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

from sklearn.feature_extraction.text import CountVectorizer

class BaseTokenizer(BaseEstimator, TransformerMixin):
    """
    The abstract tokenizer class
    """

    def __init__(self):
        pass

    def fit(self, X, **fit_params):
        """

        Parameters
        ----------
        X :  collection
            The collection of documents

        Returns
        -------
        self
        """
        self.tokens_by_sent_by_doc_ = None
        return self

    def fit_transform(self, X, **fit_params):
        """

        Parameters
        ----------
        X : collection
            The collection of documents

        Returns
        -------
        The list of lists of tokenized sentences per document
        """
        self.fit(X, **fit_params)
        return self.tokens_by_sent_by_doc_

    def tokens_by_sent_by_doc(self):
        """

        Returns
        -------
        The list of lists of tokenized sentences per document
        """
        return self.tokens_by_sent_by_doc_

    def tokens_by_sent(self):
        """

        Returns
        -------
        The complete list of tokenized sentences
        """
        return flatten(self.tokens_by_sent_by_doc())

    def tokens_by_doc(self):
        """

        Returns
        -------
        The list of tokenized documents
        """

        return [flatten(doc) for doc in self.tokens_by_sent_by_doc()]


class NLTKTokenizer(BaseTokenizer):
    """
    Tokenizes via NLTK sentence and word tokenizers, together with iterations of bigram contraction
    as measured by their Pairwise Mutual Information (PMI) exceeding the 
    minimum MultiWord Expression's (MWE) PMI (min_MWE_PMI) value.


      Parameters
      ----------
      lower_case = bool (default = False)
        Lower-case the sentences before tokenization.

      max_MWE_iterations = int (default = 2)
        The maximal number of recursive bigram contractions

      min_MWE_PMIL: int (default = 12)
        The minimal PMI value to contract a bigram per iteration

    """

    def __init__(self, lower_case = False, max_MWE_iterations=2, min_MWE_PMI=12):

        BaseTokenizer.__init__(self)
        self.max_MWE_iterations = max_MWE_iterations
        self.min_MWE_PMI = min_MWE_PMI
        self.lower_case = lower_case

    def fit(self, X, **fit_params):
        """

        Parameters
        ----------
        X: collection
            The list of documents

        Returns
        -------
        self
        """
        if self.lower_case:
            self.tokens_by_sent_by_doc_ = [
                [word_tokenize(sent.lower()) for sent in sent_tokenize(doc)] for doc in X
            ]
        else:
            self.tokens_by_sent_by_doc_ = [
                [word_tokenize(sent) for sent in sent_tokenize(doc)] for doc in X
            ]

        for i in range(self.max_MWE_iterations):
            bigramer = BigramCollocationFinder.from_documents(self.tokens_by_sent())
            mwes = list(
                bigramer.above_score(
                    BigramAssocMeasures.likelihood_ratio, self.min_MWE_PMI
                )
            )
            if len(mwes) == 0:
                break
            contracter = MWETokenizer(mwes)
            self.tokens_by_sent_by_doc_ = [
                contracter.tokenize_sents(doc) for doc in self.tokens_by_sent_by_doc()
            ]
        return self


class CountVectorizerTokenizer(BaseTokenizer):
    '''
    Uses CountVectorizers document preprocessing and word tokenizer (but NLTK sentence tokenizer) and otherwise behaves
        as NLTKTokenizer
    '''
    def __init__(self, max_MWE_iterations=2, min_MWE_PMI=12):

        BaseTokenizer.__init__(self)
        self.max_MWE_iterations = max_MWE_iterations
        self.min_MWE_PMI = min_MWE_PMI

    def fit(self, X, **fit_params):
        """

        Parameters
        ----------
        X: collection
            The list of documents

        Returns
        -------
        self
        """
        cv_word_tokenize = CountVectorizer().build_tokenizer()
        cv_preprocesser = CountVectorizer().build_preprocessor()
        self.tokens_by_sent_by_doc_ = [
            [cv_word_tokenize(sent) for sent in sent_tokenize(cv_preprocesser(doc))] for doc in X
        ]
        for i in range(self.max_MWE_iterations):
            bigramer = BigramCollocationFinder.from_documents(self.tokens_by_sent())
            mwes = list(
                bigramer.above_score(
                    BigramAssocMeasures.likelihood_ratio, self.min_MWE_PMI
                )
            )
            if len(mwes) == 0:
                break
            contracter = MWETokenizer(mwes)
            self.tokens_by_sent_by_doc_ = [
                contracter.tokenize_sents(doc) for doc in self.tokens_by_sent_by_doc()
            ]
        return self


class StanzaTokenizer(BaseTokenizer):
    pass


