# game directory

The "game" is separate from the "server," as the server will only maintain connections and direct the game state. The game state is simply what displays to show, whether to start a new match, and handle other displayable things. Inputs from the user are processed by the server, and the server will decide what can be done about that input by commanding the game.

```
Server -> Game input -> Game state -> Visual display/audio
```
