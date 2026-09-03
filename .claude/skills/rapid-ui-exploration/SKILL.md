---
name: rapid-ui-exploration
description: Rapidly create and compare many lightweight, interactive UI prototypes grounded in the current application. Use when the user requests design directions, visual experiments, interface concepts, alternative layouts, or rapid prototypes rather than production implementation.
---

# Rapid UI Exploration

Create many fast, visually complete prototypes that help the user discover what the application should look and feel like.

The current application supplies the product, information, terminology, data shapes, and important interactions. It is a foundation—not a visual limitation.

## Preserve what matters

Before designing, inspect enough of the repository and current application to understand:

- What the application helps users accomplish
- The important screens, information, metrics, and interactions
- What already works and should remain recognizable
- Existing technical or product constraints that affect the design

Keep the meaning of the application accurate. Do not invent a different product merely to support an attractive interface.

Use representative real data when readily available. Otherwise use clearly identified sample data that faithfully matches the real data’s structure and realistic ranges.

## Take every non-design shortcut

These prototypes are disposable design instruments, not production candidates.

Prefer:

- Self-contained HTML, CSS, JavaScript, and inline SVG
- Static fixtures instead of APIs, databases, authentication, or live refresh
- Simulated navigation and interactions
- Shared sample data across concepts
- Local state instead of persistence
- Simple chart approximations when exact calculations are unnecessary
- Existing assets when convenient and temporary substitutes when they are not
- Minimal dependencies and no build process when plain browser files will work

Do not spend prototype time on:

- Production architecture
- Reusable abstractions
- Backend integration
- Comprehensive error handling
- Deployment infrastructure
- Dependency migrations
- Broad automated testing
- Refactoring the actual application

Never mistake implementation shortcuts for permission to take design shortcuts.

## Explore genuinely different directions

Create several coherent design systems, not several color variations of the same layout.

Vary meaningful design decisions such as:

- Information hierarchy and density
- Navigation model
- Screen composition
- Chart and data-visualization language
- Typography
- Visual rhythm
- Controls and selection behavior
- Use of space, layers, borders, color, and motion
- How overview and detail relate
- How the interface feels during use

Each direction should have a clear design thesis. Commit to that thesis instead of mixing unrelated ideas.

Some directions may be restrained and familiar. Others may be more original or experimental. Do not force novelty where it harms comprehension.

## Make each prototype judgeable

Each concept should include enough of the important experience to answer:

- What does this direction feel like?
- Is the most important information immediately understandable?
- Can the user imagine operating the application this way?
- What does this direction improve?
- What does it sacrifice?

Favor one strong primary screen plus the minimum supporting interaction needed to demonstrate the concept. Do not build every screen unless the distinction depends on a broader flow.

Prototype important interactions when they affect the design. Controls should respond, selections should visibly change state, and navigation should demonstrate its intended behavior.

Design and verify at the application’s primary phone width. Ensure text remains readable and controls remain comfortably tappable.

## Present the exploration

Create a lightweight gallery that makes comparison fast.

The gallery should show every direction with:

- A short, memorable name
- A one-sentence design thesis
- A live phone-sized preview or direct link
- Its strongest advantage
- Its principal tradeoff

Make it possible to open and operate each prototype independently.

Default to approximately six to eight meaningfully different directions when the user does not specify a number. Prefer fewer strong directions over many superficial ones.

Store prototypes outside the production application in a clearly named exploratory location, such as:

`prototypes/ui-exploration/`

Do not modify or replace the production interface unless the user separately approves a direction for implementation.

## Conclude clearly

After presenting the prototypes:

- Identify the strongest directions for this particular product
- Explain the important differences briefly
- Point out promising ideas that could be combined
- Ask the user to choose, reject, or refine directions

Do not declare a winner based only on visual spectacle. Judge each direction against the application’s actual purpose.

Prototype creation is not authorization to implement any direction in production.
