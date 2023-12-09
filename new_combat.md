# New Combat Design Document

## Before combat

Before combat equip armor and weapons.  Unequipped armor and weapons are not available during a combat encounter.
The following can be equipped:
* One set of armor
* One shield
* Two non-polearm one-handed weapons
* One polearm or other two-handed weapon

FUTURE: Consider adding a dagger and allow combat to devolve to grappling?

## Start of combat

Choose hand configuration of weapon and shield.  Some information about the enemy combatants should be provided to
inform the selection, such as what enemies with what types of arms and armour.  Depending on what is equipped, the
following options may be available:
* Fists (if no weapons equipped)
* Fist and shield (if no weapons equipped and shield equipped)
* One-handed weapon one (if equipped)
* One-handed weapon one and shield (if both equipped)
* One-handed weapon two (if equipped)
* One-handed weapon two and shield (if both equipped)
* Polearm or other two-handed weapon (if equipped)
* One-handed polearm and shield (if both equipped, such as spear and shield)

Remember what was last used to open combat and make that the default selection.  Use two columns where a shield is
equipped, else one column.  First (only) column is for weapon and the second column is weapon with shield.  Don't
present an option if the only options is fists, but do prompt the user to obtain and equip weapons and armor.

TBD: When surprised, should this choice still be available?  If not, what selection is made?  I could see making this
selection for the player in the following order of precedence:
1. One-handed weapon one and shield (if both equipped)
2. One-handed weapon one (if equipped)
3. One-handed weapon two and shield (if both equipped)
4. One-handed weapon two (if equipped)
5. Polearm or other two-handed weapon (if equipped)
6. Fist and shield (if no weapons equipped and shield equipped)
7. Fists (if no weapons equipped)

## On-turn (attack)

Choose one of the following actions:
* Attack
* Spell (what spells?)
* Item (what items?)
* Change hand configuration
* Flee

Don't allow healing, at least non-magic healing, during combat.  Trying to perform first aid on one's self while being
attacked with a sword would be a sure fire way to punch one's ticket.

FUTURE: Consider special attack and spell combos, both of which would be learned?  Add a category of special attacks
for this???

On attack, depending on weapon, there may be additional choices for the type of attack.
* Swing: Swing the weapon in an arch toward an opponent.  The verb used for this varies depending on the damage type
being dealt.  For bludgeon damage, it is a **strike**.  For cutting damage, it is a **cut**.
  * Cut: Swing attack with a sword, axe, or other cutting weapon against a target susceptible to cutting.
  * Strike: Swing attack with any weapon which is not a cutting weapon or against a target not susceptible to cutting.
* Thrust
* Riposte: A counterattack after a successful parry.  Has an increased chance to land (perhaps even close to 100%?)
and deals the best of cut, strike, and thrust damage.

FUTURE: Consider second intention attacks where the attack is a feint (false attack) meant to setup an attack based on
predicting the behavior of the defender.  If the right behavior is predicted, the second attack occurs.  These might be
special, learned attacks.

FUTURE: Consider adding any of the following?
* Slice / Slash / Pull cut: Attack meant to cause a long, not deep, cut.
* Pommel strike (sword); strike with butt end of polearm or axe
* Hook: Halberd, axe, etc

Strength of Attack:
* Swing: A sword or one-handed swing can be delivered from the wrist, elbow, or shoulder, where each progressively 
increases the commitment to the attack.  Similarly, a polearm can be swung from different grips which affect how much of
the weapon's maximum reach is in play, how long the swing takes, and how much kinetic energy it can deliver.  As the
reach increases so does the damage, the effort used in the attack, and the disadvantage suffered should the attack be
unsuccessful.
  * Sword and one-handed swing:
    * Wrist: 50% of nominal damage on success; no stamina cost
    * Elbow: 100% of nominal damage on success; stamina cost of weapon; disadvantage on miss
    * Shoulder: 150% of nominal damage on success; 1.5x stamina cost of weapon; 2x disadvantage on miss; not available
