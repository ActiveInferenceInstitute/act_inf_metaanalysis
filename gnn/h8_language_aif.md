# GNN Sketch: Predictive Language Comprehension

# GNN Version: 1.0

# Illustrative structural sketch for hypothesis H8 (LANGUAGE_AIF).
# It states the minimal generative-model structure that assertions about H8
# presuppose: a listener infers an intended meaning from word forms, and can
# keep reading or re-read.

## GNNSection

ActInfPOMDP

## GNNVersionAndFlags

GNN v1

## ModelName

Predictive Language Comprehension (illustrative sketch for H8)

## ModelAnnotation

Illustrative structural sketch, not evidence. This file says nothing about how
much support H8 has in the corpus; those numbers come from the scored
nanopublications (`output/data/assertion_summary.json`) and the manuscript.

Hypothesis identifiers as used across this project:

- config key: `H8`
- code identifier: `LANGUAGE_AIF`
- RDF URI: `http://activeinference.institute/ontology/H8_LANGUAGE_AIF`

Structure sketched:

- 2 hidden states: the intended meaning is reading A, or reading B
- 2 observations: the observed word form fits reading A, or reading B
- 2 actions: keep reading, or re-read the passage
- Example parameters only; no value here is an estimate from the meta-analysis
  corpus, and the sketch is not part of any pipeline stage

Known limitation of the sketch: a single-factor model cannot represent the
hierarchical structure of language (phonology, syntax, semantics, discourse).
This file collapses the hierarchy into one "which reading" state. It also takes
no position on the open question that H8's contradicting evidence raises, namely
whether a predictive-error quantity adds explanatory gain over non-framework
accounts of language processing.

## StateSpaceBlock

# Generative model parameters

A[2,2,type=float]    # Likelihood matrix: P(observation | hidden state)
B[2,2,2,type=float]  # Transition matrix: B[next_state, previous_state, action]
C[2,type=float]      # Preference vector over observations
D[2,1,type=float]    # Prior belief over hidden states

# Hidden state

s[2,1,type=float]    # Hidden state (posterior belief)

# Observation

o[2,1,type=int]      # Observation (one-hot encoded)

# Action

u[1,type=int]        # Action taken

## Connections

D>s
s-A
A-o
s-B
B>u
u>s

## InitialParameterization

# Example lexicon: P(word form fits reading A | intended meaning A) = 0.80;
# P(word form fits reading B | intended meaning B) = 0.75

A={
  (0.80, 0.25),
  (0.20, 0.75)
}

# Example transitions, written one nested block per action. B is stored as
# (next_state, previous_state, action); per-action slices are column-stochastic:
# rows are next states, columns are previous states. Action 0 = keep reading, so
# the current reading mostly persists; action 1 = re-read, which can move belief
# toward the other reading.

B={
  ( (0.85, 0.20), (0.15, 0.80) ),
  ( (0.20, 0.85), (0.80, 0.15) )
}

# Neutral preference: no observation is preferred in advance of the sentence

C={(0.5, 0.5)}

# Example prior: both readings start equally likely

D={(0.5, 0.5)}

## Equations

A[o,s] = P(o | s) with o = 0 "word form fits reading A" and o = 1 "word form
fits reading B". Single-observation Bayesian perception is
q(s) = D[s] A[o,s] / sum_j D[j] A[o,j].

B[:,:,0] = keep reading, B[:,:,1] = re-read. For a chosen action u the predicted
next-state belief is q_next = B[:,:,u] q, and an actual next state is sampled
from P(s_next | s,u) = B[:,s,u].

The quantity the sketch makes explicit is the mismatch between the word form
that was read and the implicit prediction carried by q(s): H8's supporting
evidence reports effects of that mismatch on reading time and on
prediction-related ERP components, and its contradicting evidence reports those
same effects without needing the framework's account of them.

## Time

Static

## ActInfOntologyAnnotation

A=LikelihoodMatrix
B=TransitionMatrix
C=PreferenceVector
D=Prior
s=HiddenState
o=Observation
u=Action

## ModelParameters
b_tensor_order: next_state_previous_state_action

num_hidden_states: 2
num_obs: 2
num_actions: 2
num_timesteps: 2

## Footer

Predictive Language Comprehension v1 - GNN Representation.
Illustrative sketch for H8 / LANGUAGE_AIF. Not evidence, not an estimate.

## Signature

Cryptographic signature goes here
