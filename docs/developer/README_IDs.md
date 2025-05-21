# MnemonicSlugs: Human-Friendly Identifiers

## Overview

MnemonicSlugs provides a system for generating human-friendly, memorable identifiers that can replace opaque GUIDs in scenarios where readability matters. The system converts numerical IDs into sequences of memorable words, making them easier to read, communicate, and remember.

## Why Use MnemonicSlugs?

Consider these two identifiers:

```
8f9240688685a1e9  (Standard hexadecimal ID)
vs.
magic-slang-crimson  (Mnemonic slug)
```

Which would you rather:
- Read aloud on a call?
- Type manually from paper?
- Include in error messages?
- Remember when a user reports an issue?

MnemonicSlugs excels in these human-interaction scenarios while maintaining uniqueness properties required for identifiers.

## How It Works

The MnemonicSlugs system uses a carefully curated word list of 1,633 words that are:

- Internationally recognizable
- Phonetically distinct
- Easy to spell and pronounce
- Short and memorable

These words can be deterministically generated from numbers (or vice versa), and can be combined into multi-word slugs to represent larger numerical spaces.

## Key Features

### 1. Deterministic Generation

Providing the same seed value will always generate the same slug:

```python
# The same email will always generate the same user ID
user_id = MnemonicSlugs.generate_id_slug(2, "user@example.com")  # e.g., "tiger-castle"
```

### 2. Hierarchical IDs

The system supports hierarchical IDs where each level is unique within its parent context:

```python
# Create a hierarchical ID for user -> session -> message
hierarchical_id = MnemonicSlugs.generate_hierarchical_id([
    ("user_12345", 2),        # User ID with 2 words
    ("session_456", 1),       # Session ID with 1 word
    ("message_789", 1)        # Message ID with 1 word
])
# Result: "tiger-castle:apollo:banana"
```

### 3. Namespace Scoping

Objects only need to be unique within their namespace, similar to how:
- File names only need to be unique within a directory
- Variables only need to be unique within a scope

This allows using shorter IDs while maintaining uniqueness where it matters.

## Capacity and Scale

| Words | Unique Values | Appropriate For |
|-------|---------------|------------------|
| 1     | 1,633         | Small collections, enum values |
| 2     | 2.67 million  | Users, sessions, entities |
| 3     | 4.35 billion  | Global unique identifiers |
| 4     | 7.1 trillion  | Cryptographic purposes |

## Usage Examples

### Basic ID Generation

```python
# Generate a random two-word slug
random_id = MnemonicSlugs.generate_slug(2)  # e.g., "potato-uncle"

# Generate a deterministic slug from a string
user_id = MnemonicSlugs.generate_id_slug(2, "user@example.com")  # Always the same

# Convert a number to a slug
num_slug = MnemonicSlugs.from_number(12345)  # e.g., "bridge-acid"

# Convert a slug back to a number
num = MnemonicSlugs.to_number("bridge-acid")  # 12345
```

### Hierarchical IDs

```python
# Generate a user ID
user_id = MnemonicSlugs.generate_id_slug(2, "user_12345")

# Generate a session ID within that user's context
session_id = MnemonicSlugs.generate_id_slug(1, f"session_{user_id}")

# Generate a message ID within that session's context
message_id = MnemonicSlugs.generate_id_slug(1, f"message_{session_id}")

# Combine into a full hierarchical ID
full_id = f"{user_id}:{session_id}:{message_id}"
# e.g., "tiger-castle:apollo:banana"
```

## Implementation Details

The MnemonicSlugs class provides:

- `generate_slug()` - Create random word slugs
- `generate_id_slug()` - Create deterministic slugs from seeds 
- `generate_hierarchical_id()` - Create multi-level hierarchical IDs
- `from_number()`/`to_number()` - Convert between slugs and numbers
- `parse_hierarchical_id()` - Split hierarchical IDs into components

## Best Practices

1. **Choose appropriate word counts** based on your uniqueness requirements
2. **Use hierarchical IDs** when objects have natural parent-child relationships
3. **Store both the slug and numeric ID** in databases when performance matters
4. **Use consistent delimiters** (`:` for hierarchy levels, `-` between words)
5. **Consider case sensitivity** (all operations are case-insensitive)

## Historical Context

The MnemonicSlugs system is inspired by Oren Tirosh's mnemonic encoding project, which aimed to make cryptographic data more accessible for human use. Similar systems have been used in:

- One-time password schemes
- PGPfone for secure communications
- Bitcoin's BIP-39 seed phrases

MnemonicSlugs adapts these ideas specifically for application identifiers where human interaction is important.

## Conclusion

MnemonicSlugs bridges the gap between computer-friendly unique identifiers and human-friendly memorable names. By replacing opaque GUIDs with readable word combinations in user-facing contexts, we improve communication, troubleshooting, and overall user experience without sacrificing the technical requirements for unique identifiers.