# Evaluating NEAT-Generated Neural Networks

Full paper: https://docs.google.com/document/d/1RYDobGnhtztXG-a5bSxn1BJhVQe_emYEOz620gRUkPE/edit?usp=sharing

## Overview

A population of NEAT-generated neural networks will be tested in a simple simulation that is easily adapted to and played by humans but is difficult to explicitly write AI code for. Each neural network controls a player (black dot) with the capacity to move in four directions and fire a projectile (red dot) in four directions. They each have a timer that counts down from an initial value of ten seconds and a reserve of projectiles. Each time they hit another player with a projectile, that player is removed from the game and all of their life timer value and reserve is added to the player that hit them. In addition, picking up food (green dot) will increase life timer and reserve.

![game board](https://github.com/calvinhirsch/neuroevolution-research-project/blob/master/screenshots/sample-game.png)

The neural networks controlling the players are given inputs based on their current state, the position and velocity of the four nearest players, nearby projectiles, and nearby food. The outputs of the network are the four directions of movement and the four directions in which a projectile can be fired. An unconnected network (topology) with just the input and output nodes is shown below.

The simulation was run for about 2000 generations in each trial, with a population of 49 networks per generation. Due to the sheer number of configuration options, it would take far too long to test each option individually to find an optimal setup, so configurations for each trial were based on adjustments from previous ones. Evaluations on each trial are based on observations and not fitness, which in this simulation only determines how well players do relative to the others it has to play against. It is very difficult to make a measurement of how well the players are doing absolutely for a similar reason to why it’s difficult to hard code an AI for this sort of task — the best behavior is complex and not made up of simple, explicit decisions but rather a culmination of lots of inputs. In order to standardize observations, each final population will be evaluated based on its ability to collect food, avoid projectiles, and hit other players.

## Installation & Use

To run, download the repository and run main.py.

In main.py, constants exist to allow for saving and loading checkpoints.
```
# Frequency that the program saves checkpoints
CHECKPOINT_FREQ = 50;
# Maximum generations to run (set to 99999999 to run forever, can be stopped manually)
MAX_GENS = 3000;
# Checkpoint to load from (set to 0 to start from scratch)
LOAD_CHECKPOINT = 0;
```

The other most likely thing to customize would be the NEAT config file (titled 'config' in the home directory). The NEAT python documentation has descriptions for each config property.

Configs and checkpoints can be saved and later loaded/used to return to an in-progress run.