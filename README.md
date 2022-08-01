# pyDragonWarrior

![pyDragonWarrior](/data/images/title.png "pyDragonWarrior Title Image")

A Python based Dragon Warrior clone.  Dragon Warrior was chosen as a game with which I have sentimental attachment but
the intent is that it eventually evolves into a unique fantasy game in the spirit of Dragon Warrior instead of being an
out-and-out clone or reimagining.

[![language](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
![Python application](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/python-app.yml/badge.svg)
![mypy](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/mypy.yml/badge.svg)
![Pylint](https://github.com/justinbeetle/pyDragonWarrior/actions/workflows/pylint.yml/badge.svg)
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

## Credits

### Source Material

#### Dragon Warrior

Any [Dragon Warrior](https://en.wikipedia.org/wiki/Dragon_Quest_(video_game)) inspired project or remake is indebted to
the creators of Dragon Warrior.  The 8-bit chip tunes from Dragon Warrior I especially enjoy, much to the chagrin of my
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

#### Dragon Warrior Online Archives

Thanks to the people who have preserved the information from Dragon Warrior to share it with future generations.

* [Forumlas](https://gamefaqs.gamespot.com/nes/563408-dragon-warrior/faqs/61640): Very informative guide on the
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

* [Pita Madgwick](https://pita.itch.io/): Beautiful 16x16 pixel tilesets.  Looking at them makes me happy!  These assets
are licenced and as such are not stored in the repo.  Distributions of the game will eventually include them.
  * [Village Tileset](https://pita.itch.io/rpg-village-tileset)
  * [Overworld Tileset](https://pita.itch.io/rpg-overworld-tileset)
  * [Dungeon Tileset](https://pita.itch.io/rpg-dungeon-tileset)

#### Character Sprites

* [Mega Tiles](https://megatiles.itch.io/): Adorable 16x20 character sprites.  These assets are licenced and as such are
not stored in the repo.  Distributions of the game will eventually include them.
  * [Tiny Tales Character Sprites - NPC Advanced](https://megatiles.itch.io/tiny-tales-human-npc-advanced-sprite-pack)
  * [Tiny Tales Character Sprites - NPC Knights](https://megatiles.itch.io/tiny-tales-human-npc-advanced-sprite-pack)
  * [Tiny Tales Character Sprites - NPC Nobility](https://megatiles.itch.io/tiny-tales-human-npc-nobility-sprite-pack)

#### Fonts

* [somepx](https://somepx.itch.io/): [Compass Pro](https://somepx.itch.io/humble-fonts-free)

#### Encounter Backgrounds

* [Unsplash](https://unsplash.com/): Encounter background images were sourced from a variety of contributors.
  * [Lopez Robin](item.artist_url): [beach](https://unsplash.com/photos/apax4M-4kFI)
  * [Rowan Heuvel](item.artist_url): [beach_jungle](https://unsplash.com/photos/U6t80TWJ1DM)
  * [Arash Bal](item.artist_url): [deciduous_forest](https://unsplash.com/photos/2Y2sF4lB4-Y)
  * [Imat Bagja Gumilar](item.artist_url): [deciduous_forest_dark](https://unsplash.com/photos/jwTvCQQJXh0)
  * [Raimond Klavins](item.artist_url): [deciduous_forest_light](https://unsplash.com/photos/WKfnhCADseQ)
  * [Keith Hardy](item.artist_url): [desert](https://unsplash.com/photos/PP8Escz15d8)
  * [Dann Zepeda](item.artist_url): [desert_city_ruins](https://unsplash.com/photos/uP8Yvwggvmk)
  * [Paul Chambers](item.artist_url): [desert_cliff](https://unsplash.com/photos/6OFxfVuLUEs)
  * [Austin Anderson](item.artist_url): [desert_close_mountain](https://unsplash.com/photos/YrYeghM0OgE)
  * [Parastoo Maleki](item.artist_url): [desert_distant_mountain](https://unsplash.com/photos/CUDoVGSfUPg)
  * [Mostapha Abidour](item.artist_url): [desert_hill](https://unsplash.com/photos/2zgGXQsGXtQ)
  * [Ivan Aleksic](item.artist_url): [gate](https://unsplash.com/photos/16YxCJSoAek)
  * [Jeremy Cai](item.artist_url): [hill_distant_mountain](https://unsplash.com/photos/eT1ef3tPglU)
  * [Isaac Quesada](item.artist_url): [jungle](https://unsplash.com/photos/6xxxvB72qB0)
  * [Ehud Neuhaus](item.artist_url): [jungle_dark](https://unsplash.com/photos/iulSk5ChQso)
  * [Conscious Design](item.artist_url): [jungle_light](https://unsplash.com/photos/mLpbHWquEYM)
  * [Hugo Delauney](item.artist_url): [pine_forest](https://unsplash.com/photos/ykjsf518lZY)
  * [Dylan Leagh](item.artist_url): [pine_forest_dark](https://unsplash.com/photos/k5Vj3gx4vHE)
  * [Andrey Kigay](item.artist_url): [pine_forest_light](https://unsplash.com/photos/BWpKTSsiBas)
  * [Stanislav Klimanskii](item.artist_url): [plain](https://unsplash.com/photos/8krv1j-huaQ)
  * [Tim Nieland](item.artist_url): [plain_cliff](https://unsplash.com/photos/gufUJAz_y-A)
  * [Edan Cohen](item.artist_url): [plain_close_mountain](https://unsplash.com/photos/IyjhDTTQitM)
  * [Viateur Hwang](item.artist_url): [plain_deciduous_forest](https://unsplash.com/photos/-By1_DpPsBk)
  * [Kirill Shavlo](item.artist_url): [plain_deciduous_forest_cliff](https://unsplash.com/photos/eDguN_ifJjA)
  * [Mathew MacQuarrie](item.artist_url): [plain_deciduous_forest_close_mountain](https://unsplash.com/photos/Lzx4J_Pb3sk)
  * [Angela Loria](item.artist_url): [plain_deciduous_forest_distant_mountain](https://unsplash.com/photos/ZAy8srF4rRM)
  * [Achim Ruhnau](item.artist_url): [plain_deciduous_forest_hill](https://unsplash.com/photos/tXzU28GOy5k)
  * [Claudel Rheault](item.artist_url): [plain_distant_mountain](https://unsplash.com/photos/ZVbv1akA-l4)
  * [Hayarpi Mkhitaryan](item.artist_url): [plain_hill](https://unsplash.com/photos/ppEPKpdPK-0)
  * [Paul Trienekens](item.artist_url): [plain_pine_forest](https://unsplash.com/photos/9goYHROaqMo)
  * [Mick Haupt](item.artist_url): [plain_pine_forest_cliff](https://unsplash.com/photos/hb09G5FZG5k)
  * [Gabriel Phipps](item.artist_url): [plain_pine_forest_close_mountain](https://unsplash.com/photos/9CxIoNz41KY)
  * [Christina Brinza](item.artist_url): [plain_pine_forest_distant_mountain](https://unsplash.com/photos/fA2AbDSwEMo)
  * [Kseniia Rastvorova](item.artist_url): [plain_pine_forest_hill](https://unsplash.com/photos/YhZt03_OJKs)
  * [Daniil Lobachev](item.artist_url): [river](https://unsplash.com/photos/Pi1ER8QiK9o)
  * [Jordan McQueen](item.artist_url): [shore](https://unsplash.com/photos/SDsosT_RRPk)
  * [Yves Sinoir](item.artist_url): [shore_cliff](https://unsplash.com/photos/hZpWdqIMMGw)
  * [Gunnar Ridderström](item.artist_url): [swamp](https://unsplash.com/photos/WHrBWOnfypI)

### Python Libraries

* [pygame](https://github.com/pygame/pygame): Python library for multimedia applications
* [Leif Theden](https://github.com/bitcraft)
  * [pytmx](https://github.com/bitcraft/pytmx): Python library to read and render Tiled maps
  * [pyscroll](https://github.com/bitcraft/pyscroll): Python library to read and render Tiled maps

### Tools

#### Python Development Tools

* [mypy](https://github.com/python/mypy): I wouldn't want to work on a large Python project without type annotations.
And without a tool, mypy, to validate them, the type annotations wouldn't be trustworthy.
* [PyCharm](https://www.jetbrains.com/pycharm/): Python IDE
* [Pylint](https://github.com/PyCQA/pylint): Python static code analysis

#### Image and Map Building Tools

* [GIMP](https://www.gimp.org/): Image editor
* [Thorbjørn Lindeijer](https://github.com/bjorn)
  * [Tiled](https://github.com/mapeditor/tiled): 2D map editor
