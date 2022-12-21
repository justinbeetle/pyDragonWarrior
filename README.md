# pyDragonWarrior

![pyDragonWarrior Title Image](/data/images/title.png)

A Python based Dragon Warrior clone. Dragon Warrior was chosen as a game with which I have sentimental attachment but
the intent is that it eventually evolves into a unique fantasy game in the spirit of Dragon Warrior instead of being an
out-and-out clone or reimagining.

[![language](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python application](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/python-app.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/python-app.yml)
[![mypy](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/mypy.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/mypy.yml)
[![Pylint](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/pylint.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/pylint.yml)
[![CodeQL](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/codeql.yml/badge.svg)](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/codeql.yml)

## Installation

1. Install python: Install the latest Python 3.10 version from https://www.python.org/downloads
2. Install git: Install the latest git version from https://git-scm.com/downloads
3. Install pyDragonWarrior: git clone https://github.com/justinbeetle/pyDragonWarrior.git

Note: Python 3.10 is recommended for the time being as there isn't yet a stable release of pygame for Python 3.11.
 
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

The interact control does the following in order of precedence:
1. Talks to an NPC if the player character is facing one
2. Opens a chest or door if the player character is on or facing one
3. Takes the stairs if the player character is on a staircase
4. Searches in all other cases

Note: Gamepad support is based on an XBox One controller.  Other controllers have not been tested and may have different
button naming schemes.

## Features

* Fully playable game with a few deviations from Dragon Warrior.  If you get stuck, try using a [Dragon Warrior
walkthrough](https://gamefaqs.gamespot.com/nes/563408-dragon-warrior/faqs) while keeping in mind the following notable
deltas from Dragon Warrior:
  * The [controls](#Controls) are different.  They are streamlined but clumsy and will probably be retooled at some
point.  Stairs are traversed automatically, which can be really annoying in dungeons.
  * Item management is different.  Unlike Dragon Warrior, armor and weapons must be manually equipped and multiple
pieces can be owned.  Items followed by an 'E' are equipped.  Items must be unequipped before they can be sold.  There
are no item caps on the number of herbs and keys you are carrying.  The item menus don't support scrolling yet, so
collect lots of different items at your own peril.
  * Cursed items have no implemented behavior.  Implementing them has never made it to the top of my TODO list because
no one that knows what they were doing would equip them in the first place.
  * Once I make the new Tiled maps using licensed art available, there will be more differences:
    * The new maps frequently have more doors.  Most of the new doors are not locked and can be opened without a key.
They are visually identical to locked doors, so you'll have to try to open them to see.  Don't wait until you have keys!
    * In the new maps I'm coming up with new ways to hide stuff that was previously hidden by the ridiculously few
tiles we could see on screen back in the 1980s.  Be prepared.
* Overworld encounter backgrounds are selected based on nearby terrain
* Provides both a classic and math (default) combat mode, where the math mode is hardcoded to reinforce the learning of
my fourth grader.  Until I make it configurable, you can modify src/pydw/combat_encounter.py to customize the selection
of problems in the add_problem_to_use_dialog method.
* Game content is (mostly) configurable, providing a game engine capable of being repurposed to tell alternate stories

## Building for Distribution

### Using PyInstaller on Windows

1. python -m venv pyinstaller_venv
2. source pyinstaller_venv/Scripts/activate
3. pip install .
4. pip install pyinstaller
5. pyinstaller --onefile --name pyDragonWarrior --icon icon.ico --add-data "game.xml;./"
--add-data "game_licensed_assets.xml;./" --add-data "data;data" --add-data "icon.png;./" --splash data/images/title.png
src/pydw/game.py

### Using Docker

1. docker build -t pydw .
2. docker run pydw (requires X11 forwarding and I haven't tested it yet)

### Using Replit

With a lot of patience, it can be played at https://replit.com/@justinbeetle/pyDragonWarrior?v=1.  It is not a good
experience due to the limited memory and CPU.

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

I've extended Pita's tilesets for use on this project.  Here are some sample images of the new maps.
  * Tantegel Castle Throne Room<br>
![Tantegel Castle Throne Room](/samples/tantegel_lvl2.gif)
  * Map of Alefgard<br>
![Map of Alefgard](/samples/alefgard.png)
  * Brecconary<br>
![Brecconary](/samples/brecconary.gif)
  * Erdrick's Tomb<br>
![Erdrick's Tomb Upper Level](/samples/erdricks_tomb_lvl1.gif)
![Erdrick's Tomb Lower Level](/samples/erdricks_tomb_lvl2.gif)

#### Character Sprites

* [Mega Tiles](https://megatiles.itch.io/): Adorable 16x20 character sprites. These assets are licenced and as such are
not stored in the repo. Distributions of the game will eventually include them.
  * [Tiny Tales Character Sprites - NPC Advanced](https://megatiles.itch.io/tiny-tales-human-npc-advanced-sprite-pack)<br><img src="https://img.itch.zone/aW1hZ2UvMTA0OTE4Ny82MDAyNTMzLmdpZg==/347x500/jWHe53.gif" width=100>
  * [Tiny Tales Character Sprites - NPC Knights](https://megatiles.itch.io/tiny-tales-human-npc-knights-sprite-pack)<br><img src="https://img.itch.zone/aW1hZ2UvMTA0OTE5Ni82MDAyNTI0LmdpZg==/347x500/U070LY.gif" width=100>
  * [Tiny Tales Character Sprites - NPC Nobility](https://megatiles.itch.io/tiny-tales-human-npc-nobility-sprite-pack)<br><img src="https://img.itch.zone/aW1hZ2UvMTA0OTIwNi82MDAyNTI3LmdpZg==/347x500/CyUWin.gif" width=100>

#### Encounter Backgrounds

* [Unsplash](https://unsplash.com/): Encounter background images were sourced from a variety of contributors.  Some
images have been modified.  In game the images are pixelated to better jive with the other pixel graphics.
<table>
   <tr>
      <td><a href="https://unsplash.com/@lopezrobin">Lopez Robin</a>: <a href="https://unsplash.com/photos/apax4M-4kFI">beach<br><img alt="beach" src="data\images\encounter_backgrounds\unsplash\beach.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@insolitus">Rowan Heuvel</a>: <a href="https://unsplash.com/photos/U6t80TWJ1DM">beach_jungle<br><img alt="beach_jungle" src="data\images\encounter_backgrounds\unsplash\beach_jungle.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@arashbal">Arash Bal</a>: <a href="https://unsplash.com/photos/2Y2sF4lB4-Y">deciduous_forest<br><img alt="deciduous_forest" src="data\images\encounter_backgrounds\unsplash\deciduous_forest.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@imatbagjagumilar">Imat Bagja Gumilar</a>: <a href="https://unsplash.com/photos/jwTvCQQJXh0">deciduous_forest_dark<br><img alt="deciduous_forest_dark" src="data\images\encounter_backgrounds\unsplash\deciduous_forest_dark.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@raimondklavins">Raimond Klavins</a>: <a href="https://unsplash.com/photos/WKfnhCADseQ">deciduous_forest_light<br><img alt="deciduous_forest_light" src="data\images\encounter_backgrounds\unsplash\deciduous_forest_light.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@keithhardy2001">Keith Hardy</a>: <a href="https://unsplash.com/photos/PP8Escz15d8">desert<br><img alt="desert" src="data\images\encounter_backgrounds\unsplash\desert.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@idannzepeda">Dann Zepeda</a>: <a href="https://unsplash.com/photos/uP8Yvwggvmk">desert_city_ruins<br><img alt="desert_city_ruins" src="data\images\encounter_backgrounds\unsplash\desert_city_ruins.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@ummmmpaul">Paul Chambers</a>: <a href="https://unsplash.com/photos/6OFxfVuLUEs">desert_cliff<br><img alt="desert_cliff" src="data\images\encounter_backgrounds\unsplash\desert_cliff.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@aanderson0329">Austin Anderson</a>: <a href="https://unsplash.com/photos/YrYeghM0OgE">desert_close_mountain<br><img alt="desert_close_mountain" src="data\images\encounter_backgrounds\unsplash\desert_close_mountain.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@blueswallow">Parastoo Maleki</a>: <a href="https://unsplash.com/photos/CUDoVGSfUPg">desert_distant_mountain<br><img alt="desert_distant_mountain" src="data\images\encounter_backgrounds\unsplash\desert_distant_mountain.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@mostaphaabidour">Mostapha Abidour</a>: <a href="https://unsplash.com/photos/2zgGXQsGXtQ">desert_hill<br><img alt="desert_hill" src="data\images\encounter_backgrounds\unsplash\desert_hill.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@ivalex">Ivan Aleksic</a>: <a href="https://unsplash.com/photos/16YxCJSoAek">gate<br><img alt="gate" src="data\images\encounter_backgrounds\unsplash\gate.png" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@j">Jeremy Cai</a>: <a href="https://unsplash.com/photos/eT1ef3tPglU">hill_distant_mountain<br><img alt="hill_distant_mountain" src="data\images\encounter_backgrounds\unsplash\hill_distant_mountain.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@isaacquesada">Isaac Quesada</a>: <a href="https://unsplash.com/photos/6xxxvB72qB0">jungle<br><img alt="jungle" src="data\images\encounter_backgrounds\unsplash\jungle.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@paramir">Ehud Neuhaus</a>: <a href="https://unsplash.com/photos/iulSk5ChQso">jungle_dark<br><img alt="jungle_dark" src="data\images\encounter_backgrounds\unsplash\jungle_dark.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@conscious_design">Conscious Design</a>: <a href="https://unsplash.com/photos/mLpbHWquEYM">jungle_light<br><img alt="jungle_light" src="data\images\encounter_backgrounds\unsplash\jungle_light.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@ugodly">Hugo Delauney</a>: <a href="https://unsplash.com/photos/ykjsf518lZY">pine_forest<br><img alt="pine_forest" src="data\images\encounter_backgrounds\unsplash\pine_forest.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@dylanleagh">Dylan Leagh</a>: <a href="https://unsplash.com/photos/k5Vj3gx4vHE">pine_forest_dark<br><img alt="pine_forest_dark" src="data\images\encounter_backgrounds\unsplash\pine_forest_dark.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@k1gabyt0">Andrey Kigay</a>: <a href="https://unsplash.com/photos/BWpKTSsiBas">pine_forest_light<br><img alt="pine_forest_light" src="data\images\encounter_backgrounds\unsplash\pine_forest_light.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@klimy4">Stanislav Klimanskii</a>: <a href="https://unsplash.com/photos/8krv1j-huaQ">plain<br><img alt="plain" src="data\images\encounter_backgrounds\unsplash\plain.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@timnieland">Tim Nieland</a>: <a href="https://unsplash.com/photos/gufUJAz_y-A">plain_cliff<br><img alt="plain_cliff" src="data\images\encounter_backgrounds\unsplash\plain_cliff.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@edan">Edan Cohen</a>: <a href="https://unsplash.com/photos/IyjhDTTQitM">plain_close_mountain<br><img alt="plain_close_mountain" src="data\images\encounter_backgrounds\unsplash\plain_close_mountain.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@secretasianman">Viateur Hwang</a>: <a href="https://unsplash.com/photos/-By1_DpPsBk">plain_deciduous_forest<br><img alt="plain_deciduous_forest" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@svl_photo">Kirill Shavlo</a>: <a href="https://unsplash.com/photos/eDguN_ifJjA">plain_deciduous_forest_cliff<br><img alt="plain_deciduous_forest_cliff" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_cliff.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@matmacq">Mathew MacQuarrie</a>: <a href="https://unsplash.com/photos/Lzx4J_Pb3sk">plain_deciduous_forest_close_mountain<br><img alt="plain_deciduous_forest_close_mountain" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_close_mountain.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@a_lo">Angela Loria</a>: <a href="https://unsplash.com/photos/ZAy8srF4rRM">plain_deciduous_forest_distant_mountain<br><img alt="plain_deciduous_forest_distant_mountain" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_distant_mountain.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@achimr">Achim Ruhnau</a>: <a href="https://unsplash.com/photos/tXzU28GOy5k">plain_deciduous_forest_hill<br><img alt="plain_deciduous_forest_hill" src="data\images\encounter_backgrounds\unsplash\plain_deciduous_forest_hill.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@claudelrheault">Claudel Rheault</a>: <a href="https://unsplash.com/photos/ZVbv1akA-l4">plain_distant_mountain<br><img alt="plain_distant_mountain" src="data\images\encounter_backgrounds\unsplash\plain_distant_mountain.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@hayarpi_1">Hayarpi Mkhitaryan</a>: <a href="https://unsplash.com/photos/ppEPKpdPK-0">plain_hill<br><img alt="plain_hill" src="data\images\encounter_backgrounds\unsplash\plain_hill.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@paultrienekens">Paul Trienekens</a>: <a href="https://unsplash.com/photos/9goYHROaqMo">plain_pine_forest<br><img alt="plain_pine_forest" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@rocinante_11">Mick Haupt</a>: <a href="https://unsplash.com/photos/hb09G5FZG5k">plain_pine_forest_cliff<br><img alt="plain_pine_forest_cliff" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_cliff.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@gabe7753">Gabriel Phipps</a>: <a href="https://unsplash.com/photos/9CxIoNz41KY">plain_pine_forest_close_mountain<br><img alt="plain_pine_forest_close_mountain" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_close_mountain.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@cbrin">Christina Brinza</a>: <a href="https://unsplash.com/photos/fA2AbDSwEMo">plain_pine_forest_distant_mountain<br><img alt="plain_pine_forest_distant_mountain" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_distant_mountain.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@hixenia">Kseniia Rastvorova</a>: <a href="https://unsplash.com/photos/YhZt03_OJKs">plain_pine_forest_hill<br><img alt="plain_pine_forest_hill" src="data\images\encounter_backgrounds\unsplash\plain_pine_forest_hill.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@danilal">Daniil Lobachev</a>: <a href="https://unsplash.com/photos/Pi1ER8QiK9o">river<br><img alt="river" src="data\images\encounter_backgrounds\unsplash\river.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@jordanfmcqueen">Jordan McQueen</a>: <a href="https://unsplash.com/photos/SDsosT_RRPk">shore<br><img alt="shore" src="data\images\encounter_backgrounds\unsplash\shore.jfif" width=200></a></td>
   </tr>
   <tr>
      <td><a href="https://unsplash.com/@neo13">Yves Sinoir</a>: <a href="https://unsplash.com/photos/hZpWdqIMMGw">shore_cliff<br><img alt="shore_cliff" src="data\images\encounter_backgrounds\unsplash\shore_cliff.jfif" width=200></a></td>
      <td><a href="https://unsplash.com/@gunnarridder">Gunnar Ridderström</a>: <a href="https://unsplash.com/photos/WHrBWOnfypI">swamp<br><img alt="swamp" src="data\images\encounter_backgrounds\unsplash\swamp.jfif" width=200></a></td>
   </tr>
</table>

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
