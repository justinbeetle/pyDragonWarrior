#!/bin/bash

cd $(dirname $(dirname $BASH_SOURCE))

tar cfz licensed_assets.tgz \
   data/licensed_assets/itch.io/finalbossblues/tf_animals \
   data/licensed_assets/itch.io/Mega_Tiles/*/Original \
   data/licensed_assets/itch.io/pita/decorations \
   data/licensed_assets/itch.io/pita/rpg-dungeon-pack_v1.1/tiles_dungeon_v1.1.png \
   data/licensed_assets/itch.io/pita/rpg-overworld-tileset_v1.2/Overworld_Tileset.png \
   data/licensed_assets/itch.io/pita/rpg-overworld-tileset_v1.2/TropicalExtras_Tileset.png \
   data/licensed_assets/itch.io/pita/rpg-village-tileset_v1.0/AltRoofs_Tileset.png \
   data/licensed_assets/itch.io/pita/rpg-village-tileset_v1.0/Village_Tileset.png