on weapons with long reach in caves/dungeons when walls on two or more adjacent sides
  * Polearm swing:
    * Middle grip / Quarters grip: 50% of nominal damage on success; no stamina cost; range cut in half
    * Three quarters grip: 100% of nominal damage on success; stamina cost of weapon; disadvantage on miss; not
available in caves/dungeons when walls on two or more adjacent sides
    * End grip / Bottom grip / Longsword grip: 150% of nominal damage on success; 2x stamina cost of weapon; 2x
disadvantage on miss; not available in caves/dungeons when walls on two or more adjacent sides
* Thrust
  * Arm thrust / slide thrust for two-handed polearms: 100% of nominal damage; no stamina cost
  * Advancing thrust: 150% of nominal damage; min(evade, weapon) stamina cost; 2x disadvantage on miss
* Fists:
  * Jab: 50% of nominal damage on success; no stamina cost (same as wrist swing)
  * Cross: 100% of nominal damage on success; stamina cost of weapon; disadvantage on miss (same as elbow swing)

Potential polearm grips names: https://grauenwolf.wordpress.com/2015/03/15/proposed-terminology-for-gripping-the-staff-spear-and-similar-weapons/

| Action                                   | Stamina Cost                                 | Speed  | Damage Modifier | Miss Penalty    |
|------------------------------------------|----------------------------------------------|--------|-----------------|-----------------|
| Sword and one-handed swing from wrist    | 0                                            | Fast   | 0.5             | None            |
| Sword and one-handed swing from elbow    | Weapon stamina cost                          | Medium | 1.0             | Disadvantage    |
| Sword and one-handed swing from shoulder | Weapon stamina cost * 2                      | Slow   | 1.5             | 2x Disadvantage |
| Polearm swing from middle grip           | 0                                            | Fast   | 0.5             | None            |
| Polearm swing from three quarters grip   | Weapon stamina cost                          | Medium | 1.0             | Disadvantage    |
| Polearm swing from end grip              | Weapon stamina cost * 2                      | Slow   | 1.5             | 2x Disadvantage |
| Arm/slide thrust                         | 0                                            | Fast   | 0.75            | None            |
| Advancing thrust                         | min(evade stamina cost, weapon stamina cost) | Fast   | 1.25            | 2x Disadvantage |
| Fist jab                                 | 0                                            | Fast   | 0.5             | None            |
| Fist cross                               | 1                                            | Medium | 1.0             | Disadvantage    |

### Measure and Distance

FUTURE: Could add additional wrinkles and complexity to track distance of combatants and make footwork selections for the
attack.

Measure and distance: A figher's measure is their attack range.  You want to be safely outside the measure of your
opponent but need your opponent to be within your measure, or "in measure", to land an attack.
  * Stand ground: No forward movement, must already be in measure.
  * Advancing (retreating) step: Short, quick step pushing off with rear leg and take one step forward.  In reverse,
this is the retreating step.
  * Gathering step: Rear leg forward and then step with the other foot.
  * Passing step: Rear leg passed the front leg.

The movement actions above cover increasing ground and take an increasing amount of time.

References:
  * https://www.youtube.com/watch?v=Hg75zRCtrkc&t=75s
  * https://scholarvictoria.com/2016/02/25/back-to-basics-1-footwork-in-meyer

## Off-turn (defense)

Prepare to...
* Stand ground: No stamina cost
* Evade: No damage if successful.  Cost is one stamina per 10 lbs of weight.
* Block: No cutting/piercing damage and reduced bludgeoning damage if successful, but costs stamina.
  * with shield: Attempt to block the attack with your shield.
  * with weapon: When not holding a shield, hold your weapon with two hands and attempt to block a cut.  Can meet a cut
regardless of the force but does not work against thrusts.  An evade and block combo would add protection for thrusts.
* Parry: No damage and sets up a riposte if successful, but costs stamina cost of weapon.  Availability is weapon
dependent.
* Counter: Threaten an opponent with your weapon during their attack.  May disrupt their attack or even land damage.
Not possible when disadvantaged from the prior attack failing.
* Combos!!!  Evade plus block, parry, or counter

