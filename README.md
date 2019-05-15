# Evaluating NEAT-Generated Neural Networks

Full paper: https://docs.google.com/document/d/1RYDobGnhtztXG-a5bSxn1BJhVQe_emYEOz620gRUkPE/edit?usp=sharing

## Purpose

The purpose of this project is to examine the ability of NEAT to generate neural networks that complete tasks humans are good at but computers are not. Although it will likely be unable to definitively disprove its ability to do this, it could certainly prove it. This is significant because it means NEAT is able to generate neural networks that can replace human decision making in situations where it is difficult to explicitly program instructions.

## Method

The neural networks will be tested in a simple simulation that is easily adapted to and played by humans but is difficult to explicitly write AI code for. Each neural network controls a player (black dot) with the capacity to move in four directions and fire a projectile (red dot) in four directions. They each have a timer that counts down from an initial value of ten seconds and a reserve of projectiles. Each time they hit another player with a projectile, that player is removed from the game and all of their life timer value and reserve is added to the player that hit them. In addition, picking up food (green dot) will increase life timer and reserve.

![game board](http://url/to/img.png)