# GNN Sketch: Boundary-Maintaining System

# GNN Version: 1.0

# Illustrative structural sketch for hypothesis H1 (FEP_UNIVERSALITY).
# It states the minimal generative-model structure that assertions about H1
# presuppose: a system whose states are bounded, that senses deviation and can
# act to return within bounds.

## GNNSection

ActInfPOMDP

## GNNVersionAndFlags

GNN v1

## ModelName

Boundary-Maintaining System (illustrative sketch for H1)

## ModelAnnotation

Illustrative structural sketch, not evidence. This file says nothing about how
much support H1 has in the corpus; those numbers come from the scored
nanopublications (`output/data/assertion_summary.json`) and the manuscript.

Hypothesis identifiers as used across this project:

- config key: `H1`
- code identifier: `FEP_UNIVERSALITY`
- RDF URI: `http://activeinference.institute/ontology/H1_FEP_UNIVERSALITY`

Structure sketched:

- 2 hidden states: the system's internal state is either "within bounds" or
  "displaced"
- 2 observations: deviation is sensed, or not sensed
- 2 actions: do nothing, or act to restore
- Example parameters only; no value here is an estimate from the meta-analysis
  corpus, and the sketch is not part of any pipeline stage

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

# Example sensor: P(senses no deviation | within bounds) = 0.85;
# P(senses deviation | displaced) = 0.9

A={
  (0.85, 0.10),
  (0.15, 0.90)
}

# Example transitions, written one nested block per action. B is stored as
# (next_state, previous_state, action); per-action slices are column-stochastic:
# rows are next states, columns are previous states. Action 0 = do nothing, so
# the state mostly persists with some drift; action 1 = act to restore, so the
# state moves toward "within bounds" from either starting point.

B={
  ( (0.70, 0.20), (0.30, 0.80) ),
  ( (0.90, 0.90), (0.10, 0.10) )
}

# Example preference: the system prefers observations of "no deviation"

C={(1.0, 0.0)}

# Example prior: usually within bounds

D={(0.7, 0.3)}

## Equations

A[o,s] = P(o | s) with o = 0 "no deviation sensed" and o = 1 "deviation sensed".
Single-observation Bayesian perception is
q(s) = D[s] A[o,s] / sum_j D[j] A[o,j].

B[next,previous,action] gives B[:,:,0] = do nothing and B[:,:,1] = act to
restore. For a chosen action u the predicted next-state belief is
q_next = B[:,:,u] q, and an actual next state is sampled from
P(s_next | s,u) = B[:,s,u]. C is a preference over observations, so a system
that both maintains its boundary and prefers "no deviation" is exactly the
shape H1's "self-organizing system" language presupposes.

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

Boundary-Maintaining System v1 - GNN Representation.
Illustrative sketch for H1 / FEP_UNIVERSALITY. Not evidence, not an estimate.

## Signature

Cryptographic signature goes here
