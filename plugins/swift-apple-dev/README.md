# Swift Apple Dev Plugin

Comprehensive Apple Swift development skills for iOS 26, macOS Tahoe, SwiftUI, SwiftData, Liquid Glass design, Foundation Models, and modern Apple frameworks.

## Prerequisites

- **macOS 15.5+** (Sequoia) for full iOS 26 support
- **Xcode 26+** with Swift 6.x toolchain
- **Swift Command Line Tools** installed (`xcode-select --install`)

## Installation

```bash
# Add the bluewaves-skills marketplace
/plugin marketplace add /path/to/bluewaves-skills

# Install the plugin
/plugin install swift-apple-dev@bluewaves-skills
```

## Skills (15 Total)

### Core Swift
| Skill | Description |
|-------|-------------|
| **swift-fundamentals** | Swift 6.x language features, macros, Package.swift configuration |
| **swift-concurrency** | Async/await, actors, @MainActor, Sendable, strict concurrency |

### SwiftUI
| Skill | Description |
|-------|-------------|
| **liquid-glass-design** | iOS 26 Liquid Glass design system, HIG compliance (~900 lines) |
| **swiftui-patterns** | Modern architecture patterns, @Observable, MV vs MVVM |
| **swiftui-colors-modifiers** | foregroundStyle, hierarchical colors, gradients, ViewModifiers |
| **animations-transitions** | @Animatable macro, withAnimation, PhaseAnimator, KeyframeAnimator |
| **navigation-menus** | NavigationStack, NavigationSplitView, TabView, toolbars, routing |
| **text-rich-content** | AttributedString, native Markdown, rich text editing |

### Data & AI
| Skill | Description |
|-------|-------------|
| **swiftdata-persistence** | @Model, @Query, native iCloud sync (no CloudKit code needed) |
| **foundation-models** | On-device AI with @Generable, tool calling, streaming |

### System Integration
| Skill | Description |
|-------|-------------|
| **app-intents** | Siri, Shortcuts, Spotlight, Action Button integration |
| **widgets-live-activities** | WidgetKit, Live Activities, Dynamic Island, Control Center |
| **spotlight-discovery** | CoreSpotlight, NSUserActivity, content indexing |
| **transferable-sharing** | Drag/drop, copy/paste, ShareLink, Universal Clipboard |

### Testing
| Skill | Description |
|-------|-------------|
| **swift-testing** | Swift Testing framework, @Test, #expect, Xcode Playgrounds |

## Agents (4 Total)

| Agent | Purpose |
|-------|---------|
| **swift-architect** | Architecture design and code review |
| **swift-designer** | UI/UX review and HIG compliance |
| **swift-qa** | Quality assurance and test strategy |
| **swift-performance** | Profiling with Instruments and optimization |

## Usage Examples

### Ask about iOS 26 Liquid Glass
```
How do I implement morphing glass effects between toolbar buttons?
```

### SwiftData with iCloud Sync
```
Create a SwiftData model for a notes app with automatic iCloud sync
```

### Foundation Models
```
Show me how to use @Generable for structured AI output
```

### Invoke Specialized Agents
```
Review my app architecture  (triggers swift-architect)
Check this UI for HIG compliance  (triggers swift-designer)
Help me write tests for this feature  (triggers swift-qa)
Profile my app for memory leaks  (triggers swift-performance)
```

## Validation Hook

The plugin includes a validation hook that checks for Swift/Xcode installation before running Bash commands:

```bash
# Automatically triggered on Bash tool use
# Fails gracefully if Xcode Command Line Tools not installed
```

## Key Features

### Modern Best Practices
- **@Observable** over @ObservableObject
- **foregroundStyle** over deprecated foregroundColor
- **Native iCloud sync** without CloudKit code
- **Swift Testing** framework over XCTest

### iOS 26 Coverage
- Liquid Glass design system
- Glass effect morphing animations
- @Animatable macro
- Search tab role in TabView
- Close button role in toolbars

### Comprehensive Documentation
- 500-900 lines per skill
- Code examples for every concept
- Official Apple documentation links
- Best practices and common pitfalls

## Plugin Structure

```
swift-apple-dev/
├── .claude-plugin/
│   └── plugin.json
├── hooks/
│   ├── hooks.json
│   └── validate-xcode.sh
├── agents/
│   ├── swift-architect/AGENT.md
│   ├── swift-designer/AGENT.md
│   ├── swift-qa/AGENT.md
│   └── swift-performance/AGENT.md
├── skills/
│   ├── swift-fundamentals/SKILL.md
│   ├── swift-concurrency/SKILL.md
│   ├── liquid-glass-design/SKILL.md
│   ├── swiftui-patterns/SKILL.md
│   ├── swiftui-colors-modifiers/SKILL.md
│   ├── animations-transitions/SKILL.md
│   ├── navigation-menus/SKILL.md
│   ├── text-rich-content/SKILL.md
│   ├── swiftdata-persistence/SKILL.md
│   ├── foundation-models/SKILL.md
│   ├── app-intents/SKILL.md
│   ├── widgets-live-activities/SKILL.md
│   ├── spotlight-discovery/SKILL.md
│   ├── transferable-sharing/SKILL.md
│   └── swift-testing/SKILL.md
└── README.md
```

## License

MIT License - See repository root for details.

## Author

Bluewaves Team <contact@bluewaves.boutique>