| Action         | Stamina Cost           | Success Rate                                                                  | Damage Reduction                           |
|----------------|------------------------|-------------------------------------------------------------------------------|--------------------------------------------|
| Stand Ground   | 0                      | n/a                                                                           | 0%                                         |
| Block (shield) | Stamina cost of shield | Attack speed and shield block rate dependent                                  | 100% slashing/piercing<br/>75% bludgeoning |
| Block (weapon) | Stamina cost of weapon | Cut: Medium<br/>Thrust: Low                                                   | 100% slashing/piercing<br/>75% bludgeoning |
| Parry          | Stamina cost of weapon | Attack speed dependent<br/>Cut: Fails if attack has sufficient kinetic energy | 100%                                       |
| Evade          | Total weight/10        | Attack speed and type dependent                                               | 100%                                       |

|       | Swing                                                                                                          | Thrust                                                                                          |
|-------|----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| Evade | Harder to evade due to greater attack surface                                                                  | Easier to evade due to lesser attack surface<br>Harder to evade because attack can come quicker |
| Parry | Easier to meet the attack due to to greater attack surface<br>Harder to stop the attack due to increased force | Harder to meet the attack due to lesser attack surface<br>Easier to stop the attack             |
| Block | 2                                                                                                              |                                                                                                 |

Higher probability of success for slower attacks.

* Evade: Get the attacker to miss.
  * Higher probability of success against thrust than swing due to smaller attack surface.
  * Higher probability of success when less encumbered (less total weight, movement restrictions)
  * Stamina cost increases with weight
* Block: Stop the motion of the attack.  Can still absorb reduced bludgeon damage.
  * Higher probability of success against swing than thrust due to larger attach surface
  * Block with shield
    * Effective against thrust and swing
    * Higher probability of success Easier against weapons with less reach due to smaller attack surface
    * Provide opportunity to close on successful block
  * Block with weapon (when not equipping shield)
    * For weapon vs weapon where parrying does not work, such as when a bludgeon is involved 
    * Easier against swing than against thrust due to the greater attack surface.
        * Easier with shield, especially against thrust.
        * Easier with weapons with more mass.
        * Easier against weapons with less mass.
        * Easier for slower attacks.
* Parry: Deflect the motion of the attack
  * Easy for thrusts
  * Easier for slower attacks.
* Counter: Attack at the same time as your opponent.

Resources:
* https://www.youtube.com/watch?v=JSKtaCi8HD8
* https://www.youtube.com/watch?v=IVZ9b7GjQsY

Options:
* Stand ground
* Evade
* Block
* Evade and block
* Parry
* Evade and parry
* Counter
* Evade and counter
* Block and counter
* Evade, block, and counter

Options are presented in two columns, where the first is without evading and the second with evading.  The costs and
effects of the options stack.

## Armor

Armors:
* Rags: No armor
* Clothes: Tailor cloth provides minimal protection against bladed weapons
* Leather armor: Boiled leather molded to protect major swaths of the body
* Gambeson: Padded armor made of quilted layers of cloth and batting
* Chainmail: Armor made of a mesh of linked metal rings and worn over gambeson
* Half Plate: Armor made of interlocking plates covering much of the body but with sizeable gaps of chainmail and worn
over gambeson.
* Full Plate: Armor made of interlocking plates covering most of the body with chainmail protecting joints and worn
over gambeson.
* Magic Armor: Full plate with magical properties

Borrowed weights from https://roll20.net/compendium/dnd5e/Armor#content

