# -*- coding: utf-8 -*-
"""Bengio-NN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VP0RBua8YLcS6D2us_vxb_ZvDE-0399O

**Natural Language Processing**

**Bengio et al.'s Neural Language Model**

Warning! This program trains a neural network on a large dataset. Training can take a long time.

# Getting Started

We are going to implement Bengio et al.'s 2003 neural language model. This model will allow us to train word embeddings that we will use to perform some interesting tasks later in the program.

We will be using PyTorch, but we will implement the neural network from scratch in this program (as opposed to using the prebuilt layers in PyTorch's neural network module).

## Install Libraries and Download the Training Data
"""

import nltk

nltk.download('brown')

from nltk.corpus import brown

"""# Loading and Preprocessing the Data

First we load the training corpus using the code snippet below. We are using the Brown corpus. Because of runtime and memory constraints, we will only use one third of it for training.
"""

brown_corpus = brown.sents()
brown_corpus = brown_corpus[:int(len(brown_corpus)/3)]
print(brown_corpus[0])

"""We can see that `brown_corpus` has already had sentence segmentation and word tokenization done for us. It is given to us as a list of lists (aka. sentences) of strings (aka. words).

### Lowercasing

As with most word embedding models, we will convert all words to lower case. There is one complication, which is that `brown_corpus` is not a "normal" list of lists; it is actually an NLTK class called `ConcatenatedCorpusView` that is immutable, so we can't do the lowercasing in place. We must create a new list of lists to hold the lowercased version of the corpus.
"""

# The argument original_corpus is an nltk.corpus.reader.util.ConcatenatedCorpusView
# The return type should be a list of lists of strings 
def lowercase_corpus(original_corpus):
  sentences = []
  for sent in original_corpus:
    s = []
    for word in sent:
      word = word.lower()
      s.append(word)
    sentences.append(s)
  return sentences

corpus = lowercase_corpus(brown_corpus)
print(corpus[0])

"""### The Vocabulary and Unknown Word Token

Next we need to get the vocabulary of the training corpus. We also want to have an unknown word token `<unk>` so that we have at least some kind of embedding for out-of-vocabulary words that weren't seen at training time.

First, let's count how often each word occurs in the training data.
"""

# The argument corpus is a list of lists of strings
# The return type should be a dictionary (or collections.Counter)
def get_word_counts(corpus):
  vocab_dict = {}
  for sent in corpus:
    for word in sent:
      if word not in vocab_dict:
        vocab_dict[word] = vocab_dict.get(word,0)+1
      else:
        vocab_dict[word]+=1
  return vocab_dict

word_counts = get_word_counts(corpus)
print(len(word_counts))

"""Many of the words in the training data are rare words, ie. they have very small counts. In fact, many words occur only once in the entire training corpus. We want to replace those words that occur only once with the meta-token `<unk>` so that we can use those words' contexts to train the unknown word token's embedding."""

# The argument corpus is a list of lists of strings
# The argument word_counts is a dictionary (or collections.Counter)
# No return value; modifies corpus in place
def replace_rare_words(corpus, word_counts):
  for sent_idx, sent in enumerate(corpus):
    for word_idx, word in enumerate(sent):
      if word_counts[word] is 1:
        corpus[sent_idx][word_idx] = "<unk>"


replace_rare_words(corpus, word_counts)
new_word_counts = get_word_counts(corpus)
print(len(new_word_counts))

"""Here is a bit of code to get the new (smaller) vocabulary and also add the start and end tokens. We will train a word embedding for every word in this list."""

vocabulary = list(new_word_counts.keys())
vocabulary.extend(['<s>', '</s>'])
vocabulary.sort()
print(len(vocabulary))

"""# Formatting the Data for the Neural Network

Now let's format our preprocessed data so tha we can give it to a neural network as input. The input to this model is the set of $k$ context words $w_{i-k}, \ldots, w_{i-1}$ of a given word $w_i$, where each context word is represented as a one-hot vector.

A one-hot vector is simply a feature vector where every position is 0 except for one, which is 1. In this case, each position in the vector corresponds to a word in the vocabulary. For example, if our vocabulary is `["apple", "banana", "coconut"]`, then the vector for "apple" is `(1,0,0)`, while the vector for "banana" is `(0,1,0)`. The position that is 1 in the vector tells you which word the vector represents.

So our next step is to convert a word from the training data into its one-hot vector representation. For convenience, let's first build a dictionary so that we can look up words' positions more quickly.
"""

vocabulary = {vocabulary[i]:i for i in range(len(vocabulary))}

