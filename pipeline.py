import conducto as co
from inspect import cleandoc
import sys

# Docker Images
###############

# for playing the game tick-at-a-time
game_of_life= co.Image(dockerfile='conway/Dockerfile',
                       context='conway')

# for animating the whole story
# imagemagick = co.Image(image="jweissig/alpine-imagemagick:latest")

# Command Templates
###################

# use strict mode so that errors draw attention
header = "set -euo pipefail"


# create the start state and stash it
initialize_grid = cleandoc('''
    {header}
    to_grid '11000011
             01010011
             10001001
             10111000
             10000000
             00100011
             10101001
             01001100' > grid.json

    # store it as the only item in a list (subsequent grids coming soon)
    cat grid.json | jq '[.]' | tee grids.json
    cat grids.json | conducto-temp-data puts --name "grids"
''').format(header=header)

# normalize grid representation
show_grid = cleandoc('''
     {header}
     # get most recent grid
     conducto-temp-data gets --name "grids" | jq '.[-1]' > grid.json

     # make an image
     cat grid.json | to_png grid.png {i}
     conducto-temp-data put --name "image_{i}.png" --file grid.png
     IMAGE_URL=$(conducto-temp-data url --name "image_{i}.png" | sed 's/"//g')

     # display it
     echo -n "<ConductoMarkdown>
     ![grid{i}]($IMAGE_URL)
     </ConductoMarkdown>"
''')

# create metadata for each cell
find_neighborhoods = cleandoc('''
     {header}
     # get most recent grid
     conducto-temp-data gets --name "grids" | jq '.[-1]' > grid.json

     # consider population density
     cat grid.json | as_neighborhoods > neighborhoods.json
     echo "Neighborhood Samples:"
     cat neighborhoods.json | jq '[first, last]'

     # store neighborhoods for rule consumption
     cat neighborhoods.json | conducto-temp-data puts --name neighborhoods_{i}
''')

rule_header_template = header + '\n' + cleandoc('''
     # get neighborhoods
     conducto-temp-data gets --name neighborhoods_{i} > neighborhoods.json
''')

# which cells die because of too-few neighbors?
isolate = cleandoc('''
     {rule_header}
     cat neighborhoods.json \\
         | jq 'map(select(.alive == true and .neighbors < 2)
                   | .alive = false)' \\
         | tee isolations.json \\
         | conducto-temp-data puts --name isolations_{i}

     cat isolations.json
''')

# which cells survive because of ideal neighbor density?
survive = cleandoc('''
     {rule_header}
     cat neighborhoods.json \\
         | jq 'map(select(.alive == true
                          and (.neighbors == 2 or .neighbors == 3))) '\\
         | tee survivals.json \\
         | conducto-temp-data puts --name survivals_{i}

     cat survivals.json
''')

# which cells die because of crowding?
crowd = cleandoc('''
     {rule_header}
     cat neighborhoods.json \\
         | jq 'map(select(.alive == true and .neighbors > 3)
                   | .alive = false)' \\
         | tee crowdings.json \\
         | conducto-temp-data puts --name crowdings_{i}

     cat crowdings.json
''')

# which cells come alive because of reproduction?
reproduce = cleandoc('''
     {rule_header}
     cat neighborhoods.json \\
         | jq 'map(select(.alive == false and .neighbors == 3)
                   | .alive = true)' \\
         | tee reproductions.json \\
         | conducto-temp-data puts --name reproductions_{i}

     cat reproductions.json
''')

# which cells were dead and stay dead
ignore = cleandoc('''
     {rule_header}
     cat neighborhoods.json \\
         | jq 'map(select(.alive == false and .neighbors != 3)
                   | .alive = false)' \\
         | tee ignores.json \\
         | conducto-temp-data puts --name ignores_{i}

     cat ignores.json
''')

# pull updated cells into grid for next tick
next_grid = cleandoc('''
     {header}
     # get grids so far
     conducto-temp-data gets --name "grids" > grids.json

     # get rule outputs
     conducto-temp-data gets --name isolations_{i}    | jq '.[]' > isolations.json
     conducto-temp-data gets --name survivals_{i}     | jq '.[]' > survivals.json
     conducto-temp-data gets --name crowdings_{i}     | jq '.[]' > crowdings.json
     conducto-temp-data gets --name reproductions_{i} | jq '.[]' > reproductions.json
     conducto-temp-data gets --name ignores_{i}       | jq '.[]' > ignores.json

     # make grid from them
     cat isolations.json survivals.json crowdings.json reproductions.json ignores.json \\
         | jq -s . \\
         | to_grid \\
         | tee new_grid.json


     # append it to the grid list
     cat grids.json | jq ". + [$(cat new_grid.json)]" \\
         | tee updated_grids.json \\
         | conducto-temp-data puts --name "grids"

     cat updated_grids.json
''')

# Pipeline Definition
#####################

# root node
def life() -> co.Serial:

    with co.Serial(image=game_of_life) as pipeline:

        pipeline["initialize grid"] = co.Exec(initialize_grid)

        # TODO: instead of modeling a fixed number of clock ticks
        # use a lazy node to extend this until a grid state is repeated
        for i in range(3):

            # turn the templates above into commands for this tick
            def cmd(template):
                rule_header = rule_header_template.format(i=i)
                output = template.format(i=i,
                                         header=header,
                                         rule_header=rule_header)
                return output

            with co.Serial(name=f"tick {i}",
                           image=game_of_life) as iteration:

                iteration["show grid"]      = co.Exec(cmd(show_grid))
                iteration["find neighbors"] = co.Exec(cmd(find_neighborhoods))

                with co.Parallel(name=f"apply_rules",
                               image=game_of_life) as rules:

                    rules["isolate"] = co.Exec(cmd(isolate))
                    rules["survive"] = co.Exec(cmd(survive))
                    rules["crowd"] = co.Exec(cmd(crowd))
                    rules["reproduce"] = co.Exec(cmd(reproduce))
                    rules["ignore"] = co.Exec(cmd(ignore))

                iteration["next grid"] = co.Exec(cmd(next_grid))

    return pipeline

if __name__ == "__main__":
    co.main(default=life)