| Armor           | Cost | Weight | Bludgeon Resist | Cut Resist | Pierce Resist | Movement Penalty |
|-----------------|------|--------|-----------------|------------|---------------|------------------|
| Rags            | 0    | 1 lb.  | 0%              | 0%         | 0%            | 0%               |
| Clothes         | 20   | 2 lb.  | 0%              | 5%         | 5%            | 0%               |
| Leather Armor   | 70   | 10 lb. | 10%             | 10%        | 10%           | 5%               |
| Gambeson        | 300  | 8 lb.  | 25%             | 25%        | 25%           | 5%               |
| Chainmail       | 1000 | 55 lb. | 25%             | 100%       | 50%           | 10%              |
| Half Plate      | 2000 | 60 lb. | 50%             | 100%       | 75%           | 25%              |
| Full Plate      | 3000 | 65 lb. | 75%             | 100%       | 90%           | 30%              |
| Magic Armor     | 7700 | 50 lb. | 75%             | 100%       | 90%           | 20%              |
| Erdrick's Armor | n/a  | 50 lb. | 80%             | 100%       | 90%           | 10%              |

Special Properties:
* Magic Armor
  * Healing 1 health per 4 steps
  * No damage from terrain
  * 33% magic resist
* Erdrick's Armor
  * Healing 1 health per step
  * No damage from terrain
  * 33% fire resist
  * 33% magic resist

## Shields

Shields:
* Round Shield: Large round wooden shield.
* Kite Shield: Large tear-drop shaped shield tall enough to extend coverage to the legs.
* Heater Shield: Medium sized heater-shaped shield made with layers of wooden and leather reinforced with steel.  Has
a slight curvature to partially deflect blows.
* Buckler: Small and light metal shield with a curved surface to partially deflect blows.
* Pavise Shield: Oblong shield large enough to cover the entire body.  Very heavy, so its usage costs mobility.  This
shield can be planted on the ground, in which case it shifts much of the absorbed bludgeon damage into the ground.
When planted, its weight no longer factors into stamina costs.  Blocking with a planted pavise cannot be combined with
evading or parrying as it lacks the mobility to do either.  TODO: Need to figure out mechanics of planting and
unplanting the pavise.

| Shield        | Cost | Weight                                 | Bludgeon Resist                   | Magic Resist | Block Chance | Stamina Cost (weight/4)        |
|---------------|------|----------------------------------------|-----------------------------------|--------------|--------------|--------------------------------|
| Round Shield  | ?    | 10 lb.                                 | 50%                               | 0%           | 25%          | 2.5                            |
| Kite Shield   | ?    | 14 lb.                                 | 50%                               | 0%           | 40%          | 3.5                            |
| Heater Shield | ?    | 8 lb.                                  | 66%                               | 0%           | 33%          | 2                              |
| Buckler       | ?    | 4 lb.                                  | 66%                               | 0%           | 25%          | 1                              |
| Pavise Shield | ?    | 40 lb. when held<br>0 lb. when planted | 40% when held<br>80% when planted | 0%           | 80%          | 10 when held<br>4 when planted |

Borrowed weights from https://blackcitadelrpg.com/magic-shields-5e/

## Weapons

### Weapon Types

**Sword:** Metal bladed weapon with medium reach.  The weight distribution is near the wielder allowing fast movement
and parrying.

Allows the following attacks:
* Cut: Swing of the sword that deals slashing damage.  The swing can be delivered from the wrist, elbow, or shoulder, 
where each progressively increases the commitment to the attack.  .  Where armor resists the slashing damage, minor
bludgeoning damage is delivered instead.
* Thrust: Deals piercing damage

TODO: What about pommel strikes?

Allow the following defenses:
* Parry: 
* Block:

**Axe:** Metal bladed weapon with medium reach.  The weight distribution is away from the wielder slowing movement and
parrying.  Parry success rate dropped to 50%.

**Bludgeon:** Blunt weapon with short reach.  The weight distribution is away from the wielder.  Can't effectively
parry or be parried.  Swung but not thrust.

**Polearm:** Staff weapon with long range.  May allow for cutting and/or piercing damage.  A polearm used in a
one-handed configuration may only be used to thrust, but in all-two handed configurations both swinging and thrusting
are supported as well as parrying.  The weight distribution is near the center of the weapon, but depending on grip may
not be far from wielders grip.  Parry success rate dropped to 75%.

