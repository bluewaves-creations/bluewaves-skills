#!/bin/bash
# Validate Xcode command line tools are installed
if ! command -v swift &> /dev/null; then
    echo "ERROR: Swift is not installed. Please install Xcode or Xcode Command Line Tools."
    echo "Run: xcode-select --install"
    exit 1
fi
exit 0
