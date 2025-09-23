#!/bin/bash

echo "Cleaning Next.js cache..."
rm -rf .next
rm -rf node_modules/.cache

echo "Cleaning complete!"