"""Now fill in the following code snippet to convert a word into a one-hot vector. The return type is a `torch.Tensor`, which supports many of the same functions as the `numpy.array` data type that we have previously used. See [the documentation here](https://pytorch.org/docs/stable/tensors.html)."""

import torch

# The argument word is a string
# The argument vocabulary is a dictionary {string: int}
# The return type should be a torch.Tensor of size |V|
def convert_to_one_hot(word, vocabulary):
  n = len(vocabulary)
  one_hot_vec = torch.zeros([1,n],dtype = torch.float32)
  word_idx = vocabulary[word]
  one_hot_vec[0][word_idx] = 1
  return one_hot_vec

print(convert_to_one_hot('!', vocabulary))

"""Now we just need to reorganize our training data into "n-grams". We want to build pairs `(word, context)`, where `word` is the index of the word in the vocabulary and `context` is a list of one-hot vectors, for every word in the training data.

There are a few wrinkles to keep in mind for this function: 

- Because the training set is so large, we don't have enough memory to hold all the one-hot context vectors for the entire training set; we need to use a generator function instead. When we train the neural network in a later section, we will want to run the training examples in random order, so we also need to randomize the order of the training pairs yielded by this function.

- While we are generating "n-grams", we are using $k$, not $n$, where $k = n-1$. Also, remember to use the start and end tokens where necessary.
"""

import random

# The argument corpus is a list of lists of strings
# The argument vocabulary is a dictionary {string: int}
# The argument k is an int
# The yield type should be a list of tuples (int, list of torch.Tensors)
def generate_training_pairs(corpus, vocabulary, k=4):

  random.shuffle(corpus)
  for sent in corpus:
    sent = ['<s>']*k+sent+['</s>']
    for index, word in enumerate(sent):
      word_idx = 0
      context_vec = []
      if word != '<s>':
        word_idx = vocabulary[word]
        for i in range(index-k,index):
          context_vec.append(convert_to_one_hot(sent[i], vocabulary))
        yield (word_idx, context_vec)
      

for word, _ in generate_training_pairs(corpus, vocabulary):
  print(word)
  break
for word, _ in generate_training_pairs(corpus, vocabulary):
  print(word)
  break
for word, _ in generate_training_pairs(corpus, vocabulary):
  print(word)
  break

"""# Building the Neural Network

Now we are ready to build the neural network itself. Recall from lecture that Bengio et al.'s network is as follows:

$\mathbf{e}_j = \mathbf{Ew}_j \text{ for } j \in [i-k, i-1]$

$\mathbf{x} = [\mathbf{e}_{i-k}, \ldots, \mathbf{e}_{i-1}]$

$\mathbf{h} = \text{tanh}(\mathbf{W_1x} + \mathbf{b_1})$

$\mathbf{\hat{y}} = \text{softmax}(\mathbf{W_2h} + \mathbf{b_2})$

Here $\mathbf{w_j}$ refers to the one-hot vectors we just generated for the context works. The output $\mathbf{\hat{y}}$ is the language model probability distribution $p(w_i | w_{i-k}, \ldots, w_{i-1})$ over words in the vocabulary. After this network is trained, the embedding layer $\mathbf{E}$ can be used to get word embeddings for all words in the vocabulary.
"""

from math import sqrt
import torch.nn.functional

# Also turn on Pytorch's automatic gradient calculations
# The argument parameter_size is a tuple of ints
# The return type should be a torch.Tensor
def initialize_parameter(parameter_size):
  weight = torch.randn(parameter_size[0],parameter_size[1],requires_grad=True)
  torch.nn.init.xavier_normal_(weight, gain=1.0)
  return weight
  

class NLM:

  # The argument vocabulary_size is an int
  # The argument embedding_length is an int
  # No return value
  def __init__(self, vocabulary_size, embedding_length=64, k=4):
    self.embedding_length = embedding_length
    self.E = initialize_parameter((embedding_length, vocabulary_size))
    self.w1 = initialize_parameter((256,256)) 
    self.b1 = initialize_parameter((256,1))
    self.w2 = initialize_parameter((vocabulary_size,256)) 
    self.b2 = initialize_parameter((vocabulary_size,1))


  # The argument context is a list of torch.Tensors
  # The return type should be a torch.Tensor
  def forward_pass(self, context):
    
    X = torch.empty(self.embedding_length,0)
    for index, c in enumerate(context):
      c = torch.transpose(c,0,1)
      if index is 0:
        ej = torch.matmul(self.E, c)
        X = ej
        continue
      ej = torch.matmul(self.E, c)
      X = torch.cat((X,ej),0)

    h_a = torch.matmul(self.w1,X)
    h_a = torch.add(h_a,self.b1)
    h = torch.tanh(h_a)
    
    y_a = torch.matmul(self.w2,h)
    y_a = torch.add(y_a, self.b2)
    
    y_hat = torch.nn.functional.log_softmax(y_a,dim=0)
   
    return y_hat

