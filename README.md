# CAP

**Codebase Awareness Protocol**

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python: ≥3.10](https://img.shields.io/badge/python-≥3.10-3776ab.svg)](https://python.org)

> Give AI coding agents the context they need - architecture, dependencies, and API - so they stop guessing and start respecting your codebase.

---

## Philosophy

AI coding agents are powerful, but they are blind. They see files, not architecture. They read imports, not intent. Without explicit context, they silently violate boundaries, import forbidden packages, and ignore the structure you spent months building.

**CAP fixes this.** You describe your codebase once in three small YAML files. CAP serves that knowledge to any AI agent through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), the open standard for connecting AI to tools.

The result: agents that understand your layers, respect your dependency rules, and use your public API - without you repeating yourself in every prompt.

### Three principles

1. **Declarative over discovery** - You know your codebase better than static analysis. Write it down once, in plain YAML.
2. **Protocol over prompts** - Structured MCP tool responses beat pasted context every time.
3. **Zero lock-in** - YAML files live in your repo. No SaaS, no accounts, no telemetry.

---

## Getting Started

### VS Code Extension (recommended)

The fastest path. The extension handles Python, installs CAP, runs the MCP server, and connects it to your AI agent - all automatically.

**1. Install the extension**

Search for **"CAP - Codebase Awareness Protocol"** in the VS Code Extensions Marketplace, or install from the command line:

```
code --install-extension domasles.cap-vscode
```

**2. Initialize your workspace**

Open the Command Palette (`Ctrl+Shift+P`) and run:

```
CAP: Initialize Configuration
```

This creates a `.cap/` directory with three template files:

```
.cap/
├── api.yaml            # What your code exports
├── architecture.yaml   # How your code is organized
└── dependencies.yaml   # What your code depends on
```

Edit them to match your project. That's all the setup you need.

**3. Enable the MCP server**

When `.cap/` is created, the extension shows a notification prompting you to enable the MCP server. Click **Open Chat** to go to the Copilot panel, then enable the **CAP** server in the MCP tools list.

Once enabled, every AI agent conversation has access to three tools:

| Tool | What the agent gets |
|---|---|
| `get_architecture` | Layers, modules, ownership, architectural rules |
| `get_dependencies` | Runtime/dev packages, versions, forbidden patterns |
| `get_api` | Public/internal exports, stability, access rules |

The agent calls these tools when it needs context. You don't need to prompt for it.

### CLI

If you prefer working from the terminal or want CAP without VS Code:

```bash
pip install cap-cli
```

**Initialize:**

```bash
cap init              # Create .cap/ with templates
cap init --minimal    # Bare minimum scaffolding
cap init --force      # Overwrite existing files
```

**Validate your configuration:**

```bash
cap validate          # Pretty terminal output
cap validate --json   # Machine-readable for CI
```

**Start the MCP server:**

```bash
cap serve
```

