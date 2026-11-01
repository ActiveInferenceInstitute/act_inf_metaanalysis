# GNN Sketch: Prediction Error Minimization

# GNN Version: 1.0

# Illustrative structural sketch for hypothesis H4 (PREDICTIVE_CODING).
# It states the minimal generative-model structure that assertions about H4
# presuppose: predictions, an input that either fits them or does not, and a
# choice between updating the model and keeping it.

## GNNSection

ActInfPOMDP

## GNNVersionAndFlags

GNN v1

## ModelName

Prediction Error Minimization (illustrative sketch for H4)

## ModelAnnotation

Illustrative structural sketch, not evidence. This file says nothing about how
much support H4 has in the corpus; those numbers come from the scored
nanopublications (`output/data/assertion_summary.json`) and the manuscript.

Hypothesis identifiers as used across this project:

- config key: `H4`
- code identifier: `PREDICTIVE_CODING`
- RDF URI: `http://activeinference.institute/ontology/H4_PREDICTIVE_CODING`

Structure sketched:

- 2 hidden states: the current prediction accounts for the input, or the input
  is not yet predicted
- 2 observations: the input matches the prediction, or it mismatches
- 2 actions: update the model, or keep it
- Example parameters only; no value here is an estimate from the meta-analysis
  corpus, and the sketch is not part of any pipeline stage

Known limitation of the sketch: the hierarchical direction of predictive coding
(prediction errors upward, predictions downward) is not expressible in a
single-factor model. This file collapses that hierarchy into one "accounted /
not yet predicted" state. A two-level version would need a second state factor,
which the notation supports but this minimal sketch does not claim.

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

# Example sensor: P(input matches | accounted for) = 0.85;
# P(input mismatches | not yet predicted) = 0.80

A={
  (0.85, 0.20),
  (0.15, 0.80)
}

# Example transitions, written one nested block per action. B is stored as
# (next_state, previous_state, action); per-action slices are column-stochastic:
# rows are next states, columns are previous states. Action 0 = update the model,
# which moves the state toward "accounted for"; action 1 = keep the model, which
# mostly preserves the current state.

B={
  ( (0.90, 0.80), (0.10, 0.20) ),
  ( (0.80, 0.20), (0.20, 0.80) )
}

# Example preference: the system prefers inputs that match its predictions

C={(1.0, 0.0)}

# Example prior: a little more likely that the input is accounted for already

D={(0.6, 0.4)}

## Equations

A[o,s] = P(o | s) with o = 0 "input matches the prediction" and o = 1 "input
mismatches". Single-observation Bayesian perception is
q(s) = D[s] A[o,s] / sum_j D[j] A[o,j].

B[:,:,0] = update the model, B[:,:,1] = keep the model. For a chosen action u
the predicted next-state belief is q_next = B[:,:,u] q, and an actual next state
is sampled from P(s_next | s,u) = B[:,s,u].

Because A links "not yet predicted" to "mismatches", the perception update above
is precisely the prediction-error term that H4's supporting evidence reports in
fMRI and EEG work, and precisely the quantity that its contradicting evidence
claims is explainable without the framework.

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

Prediction Error Minimization v1 - GNN Representation.
Illustrative sketch for H4 / PREDICTIVE_CODING. Not evidence, not an estimate.

## Signature

Cryptographic signature goes here
