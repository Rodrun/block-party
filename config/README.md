# Configuration

```json
{
    "board": {
        "layout": {
            "name": [x, y, width, height], ...
        }
    }
}
```

__board__: Game board config.

* __layout__: Game board layout
    * __points__: Scoreboard.
    * __lines__: Lines cleared display.
    * __next__: Next block display.
    * __playfield__: Playfield view.
    * __name__: Name tag display.
    * __statistic__: Satistic display.
    * __level__: Level display.

Note that all of the coordinate and dimension values represent percentage of the width or height of the board display. For example, in a 300px x 300px board, a position of (.5, .5) would be (150, 150) converted to absolute position.