model = NLM(len(vocabulary))
print(model)

"""## The Parameters

Before we talk about the individual equations, let's get one quick function out of the way. Recall that a neural network's parameters are a bunch of weight matrices (usually denoted $\mathbf{W}$) and bias vectors (usually denoted $\mathbf{b}$). 

The values in these parameters need to be initialized to random, small values. Let's use Xavier initialization, where the parameter values are sampled from a normal distribution with mean 0 and variance $\frac{2}{(n_{in} + n_{out})}$.


- $n_{in}$ and $n_{out}$ are the incoming and outgoing dimensions of this parameter.

- There is a PyTorch function called `torch.randn()` that samples random numbers from a normal distribution with mean 0 and variance 1 (ie. the standard distribution); see [the documentation here](https://pytorch.org/docs/stable/generated/torch.randn.html). We can use this function as a shortcut; all we have to do is change the variance.

- We also need to enable PyTorch's automatic gradient calculations for this parameter (we don't want to have to do that calculus by hand!). Use the function `torch.Tensor.requires_grad()` before returning the initialized parameter.

## The Embedding Layer

$\mathbf{e}_j = \mathbf{Ew}_j \text{ for } j \in [i-k, i-1]$

We can see from this equation that the embedding layer $\mathbf{E}$ is a matrix that is multiplied with a vector $\mathbf{w}_j$ (of length $|V|$) to produce a vector $\mathbf{e}_j$, ie. the embedding for word $w_j$. 

Word embeddings can be whatever length you want, as long as you have enough data to train them. 100-300 dimensions is a common range for word embedding lengths; to save some memory and compute time, we will use just 64 dimensions for this assignment.

So what are the dimensions of $\mathbf{E}$? Here's what we know:

- $\textbf{w}_j$ is a vector of length $|V|$.
- $\mathbf{e}_j$ is a vector of length 64.

If we rewrite the above equation in terms of dimensions, we get $(n \times m) \cdot (|V| \times 1) = (64 \times 1)$, which clearly tells us what $n$ and $m$ should be. Edit the `__init__()` function in the skeleton code to initialize $\mathbf{E}$ with the correct dimensions.

Also edit the `forward_pass()` function to implement this embedding layer equation and compute the $\mathbf{e}_j$'s. (HINT: PyTorch provides a function `torch.matmul()` that you can use; see [the documentation here](https://pytorch.org/docs/stable/generated/torch.matmul.html).)

## The Concat Layer

$\mathbf{x} = [\mathbf{e}_{i-k}, \ldots, \mathbf{e}_{i-1}]$

Actually, PyTorch does not consider concatenation to be a layer, but some neural network libraries do (like Keras). This equation is very simple: the $k$ embeddings $\mathbf{e}_j$ from the previous section need to be concatenated together to form one extra-long vector to be used in the rest of the network. In other words, this "layer" takes as input `k` vectors of length `embedding_length` and outputs a single vector of length `k` $\times$ `embedding_length`.

Edit the `forward_pass()` function to implement this equation and compute $\mathbf{x}$. (HINT: PyTorch provides a function `torch.cat()`; see [the documentation here](https://pytorch.org/docs/stable/generated/torch.cat.html).)

## The Hidden Layer

$\mathbf{h} = \text{tanh}(\mathbf{W_1x} + \mathbf{b_1})$

The Universal Approximation Theorem tells us that a neural network with a single hidden layer can model any function we want. This is that hidden layer; it computes the intermediate representation $\mathbf{h}$. There are two parameters, the weight matrix $\mathbf{W}_1$ and the bias vector $\mathbf{b}_1$.

Hidden layers don't usually change the representation size, so the input and output dimensions are the same for this layer. Again, we can rewrite the equation in terms of dimensions to find out what the sizes of  $\mathbf{W}_1$ and $\mathbf{b}_1$ should be:

$(n \times n) \cdot (320 \times 1) + (m \times 1) = (320 \times 1)$

The `__init__()` function initializes $\mathbf{W}_1$ and $\mathbf{b}_1$, and `forward_pass()` implements this equation and compute $\mathbf{h}$. (PyTorch provides a function `torch.tanh()` that you can use; see [the documentation here](https://pytorch.org/docs/stable/generated/torch.tanh.html).)

## The Output Layer

$\mathbf{\hat{y}} = \text{softmax}(\mathbf{W_2h} + \mathbf{b_2})$

Finally, we have the output layer. This layer looks a lot like the hidden layer, except it needs to output $\mathbf{\hat{y}}$, which is a probability distribution over the vocabulary, ie. a vector of length $|V|$.

The `__init__()` function initializes $\mathbf{W}_2$ and $\mathbf{b}_2$, and `forward_pass()` implements this equation and compute $\mathbf{\hat{y}}$. 

There is one wrinkle, which is that we don't actually want to use a raw softmax function. PyTorch provides another function `torch.nn.functional.log_softmax()` that takes the log after applying softmax; see [the documentation here](https://pytorch.org/docs/stable/nn.functional.html#log-softmax). Since we will want to get the log probabilities for calculating cross-entropy loss later anyway, we might as well do it now and take advantage of PyTorch's implementation of the log-softmax combo (there are other advantages related to numerical stability of the implementation).

# Training with Stochastic Gradient Descent

Now that we have the neural network, it's time to train using gradient descent. For ease of implementation, we will use stochastic, rather than batch or mini-batch gradient descent, and a fixed learning rate.

Training with stochastic gradient descent is basically a loop that 
- runs a single training example through the network to produce the log probability distribution over the output vocabulary, aka. the forward pass over the computation graph;
- calculates the value of the loss function using the network output and the gold standard label;
- takes the gradient and performs backpropagation, aka. the backward pass over the computation graph; and
- updates the parameter weights based on the gradient and the learning rate.

Fill in the code snippet below by implementing this training loop. Here are some details and hints to keep in mind:

- An epoch is one pass through the entire training dataset. Most neural networks take multiple epochs to converge; for simplicity, we will use a fixed number of epochs, rather than using an adaptive approach like early stopping.

- We will use the standard cross-entropy loss, aka. negative log likelihood loss, for multi-class classification; our output is a probability distribution over classes (words in the vocabulary). If the gold standard word is $w_i$, then the cross-entropy loss is $- \log p(w_i | w_{i-k}, \ldots, w_{i-1})$. (We can get the loss very easily by using the output of `NLM.forward_pass()`.)

- PyTorch provides a function `backward()` that calculates and backpropagates the gradient; see [the documentation here](https://pytorch.org/docs/stable/autograd.html#torch.autograd.backward). We can call `backward()` on any variable that contains the output of a PyTorch computation graph (ie. the loss, which is calculated directly from the output of `NLM.forward_pass()`).

- To do the actual updates, we can access the gradient at a given point in the computation graph using `<parameter_name>.grad` and simply assigning it a new value.

- Finally, we need to reset the gradients in the computation graph to zero before the next training example is processed. You can use the "private" function `<parameter_name>.grad.zero_()` to do this.

Before we run this code snippet, make sure to have enough time to let it run for five to seven hours!
"""

