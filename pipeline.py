import conducto as co
from inspect import cleandoc
import sys


def life() -> co.Serial:

    # for playing the game tick-at-a-time
    game_of_life= co.Image(dockerfile='conway/Dockerfile',
                           context='conway')

    # for animating the whole story
    # imagemagick = co.Image(image="jweissig/alpine-imagemagick:latest")

    with co.Serial(image=game_of_life) as pipeline:

        pipeline["initialize grid"] = co.Exec(cleandoc(
            '''
                set -euo pipefail
                GRID="$(to_grid '11000110
                                 01010110
                                 10001001
                                 10111000
                                 10000000
                                 00100011
                                 10101001
                                 01001100')"


                # store it as the only item in a list
                # (subsequent grids coming soon)
                echo "$GRID" | jq '[.]' | conducto-temp-data puts --name "grids"
            '''))

        # templates for use in the loop below
        show_grid = cleandoc(
            '''
                 set -euo pipefail
                 IMAGE_KEY=grid_image_{i}.png
                 GRID="$(conducto-temp-data gets --name "grids" | jq '.[-1]')"

                 (set -x ; echo "$GRID" | to_png grid.png {i})
                 conducto-temp-data put --name "$IMAGE_KEY" --file grid.png
                 IMAGE_URL=$(conducto-temp-data url --name $IMAGE_KEY | sed 's/"//g')

                 echo -n "<ConductoMarkdown>
                 ![grid{i}]($IMAGE_URL)
                 </ConductoMarkdown>"
            ''')

        find_neighborhoods = cleandoc(
            '''
                 set -euo pipefail
                 NEIGHBORHOODS_KEY=neighborhoods_{i}

                 (set -x; NEIGHBORHOODS="$(echo "$GRID" | as_neighborhoods)")

                 echo "Neighborhood Samples:"
                 echo "$NEIGHBORHOODS" | jq '[first, last]'
                 echo "$NEIGHBORHOODS" | conducto-temp-data puts --name $NEIGHBORHOODS_KEY
            ''')

        # TODO: instead of modeling a fixed number of clock ticks
        # use a lazy node to extend this until a grid state is repeated
        for i in range(3):
            with co.Serial(name=f"tick {i}", image=game_of_life) as iteration:
                iteration["show grid"] = co.Exec(show_grid.format(i=i))
                iteration["find neighbors"] = co.Exec(find_neighborhoods.format(i=i))

    return pipeline

if __name__ == "__main__":
    co.main(default=life)
