# Understanding Game Data: From Concept to YAML

## The Big Picture

Think of creating an interactive story like building a dollhouse:

- You need **rooms** (the spaces)
- You need **furniture and objects** (things to interact with)
- You need **rules** about how things work (doors open, lights turn on)
- You need **connections** between rooms (hallways, stairs)

In the old days, programmers had to write complex code to represent all this. Your system will let story creators describe their world using simple, readable data files.

## From Ideas to Data

### Describing a Room

**Story Creator's Vision**: "I want a cozy library with old books, a fireplace, and a secret passage behind the bookshelf."

**How This Becomes Data**:

```yaml
id: "cozy_library"
name: "Cozy Library"
type: "room"
description: "Warm light from the fireplace dances across leather-bound books. The air smells of old paper and wood smoke."

connections:
  north: "main_hall"
  secret: "hidden_chamber"  # only available under certain conditions

objects:
  - "ancient_book"
  - "fireplace"
  - "secret_lever"

properties:
  lit: true  # room has its own light
  cozy: true # affects how descriptions are generated
```

### Describing Objects

**Story Creator's Vision**: "There's an old book that glows when you touch it, and it contains a map to treasure."

**How This Becomes Data**:

```yaml
id: "ancient_book"
name: "Ancient Tome"
type: "item"
description: "A leather-bound book with strange symbols on the cover."

can_do:
  - "take"
  - "read"
  - "touch"

special_properties:
  magical: true
  glows_when_touched: true
  contains_map: true

responses:
  touch: "The book begins to glow with a soft blue light!"
  read: "The pages show a detailed map of the mansion's hidden passages."
```

## The Magic: From Files to Living World

Here's the brilliant part - your AI Game Master takes these simple descriptions and creates a living, responsive world:

### The "Compilation" Process

Just like old games converted human-readable code into computer instructions, your system converts YAML files into a dynamic game world:

1. **Loading Phase**: Game Master reads all the YAML files
2. **World Building**: Creates connections between rooms and objects
3. **Rule Setup**: Establishes what's possible and what isn't
4. **State Tracking**: Keeps track of what's happening as the game progresses

### Example: What Happens Behind the Scenes

**Player Says**: "I want to touch the glowing book"

**Game Master Thinks**:

1. *Player is in cozy_library*
2. *ancient_book is in this room*
3. *Book has "touch" in its can_do list*
4. *Book has special response for "touch"*
5. *Book's magical property should activate*

**Game Master Responds**: "The book begins to glow with a soft blue light! As you touch it, you feel a warm tingling sensation, and the pages flutter open to reveal a detailed map."

## Key Concepts for Your System

### 1. Everything Has Properties

Instead of complex programming, use simple properties:

```yaml
# A door
properties:
  open: false
  locked: true
  key_needed: "brass_key"

# A lamp  
properties:
  lit: false
  battery_level: 75
  light_radius: 3
```

### 2. Connections Create the World

```yaml
# From the kitchen
connections:
  north: "dining_room"
  up: "attic"
  down: "basement"
  secret: "hidden_pantry"  # only if player knows about it
```

### 3. Conditions Make Things Interesting

```yaml
# A door that only opens under certain conditions
connections:
  east:
    leads_to: "treasure_room"
    requires:
      - player_has: "golden_key"
      - room_property: "ritual_complete"
    blocked_message: "The door remains sealed. You sense it requires something special."
```

### 4. Objects Can Contain Other Objects

```yaml
# A treasure chest
type: "container"
contains:
  - "gold_coins"
  - "magic_ring"
  - "old_letter"
properties:
  open: false
  locked: true
  key_needed: "small_key"
```

## Making It User-Friendly

### For Story Creators

Your World Builder agent should guide them through conversation:

**Agent**: "Let's create your first room! What kind of space do you have in mind?"
**Creator**: "A spooky attic with old furniture covered in sheets"
**Agent**: "Great! I'll help you set that up. Should this attic connect to other rooms?"

### For Players

Your Game Master should understand natural language:

**Player**: "I want to carefully search through the old furniture"
**Game Master**: *checks room objects and properties* "You lift the dusty sheet from an old trunk. Inside, you discover a tarnished silver locket and a bundle of yellowed letters tied with ribbon."

## The Workspace Connection

### File Organization

```
//workspace/stories/haunted_mansion/
├── rooms/
│   ├── attic.yaml
│   ├── library.yaml
│   └── basement.yaml
├── objects/
│   ├── ancient_book.yaml
│   ├── silver_locket.yaml
│   └── brass_key.yaml
└── story_info.yaml
```

### Game State in Metadata

While the YAML files define what's *possible*, the workspace metadata tracks what's *happening*:

```
//workspace/meta/game_sessions/player123/
├── current_location: "cozy_library"
├── inventory: ["brass_key", "ancient_book"]
├── discovered_rooms: ["main_hall", "cozy_library", "attic"]
├── completed_actions: ["touched_book", "found_secret_passage"]
└── story_progress: "found_map_phase"
```

## Your Challenge

Design a system where:

1. **Story creators** can describe their world naturally
2. **The data format** captures their vision clearly
3. **AI agents** can turn that data into engaging experiences
4. **Players** feel like they're in a living, responsive world

The magic happens when simple data files become rich, interactive experiences through the power of AI conversation. Focus on making that transformation feel seamless and natural for everyone involved.