import datetime

# The argument model is an NLM
# The argument corpus is a list of lists of strings
# The argument vocabulary is a dictionary {string: int}
# The argument learning_rate is a float
# No return value
def train(model, corpus, vocabulary, learning_rate=0.1):
  for word_context in generate_training_pairs(corpus, vocabulary):
    log_y = model.forward_pass((word_context)[1])
    loss = -log_y[(word_context)[0]]
    loss.backward()
  
    with torch.no_grad():
      model.w1 -= learning_rate*model.w1.grad
      model.w2 -= learning_rate*model.w2.grad
      model.E -= learning_rate*model.E.grad
      model.b1 -= learning_rate*model.b1.grad
      model.b2 -= learning_rate*model.b2.grad
    
      model.w1.grad.zero_()
      model.w2.grad.zero_()
      model.E.grad.zero_()
      model.b1.grad.zero_()
      model.b2.grad.zero_()

print(datetime.datetime.now())
train(model, corpus, vocabulary)
print(datetime.datetime.now())

"""That took a long time to train! Let's save the model so we don't lose our work."""

import pickle
with open('bengio-nn.pickle', 'wb') as f:
  pickle.dump(model, f)

from google.colab import files
files.download('bengio-nn.pickle')

"""If you ever need to load that saved model again (eg. because your Colab session timed out or was interrupted), you can get it back easily."""

from google.colab import files
import pickle

uploaded_files = files.upload()
f = list(uploaded_files.values())[0]
model = pickle.loads(f)

