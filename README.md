# connect4.py
A solver for [Connect 4](https://en.wikipedia.org/wiki/Connect_Four) written in python which achieves near-optimal play.

Thanks to [Pascal Pons](https://github.com/PascalPons/connect4) for inspiration of many of the methods used in this solver.

## Usage
``` bash
$ python3 connect4.py --mode play_human
---------------
. . . . . . . 5
. . . . . . . 4
. . . . . . . 3
. . . . . . . 2
. . . . . . . 1
. . . o . . . 0
1 2 3 4 5 6 7

Your move:
```

### Parameters
The following parameters can be used with the script:
```
  --mode {play_self,play_human}
```
With **play_self** the solver will play itself until end of game. Default is **play_self**.

```
  --max_depth MAX_DEPTH
```
Maximum search depth for the search algorithm. Default is **14**, which takes no less than a few seconds at most and is near impossible for a human to beat.

```
  --starting_moves STARTING_MOVES
```
Start the game from a sequence of moves gives as a string of numbers representing columns picked.

```
  --starting
```
Change which player starts the game, by default solver starts.

## Performance
The algorithm was tested against an optimal solver at https://connect4.gamesolver.org/. Using search depth of **20** and starting it was able to win every time. Every match took approximately 30 minutes of computation time.