### Weapon Descriptions

### Weapon Stats
 
| Weapon       | Type | Reach    | Cost | Weight  | Center of Mass | Stamina Cost | Speed | Bludgeon Damage | Cut Damage | Pierce Damage | Pierce Mail? | Parry Modifier |
|--------------|------|----------|------|---------|----------------|--------------|-------|-----------------|------------|---------------|--------------|----------------|
| Fist         | 1H   | S        | n/a  | 0 lb.   | n/a            | 1            | ?     | Very low        | 0          | 0             | n/a          | 0              |
| Club         | 1H   | S (3')   | ?    | 2 lb.   | 0.66           | 1.2          | 1.0   | Low             | 0          | 0             | n/a          | 0.5            |
| Quarterstaff | 1H   | L (6')   | ?    | 4 lb.   | 0.5            | 1.2          | 1.0   | Medium          | 0          | 0             | n/a          | 0.8            |
| Spear        | 1H   | L (6')   | ?    | 4 lb.   | 0.55           | 1.0          | ?     | Low             | Low        | High          | Yes          | 0.8            |
| Handaxe      | 1H   | S (2')   | ?    | 2 lb.   | 0.75           | 1.0          | ?     | Low             | Medium     | 0             | n/a          | 0.5            |
| Mace         | 1H   | S (2')   | ?    | 3.5 lb. | 0.9            | 1.2          | ?     | High            | 0          | 0             | n/a          | 0              |
| Arming Sword | 1H   | M (3')   | ?    | 2.5 lb. | 0.25           | 1.0          | 1.0   | Low             | High       | Medium        | No           | 1.0            |
| Longsword    | 1H   | M (3.5') | ?    | 3 lb.   | 0.25           | 1.0          | 1.0   | Low             | Medium     | High          | Yes          | 1.0            |
| Dane Axe     | 2H   | M (4.5') | ?    | 3 lb.   | 0.75           | 2            | ?     | Medium          | High       | 0             | n/a          | 0.4            |
| Greatsword   | 2H   | L (5.5') | ?    | 5.5 lb. | 0.25           | 1.5          | ?     | Medium          | High       | Low           | No           | 0.8            |
| Halberd      | 2H   | L (7')   | ?    | 5 lb.   | 0.66           | 2            | ?     | Medium          | High       | High          | Yes          | 0.6            |

Bludgeon damage is for strike.  Thrust bludgeon damage is always low.
2H: Damage x1.4


https://sbg-sword-forum.forums.net/thread/3342/calculating-cutting-power-longsword?page=2

Center of applied force:
  2H polearm:  8"  (quarterstaff, spear, battleaxe, halberd) 
  1H: 3"
  2H: 4"

Reach * center of mass * weight


Speed calculation: 
Kinetic energy calculation: 1/2 mass * velocity squared

TODO: Need to add purchase costs.  Need to add attack stamina costs.

Weapons to consider adding:
* Dagger
* Warhammer

Borrowed weights from https://roll20.net/compendium/dnd5e/Weapons#content

## Perks

### Situational Perks

* Battle hardened: After 5+ successful encounters in a row, nearly across the board bonuses
* Rush of adrenaline: Up to once per combat encounter, gain 20% of maximum stamina when at low (<25%) health.  This can
occur at the onset of battle if starting at low health or upon taking damage which put you at low health.

### Earned Perks

* Weapon type masteries:
  * Sword
  * Axe
  * Bludgeon
  * Polearm
* Attack type masteries:
  * Swinging
  * Thrusting
* Form masteries:
  * 1H without shield
  * 1H with shield
  * 2H
* Defense masteries:
  * Evasion (nimble feet)
  * Parry / 
  * Shield mastery


* Invigorated by battle: Gain 10% of maximum stamina at the onset of battle
* Keep your weapon swinging: Attack after a swing attack, parry or counter, and then another swing attack
* Magical Adept: Casting is natural and does not require stamina.  Non-adept casters require intense focus to cast
magic, which has a fixed stamina cost.