"""We have run the training data through the neural network once so far. One training pass through the data is called an epoch. Most neural networks require several epochs (ie. several passes through the training data) to converge. This is due to how gradient descent works: each training example updates the weights by a small amount, so it takes a large number of updates to get anywhere.

If you have time, run the training snippet again multiple times to improve performance. (While it is possible to overfit by running too many epochs, it is unlikely that you will run into this problem in the amount of time alotted for this assignment.) You will need at least four to five epochs before you start to see good performance.

# Using and Evaluating Embeddings

Now that we have a trained model, we can use the embedding layer $\mathbf{E}$ to get word embeddings for any word in the vocabulary.
"""

embedding_matrix = model.E

"""We are going to run an intrinsic evaluation on our learned embeddings. The task is word similarity using the WordSim353 dataset from [Finkelstein et al. (2002)](https://dl.acm.org/doi/10.1145/503104.503110). The test data is in the provided file `wordsim1.tab`. The following code snippet prompts you to upload the file and then reads in the test data as a pair of lists `[(word1, word2)]` and `[gold_similarity_score]`."""

from google.colab import files

uploaded_files = files.upload()
file_content = str(list(uploaded_files.values())[0], 'utf-8')

word_pairs, gold_scores = [], []
for line in file_content.split('\n')[1:]:
  if len(line) == 0:
    continue

  line = line.split()
  word_pairs.append((line[0].lower(), line[1].lower()))
  gold_scores.append(float(line[2]))

print(word_pairs[0])
print(gold_scores[0])

"""To evaluate the quality of our word embeddings, we need to use them to score the similarity of the word pairs in the test data. We can then compare our embedding-based similarity scores to the human-annotated, gold standard similarity scores.

We will use the cosine similarity between our word embeddings to predict the word similarity. Recall that cosine similarity is

$\cos(v, w) = \cfrac{v \cdot w}{|v| |w|}$

Fill in the code snippet below to implement cosine similarity. (PyTorch provides functions `torch.dot()` and `torch.norm()` implementing the linear algebra operations.) 

One thing to keep in mind is, since our embeddings are `torch.Tensor`'s, the output of any calculation done with them will also be a `torch.Tensor`. Thus, the result of calculating cosine similiarity will be a `torch.Tensor` containing just one scalar value; use `item()` to get the raw value out before returning it. 
"""

# The arguments embedding1 and embedding2 are torch.Tensors
# The return type should be a float
def get_cosine_similarity(embedding1, embedding2):
  cosine_similarity = (torch.dot(embedding1,embedding2))/(torch.norm(embedding1)*torch.norm(embedding2))
  return cosine_similarity.item()

"""Finally, we are ready to evaluate. Since we are comparing similarity scores, which are continuous values, rather than class labels like in a classification problem, the familiar precision, recall, and F-measure metrics don't make sense here. 

Instead, we will use Spearman's $\rho$, which measures rank correlation. This metric doesn't care what actual number we output as our similarity score, only that, if word pair A has a higher gold standard similarity score than word pair B, then we should predict a higher similarity score for word pair A than for word pair B. In other words, as long as our scores would sort the word pairs in the same order as the gold standard scores, we will get a high $\rho$.

We need to iterate through the test set, getting the word embeddings for each word pair and calculating the cosine similarity. Then we compare the list of gold standard similarity scores with our predicted similarity scores using `scipy.stats.spearmanr()`; see [the documentation here](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html). Fill in the following code snippet to do this:
"""

from scipy.stats import spearmanr

# The argument word_pairs is a list of tuples of strings
# The argument gold_scores is a list of floats
# The argument embedding matrix is a torch.Tensor
# The argument vocabulary is a dictionary {string: int}
# The return type should be a scipy.stats.SpearmanrResult
def evaluate_wordsim(word_pairs, gold_scores, embedding_matrix, vocabulary):
  similarity_list=[]
  for pairs in word_pairs:
    if pairs[0] not in vocabulary:
      word_one_index = vocabulary["<unk>"]
    else:
      word_one_index = vocabulary[pairs[0]]
    if pairs[1] not in vocabulary:
      word_two_index = vocabulary["<unk>"]
    else:
      word_two_index = vocabulary[pairs[1]]
      
    e_one = embedding_matrix[:,word_one_index]
    e_two = embedding_matrix[:,word_two_index]
    similarity_list.append(get_cosine_similarity(e_one,e_two))
  return spearmanr(similarity_list,gold_scores)

print(evaluate_wordsim(word_pairs, gold_scores, embedding_matrix, vocabulary))

"""All done! Make sure your model is saved, and use the "File" menu to download this notebook."""