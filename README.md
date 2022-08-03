# pyDragonWarrior

![pyDragonWarrior](/data/images/title.png "pyDragonWarrior Title Image")

A Python based Dragon Warrior clone. Dragon Warrior was chosen as a game with which I have sentimental attachment but
the intent is that it eventually evolves into a unique fantasy game in the spirit of Dragon Warrior instead of being an
out-and-out clone or reimagining.

[![language](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python application](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/python-app.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/python-app.yml)
[![mypy](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/mypy.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/mypy.yml)
[![Pylint](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/pylint.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/pylint.yml)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/justinbeetle/pyDragonWarrior.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/justinbeetle/pyDragonWarrior/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/justinbeetle/pyDragonWarrior.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/justinbeetle/pyDragonWarrior/context:python)

## Installation

1. Install python: Install the latest Python 3 version from https://www.python.org/downloads
2. Install pyDragonWarrior: git clone https://github.com/justinbeetle/pyDragonWarrior.git
 
## Running

Execute pyDragonWarrior/src/pydw/game.py

Note: Running game.py runs a subshell command to install the required Python libraries in a venv using pip.

## Controls

| Control                      | Keyboard Bindings  | Gamepad Bindings |
| ---------------------------- | ------------------ | ---------------- |
| Move                         | WASD or Arrow Keys | D-Pad            |
| Interact or Make Selection   | Enter or E         | A                |
| Enter Menu or Leave Menu     | Space or Q         | B                |
| Exit                         | Escape             | Select           |
| Quick Save                   | F1                 | Menu             |

Note: Gamepad support has only been tested with an XBox One controller.

## Features

* Fully playable game
  * Unlike Dragon Warrior, weapons and armor must be manually equipped and multiple pieces can be owned
  * Unlike Dragon Warrior, stairs are automatically traversed
  * Cursed items have no implemented behavior
* Overworld encounter backgrounds are selected based on nearby terrain
* Provides both a classic and math (default) combat mode, where the math mode is hardcoded to reinforce the learning of
my fourth grader
* Game content is (mostly) configurable, providing a game engine capable of being repurposed to tell alternate stories

## Credits

### Source Material

#### Dragon Warrior

Any [Dragon Warrior](https://en.wikipedia.org/wiki/Dragon_Quest_(video_game)) inspired project or clone is indebted to
the creators of Dragon Warrior. I especially enjoy the 8-bit chip tunes from Dragon Warrior, much to the chagrin of my
family!

* Developer: Chunsoft
* Publisher: Enix and Nintendo of America
* Director: Koichi Nakamura
* Producer: Yukinobu Chida
* Designer: Yuji Horii
* Programmer: Koichi Nakamura
* Artist: Akira Toriyama
* Writer: Yuji Horii
* Composer: Koichi Sugiyama

#### Archived Dragon Warrior Materials

Thanks to the people who have preserved the artwork and information from Dragon Warrior to share it with future
generations.

* [Formulas](https://gamefaqs.gamespot.com/nes/563408-dragon-warrior/faqs/61640): Very informative guide on the
mechanics of Dragon Warrior.
* [Gameplay](https://www.youtube.com/watch?v=Fj_eA0f_KtY): My old NES died at some point after I started, so when I want
to compare to the source material now I skip through the speed runs on YouTube.
* [Item Info](https://strategywiki.org/wiki/Dragon_Warrior/Items_and_Equipment)
* [Music](http://www.vgmpf.com/Wiki/index.php?title=Dragon_Warrior_(NES))
* [Script](https://gamefaqs.gamespot.com/nes/563408-dragon-warrior/faqs/54647)
* [Sound Effects](https://www.sounds-resource.com/download/4229/)
* [Sprites](https://www.spriters-resource.com/nes/dw/)

### Art

#### Tilesets

* [Pita Madgwick](https://pita.itch.io/): Beautiful 16x16 pixel tilesets. Looking at them -- especially the overworld
tileset -- makes me happy! These assets are licenced and as such are not stored in the repo. Distributions of the game
will eventually include them.
  * [WONDERDOT RPG Asset Series - Dungeon Tileset<br><img src="https://img.itch.zone/aW1hZ2UvMTUyMDU3LzcwMjI2My5wbmc=/original/kcqpkf.png" width=300>](https://pita.itch.io/rpg-dungeon-tileset)
  * [WONDERDOT RPG Asset Series - Overworld Tileset](https://pita.itch.io/rpg-overworld-tileset)<br><img src="https://img.itch.zone/aW1nLzEzMjA3MzUuZ2lm/original/QaINOc.gif" width=300>
  * [WONDERDOT RPG Asset Series - Village Tileset](https://pita.itch.io/rpg-village-tileset)<br><img src="https://img.itch.zone/aW1nLzE1MjU5NjMuZ2lm/original/Q5Zcnx.gif" width=300>

#### Character Sprites

* [Mega Tiles](https://megatiles.itch.io/): Adorable 16x20 character sprites. These assets are licenced and as such are
not stored in the repo. Distributions of the game will eventually include them.
  * [Tiny Tales Character Sprites - NPC Advanced](https://megatiles.itch.io/tiny-tales-human-npc-advanced-sprite-pack)<br><img src="https://img.itch.zone/aW1hZ2UvMTA0OTE4Ny82MDAyNTMzLmdpZg==/347x500/jWHe53.gif" width=100>
  * [Tiny Tales Character Sprites - NPC Knights](https://megatiles.itch.io/tiny-tales-human-npc-knights-sprite-pack)<br><img src="https://img.itch.zone/aW1hZ2UvMTA0OTE5Ni82MDAyNTI0LmdpZg==/347x500/U070LY.gif" width=100>
  * [Tiny Tales Character Sprites - NPC Nobility](https://megatiles.itch.io/tiny-tales-human-npc-nobility-sprite-pack)<br><img src="https://img.itch.zone/aW1hZ2UvMTA0OTIwNi82MDAyNTI3LmdpZg==/347x500/CyUWin.gif" width=100>

#### Encounter Backgrounds

* [Unsplash](https://unsplash.com/): Encounter background images were sourced from a variety of contributors.  Some
images have been modified.  In game the images are pixelated to better jive with the other pixel graphics.
  * [Lopez Robin](https://unsplash.com/@lopezrobin): [beach<br><img alt="beach" src="data\images\encounter_backgrounds\unsplash\beach.jfif" width=200>](https://unsplash.com/photos/apax4M-4kFI)
  * [Rowan Heuvel](https://unsplash.com/@insolitus): [beach_jungle<br><img alt="beach_jungle" src="data\images\encounter_backgrounds\unsplash\beach_jungle.jfif" width=200>](https://unsplash.com/photos/U6t80TWJ1DM)
  * [Arash Bal](https://unsplash.com/@arashbal): [deciduous_forest<br><img alt="deciduous_forest" src="data\images\encounter_backgrounds\unsplash\deciduous_forest.jfif" width=200>](https://unsplash.com/photos/2Y2sF4lB4-Y)
  * [Imat Bagja Gumilar](https://unsplash.com/@imatbagjagumilar): [deciduous_forest_dark<br><img alt="deciduous_forest_dark" src="data\images\encounter_backgrounds\unsplash\deciduous_forest_dark.jfif" width=200>](https://unsplash.com/photos/jwTvCQQJXh0)
  * [Raimond Klavins](https://unsplash.com/@raimondklavins): [deciduous_forest_light<br><img alt="deciduous_forest_light" src="data\images\encounter_backgrounds\unsplash\deciduous_forest_light.jfif" width=200>](https://unsplash.com/photos/WKfnhCADseQ)
  * [Keith Hardy](https://unsplash.com/@keithhardy2001): [desert<br><img alt="desert" src="data\images\encounter_backgrounds\unsplash\desert.jfif" width=200>](https://unsplash.com/photos/PP8Escz15d8)
  * [Dann Zepeda](https://unsplash.com/@idannzepeda): [desert_city_ruins<br><img alt="desert_city_ruins" src="data\images\encounter_backgrounds\unsplash\desert_city_ruins.jfif" width=200>](https://unsplash.com/photos/uP8Yvwggvmk)
  * [Paul Chambers](https://unsplash.com/@ummmmpaul): [desert_cliff<br><img alt="desert_cliff" src="data\images\encounter_backgrounds\unsplash\desert_cliff.jfif" width=200>](https://unsplash.com/photos/6OFxfVuLUEs)
  * [Austin Anderson](https://unsplash.com/@aanderson0329): [desert_close_mountain<br><img alt="desert_close_mountain" src="data\images\encounter_backgrounds\unsplash\desert_close_mountain.jfif" width=200>](https://unsplash.com/photos/YrYeghM0OgE)
  * [Parastoo Maleki](https://unsplash.com/@blueswallow): [desert_distant_mountain<br><img alt="desert_distant_mountain" src="data\images\encounter_backgrounds\unsplash\desert_distant_mountain.jfif" width=200>](https://unsplash.com/photos/CUDoVGSfUPg)
  * [Mostapha Abidour](https://unsplash.com/@mostaphaabidour): [desert_hill<br><img alt="desert_hill" src="data\images\encounter_backgrounds\unsplash\desert_hill.jfif" width=200>](https://unsplash.com/photos/2zgGXQsGXtQ)
  * [Ivan Aleksic](https://unsplash.com/@ivalex): [gate<br><img alt="gate" src="data\images\encounter_backgrounds\unsplash\gate.png" width=200>](https://unsplash.com/photos/16YxCJSoAek)
  * [Jeremy Cai](https://unsplash.com/@j): [hill_distant_mountain<br><img alt="hill_distant_mountain" src="data\images\encounter_backgrounds\unsplash\hill_distant_mountain.jfif" width=200>](https://unsplash.com/photos/eT1ef3tPglU)
  * [Isaac Quesada](https://unsplash.com/@isaacquesada): [jungle<br><img alt="jungle" src="data\images\encounter_backgrounds\unsplash\jungle.jfif" width=200>](https://unsplash.com/photos/6xxxvB72qB0)
  * [Ehud Neuhaus](https://unsplash.com/@paramir): [jungle_dark<br><img alt="jungle_dark" src="data\images\encounter_backgrounds\unsplash\jungle_dark.jfif" width=200>](https://unsplash.com/photos/iulSk5ChQso)
  * [Conscious Design](https://unsplash.com/@conscious_design): [jungle_light<br><img alt="jungle_light" src="data\images\encounter_backgrounds\unsplash\jungle_light.jfif" width=200>](https://unsplash.com/photos/mLpbHWquEYM)
  * [Hugo Delauney](https://unsplash.com/@ugodly): [pine_forest<br><img alt="pine_forest" src="data\images\encounter_backgrounds\unsplash\pine_forest.jfif" width=200>](https://unsplash.com/photos/ykjsf518lZY)
  * [Dylan Leagh](https://unsplash.com/@dylanleagh): [pine_forest_dark<br><img alt="pine_forest_dark" src="data\images\encounter_backgrounds\unsplash\pine_forest_dark.jfif" width=200>](https://unsplash.com/photos/k5Vj3gx4vHE)
  * [Andrey Kigay](https://unsplash.com/@k1gabyt0): [pine_forest_light<br><img alt="pine_forest_light" src="data\images\encounter_backgrounds\unsplash\pine_forest_light.jfif" width=200>](https://unsplash.com/photos/BWpKTSsiBas)
  * [Stanislav Klimanskii](https://unsplash.com/@klimy4): [plain<br><img alt="plain" src="data\images\encounter_backgrounds\unsplash\plain.jfif" width=200>](https://unsplash.com/photos/8krv1j-huaQ)
  * [Tim Nieland](https://unsplash.com/@timnieland): [plain_cliff<br><img alt="plain_cliff" src="data\images\encounter_backgrounds\unsplash\plain_cliff.jfif" width=200>](https://unsplash.com/photos/gufUJAz_y-A)
  * [Edan Cohen](https://unsplash.com/@edan): [plain_close_mountain<br><img alt="plain_close_mountain" src="data\images\encounter_backgrounds\unsplash\plain_close_mountain.jfif" width=200>](https://unsplash.com/photos/IyjhDTTQitM)
  * [Viateur Hwang](https://unsplash.com/@secretasianman): [plain_deciduous_forest<br><img alt="plain_deciduous_forest" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest.jfif" width=200>](https://unsplash.com/photos/-By1_DpPsBk)
  * [Kirill Shavlo](https://unsplash.com/@svl_photo): [plain_deciduous_forest_cliff<br><img alt="plain_deciduous_forest_cliff" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_cliff.jfif" width=200>](https://unsplash.com/photos/eDguN_ifJjA)
  * [Mathew MacQuarrie](https://unsplash.com/@matmacq): [plain_deciduous_forest_close_mountain<br><img alt="plain_deciduous_forest_close_mountain" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_close_mountain.jfif" width=200>](https://unsplash.com/photos/Lzx4J_Pb3sk)
  * [Angela Loria](https://unsplash.com/@a_lo): [plain_deciduous_forest_distant_mountain<br><img alt="plain_deciduous_forest_distant_mountain" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_distant_mountain.jfif" width=200>](https://unsplash.com/photos/ZAy8srF4rRM)
  * [Achim Ruhnau](https://unsplash.com/@achimr): [plain_deciduous_forest_hill<br><img alt="plain_deciduous_forest_hill" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_hill.jfif" width=200>](https://unsplash.com/photos/tXzU28GOy5k)
  * [Claudel Rheault](https://unsplash.com/@claudelrheault): [plain_distant_mountain<br><img alt="plain_distant_mountain" src="data\images\encounter_backgrounds\unsplash\plain_distant_mountain.jfif" width=200>](https://unsplash.com/photos/ZVbv1akA-l4)
  * [Hayarpi Mkhitaryan](https://unsplash.com/@hayarpi_1): [plain_hill<br><img alt="plain_hill" src="data\images\encounter_backgrounds\unsplash\plain_hill.jfif" width=200>](https://unsplash.com/photos/ppEPKpdPK-0)
  * [Paul Trienekens](https://unsplash.com/@paultrienekens): [plain_pine_forest<br><img alt="plain_pine_forest" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest.jfif" width=200>](https://unsplash.com/photos/9goYHROaqMo)
  * [Mick Haupt](https://unsplash.com/@rocinante_11): [plain_pine_forest_cliff<br><img alt="plain_pine_forest_cliff" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_cliff.jfif" width=200>](https://unsplash.com/photos/hb09G5FZG5k)
  * [Gabriel Phipps](https://unsplash.com/@gabe7753): [plain_pine_forest_close_mountain<br><img alt="plain_pine_forest_close_mountain" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_close_mountain.jfif" width=200>](https://unsplash.com/photos/9CxIoNz41KY)
  * [Christina Brinza](https://unsplash.com/@cbrin): [plain_pine_forest_distant_mountain<br><img alt="plain_pine_forest_distant_mountain" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_distant_mountain.jfif" width=200>](https://unsplash.com/photos/fA2AbDSwEMo)
  * [Kseniia Rastvorova](https://unsplash.com/@hixenia): [plain_pine_forest_hill<br><img alt="plain_pine_forest_hill" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_hill.jfif" width=200>](https://unsplash.com/photos/YhZt03_OJKs)
  * [Daniil Lobachev](https://unsplash.com/@danilal): [river<br><img alt="river" src="data\images\encounter_backgrounds\unsplash\river.jfif" width=200>](https://unsplash.com/photos/Pi1ER8QiK9o)
  * [Jordan McQueen](https://unsplash.com/@jordanfmcqueen): [shore<br><img alt="shore" src="data\images\encounter_backgrounds\unsplash\shore.jfif" width=200>](https://unsplash.com/photos/SDsosT_RRPk)
  * [Yves Sinoir](https://unsplash.com/@neo13): [shore_cliff<br><img alt="shore_cliff" src="data\images\encounter_backgrounds\unsplash\shore_cliff.jfif" width=200>](https://unsplash.com/photos/hZpWdqIMMGw)
  * [Gunnar Ridderström](https://unsplash.com/@gunnarridder): [swamp<br><img alt="swamp" src="data\images\encounter_backgrounds\unsplash\swamp.jfif" width=200>](https://unsplash.com/photos/WHrBWOnfypI)

#### Fonts

* [somepx](https://somepx.itch.io/): [Compass Pro<br><img src="https://img.itch.zone/aW1hZ2UvMjk4NDM1LzUyNzM1MDEucG5n/original/s7yJQ%2B.png" width=300>](https://somepx.itch.io/humble-fonts-free)

### Python Libraries

The pygame library is integral to this project. Migrating to using Tiled maps and leveraging pytmx and pyscroll have
been a really nice improvement, but one that you only see with the licensed assets that are not included in the repo. A
future distribution of the game will include these.

* [pygame](https://github.com/pygame/pygame): Python library for multimedia applications
* [Leif Theden](https://github.com/bitcraft):
  * [pytmx](https://github.com/bitcraft/pytmx): Python library to read Tiled maps
  * [pyscroll](https://github.com/bitcraft/pyscroll): Python library to render Tiled maps

### Tools

#### Python Development Tools

* [mypy](https://github.com/python/mypy): I wouldn't want to work on a large Python project without type annotations.
And without a tool, mypy, to validate them, the type annotations wouldn't be trustworthy.
* [PyCharm](https://www.jetbrains.com/pycharm/): Python IDE
* [Pylint](https://github.com/PyCQA/pylint): Python static code analysis

#### Image and Map Building Tools

* [GIMP](https://www.gimp.org/): Image editor
* [Thorbjørn Lindeijer](https://github.com/bjorn):
  * [Tiled](https://github.com/mapeditor/tiled): 2D map editor