This runs a [stdio MCP server](https://modelcontextprotocol.io/docs/concepts/transports#standard-io-stdio) that any MCP-compatible client can connect to. Point your AI tool at the `cap serve` command and it will discover the three tools automatically.

---

## The `.cap/` Files

### `architecture.yaml`

Defines the structural skeleton of your codebase.

```yaml
architecture:
  style: "hexagonal"

layers:
  domain:
    owns: "src/domain/**"
    may_import: []

  application:
    owns: "src/application/**"
    may_import:
      - "domain"

  infrastructure:
    owns: "src/infrastructure/**"
    may_import:
      - "domain"

modules:
  core:
    owns: "src/core/**"
    purpose: "Core business logic and domain models"

rules:
  forbid:
    - path: "src/domain/**"
      calls: "requests.get"
      reason: "Domain must not make HTTP calls"
```

### `dependencies.yaml`

Lists every dependency with its purpose and defines what layers cannot use.

```yaml
dependencies:
  python:
    runtime:
      pydantic:
        version: ">=2.0"
        reason: "Data validation using type annotations"
    dev:
      pytest:
        version: ">=7.0"
        reason: "Testing framework"

rules:
  forbid:
    - layer: "domain"
      dependency: "requests"
      reason: "Domain should not make HTTP calls directly"

notes:
  - "Prefer standard library when possible"
```

### `api.yaml`

Maps what your code exports and who should use it.

```yaml
api:
  public:
    core:
      location: "src/api.py"
      exports:
        - "initialize"
        - "process_data"
      stability: "stable"

  internal:
    utilities:
      location: "src/utils/**"
      exports:
        - "helper_function"
      stability: "experimental"
      warning: "Internal only - use the public API instead"

rules:
  forbid:
    - path: "src/plugins/**"
      api: "internal.utilities"
      reason: "Plugins must use the public API"
```

All fields are validated with strict schemas. Unknown keys are rejected. Run `cap validate` to catch mistakes before your agent does.

---

## Architecture

CAP itself follows hexagonal architecture. The monorepo contains three packages with a strict one-way dependency flow:

```
Dependency flow: cli -> mcp -> core. Never the reverse.
```

```
cap/
├── core/                   # cap-core - parsing, validation, formatting
│   └── cap_core/
│       ├── domain/         # Pydantic models - pure data, no I/O
│       │   └── models/
│       ├── infrastructure/ # FileReader - the only class that touches disk
│       └── application/    # ConfigService, ValidationService, MCPFormatter
│           └── services/
├── mcp/                    # cap-mcp - FastMCP server with stdio transport
│   └── cap_mcp/
│       ├── server.py       # Composition root - wires ConfigService into tools
│       └── tools/          # One file per MCP tool
├── shells/
│   ├── cli/                # cap-cli - click-based CLI
│   │   └── cap_cli/
│   │       ├── commands/   # init, serve, validate
│   │       ├── templates/  # Default .cap/ YAML files
│   │       └── utils/      # Workspace detection, output helpers
│   └── vscode/             # VS Code extension - TypeScript
│       └── src/
│           ├── setup/      # Python discovery, venv management, updates
│           ├── cap/        # CLI runner, init commands, validation
│           ├── mcp/        # MCP server provider, enable notice
│           └── utils/      # Shared workspace/venv/watcher helpers
└── .cap/                   # CAP's own configuration (we eat our own dogfood)
```

### Key design decisions

- **Domain models are pure data.** Pydantic `BaseModel` subclasses with `extra="forbid"` - no I/O, no side effects, strict validation.
- **`ConfigService` is the main facade.** All config loading goes through it. Shells never touch `FileReader` directly.
- **One MCP tool per file.** Each tool module exposes a `register(mcp, config_service)` function.
- **The VS Code extension calls `cap` as a subprocess.** It never imports Python - it installs `cap-cli` into an isolated venv and runs commands through it.

---

## Development

### Prerequisites

- Python ≥ 3.10
- Node.js ≥ 18 (for the VS Code extension)
- Git

### Setup

Clone and install all packages in editable mode:

```bash
git clone https://github.com/domasles/cap.git
cd cap

pip install -e core/
pip install -e mcp/
pip install -e shells/cli/
```

Verify everything works:

```bash
cap --version
cap validate
```

### VS Code Extension Development

```bash
cd shells/vscode
npm install
npm run build
```

Press `F5` in VS Code to launch the Extension Development Host. In dev mode, the extension skips venv setup and expects `cap` to be installed on your PATH (from the editable installs above).

### Project structure cheat sheet

| Package | Language | Entry point | Install |
|---|---|---|---|
| cap-core | Python | `cap_core.ConfigService` | `pip install -e core/` |
| cap-mcp | Python | `cap_mcp.create_server()` | `pip install -e mcp/` |
| cap-cli | Python | `cap` CLI command | `pip install -e shells/cli/` |
| cap-vscode | TypeScript | `src/extension.ts` | `npm install` in `shells/vscode/` |

### Running tests

```bash
cap validate --json    # Validate .cap/ files
```

### Adding a new shell

CAP is designed to be extended with new shells (IDE plugins, web UIs, etc.). A shell:

1. Calls `cap` CLI commands as a subprocess - it does not import core or mcp directly
2. Never adds logic to core - it only wires CLI output into its own UI
3. Lives in `shells/<name>/`
4. Gets its own build system and entry point

---

## Contributing

Contributions are welcome. Before you start:

1. **Open an issue first** for non-trivial changes so we can discuss the approach.
2. **Run `cap validate`** to make sure your `.cap/` files are correct.
3. **Respect the architecture.** The layer rules in `architecture.yaml` aren't suggestions - they're the contract.
4. **Keep the dependency flow.** `cli -> mcp -> core`. If you find yourself importing from a shell into core, stop and rethink.

### Style

- Python: [Black](https://github.com/psf/black) formatter, type hints everywhere
- TypeScript: Strict mode, no `any`
- YAML: 2-space indent, comments for anything non-obvious

---

## License

[Apache License 2.0](LICENSE)
