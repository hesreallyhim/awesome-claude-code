# LangGraphJS Development Guide

## Build & Test Commands
- Build: `yarn build`
- Lint: `yarn lint` (fix with `yarn lint:fix`)
- Format: `yarn format` (check with `yarn format:check`)
- Test: `yarn test` (single test: `yarn test:single /path/to/yourtest.test.ts`)
- Integration tests: `yarn test:int` (start deps: `yarn test:int:deps`, stop: `yarn test:int:deps:down`)

## Code Style Guidelines
- **TypeScript**: Target ES2021, NodeNext modules, strict typing enabled
- **Formatting**: 2-space indentation, 80 char width, double quotes, semicolons required
- **Naming**: camelCase (variables/functions), CamelCase (classes), UPPER_CASE (constants)
- **Files**: lowercase .ts, tests use .test.ts or .int.test.ts for integration
- **Error Handling**: Custom error classes that extend BaseLangGraphError
- **Imports**: ES modules with file extensions, order: external deps → internal modules → types
- **Project Structure**: Monorepo with yarn workspaces, libs/ for packages, examples/ for demos
- **New Features**: Match patterns of existing code, ensure proper testing, discuss major abstractions in issues

## Library Architecture

### System Layers
- **Channels Layer**: Base communication & state management (BaseChannel, LastValue, Topic)
- **Checkpointer Layer**: Persistence and state serialization across backends
- **Pregel Layer**: Message passing execution engine with superstep-based computation
- **Graph Layer**: High-level APIs for workflow definition (Graph, StateGraph)

### Key Dependencies
- Channels provide state management primitives used by Pregel nodes
- Checkpointer enables persistence, serialization, and time-travel debugging
- Pregel implements the execution engine using channels for communication
- Graph builds on Pregel adding workflow semantics and node/edge definitions
- StateGraph extends Graph with shared state management capabilities