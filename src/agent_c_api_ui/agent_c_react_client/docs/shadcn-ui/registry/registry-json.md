# Registry.json Schema

Created: 2025-04-24
Source: registry-json.mdx

## Overview

The `registry.json` schema is used to define your custom component registry, listing all available registry items.

## Example

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry.json",
  "name": "shadcn",
  "homepage": "https://ui.shadcn.com",
  "items": [
    {
      "name": "hello-world",
      "type": "registry:block",
      "title": "Hello World",
      "description": "A simple hello world component.",
      "files": [
        {
          "path": "registry/new-york/hello-world/hello-world.tsx",
          "type": "registry:component"
        }
      ]
    }
  ]
}
```

## Schema Properties

### $schema

The `$schema` property is used to specify the schema for the `registry.json` file.

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry.json"
}
```

### name

The `name` property is used to specify the name of your registry. This is used for data attributes and other metadata.

```json
{
  "name": "acme"
}
```

### homepage

The homepage of your registry. This is used for data attributes and other metadata.

```json
{
  "homepage": "https://acme.com"
}
```

### items

The `items` in your registry. Each item must implement the [registry-item schema specification](https://ui.shadcn.com/schema/registry-item.json).

```json
{
  "items": [
    {
      "name": "hello-world",
      "type": "registry:block",
      "title": "Hello World",
      "description": "A simple hello world component.",
      "files": [
        {
          "path": "registry/new-york/hello-world/hello-world.tsx",
          "type": "registry:component"
        }
      ]
    }
  ]
}
```

See the [registry-item schema documentation](/docs/registry/registry-item-json) for more information about individual registry item structure.

## Registry File Organization

The registry.json file typically resides at the root of your registry project, with registry items organized in subdirectories by style and component type.

## Schema Validation

The official schema is available at https://ui.shadcn.com/schema/registry.json for validation purposes.