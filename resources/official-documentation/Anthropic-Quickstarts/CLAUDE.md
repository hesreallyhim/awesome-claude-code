# Anthropic Quickstarts Development Guide

## Computer-Use Demo

### Setup & Development

- **Setup environment**: `./setup.sh`
- **Build Docker**: `docker build . -t computer-use-demo:local`
- **Run container**: `docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -v $(pwd)/computer_use_demo:/home/computeruse/computer_use_demo/ -v $HOME/.anthropic:/home/computeruse/.anthropic -p 5900:5900 -p 8501:8501 -p 6080:6080 -p 8080:8080 -it computer-use-demo:local`

### Testing & Code Quality

- **Lint**: `ruff check .`
- **Format**: `ruff format .`
- **Typecheck**: `pyright`
- **Run tests**: `pytest`
- **Run single test**: `pytest tests/path_to_test.py::test_name -v`

### Code Style

- **Python**: snake_case for functions/variables, PascalCase for classes
- **Imports**: Use isort with combine-as-imports
- **Error handling**: Use custom ToolError for tool errors
- **Types**: Add type annotations for all parameters and returns
- **Classes**: Use dataclasses and abstract base classes

## Customer Support Agent

### Setup & Development

- **Install dependencies**: `npm install`
- **Run dev server**: `npm run dev` (full UI)
- **UI variants**: `npm run dev:left` (left sidebar), `npm run dev:right` (right sidebar), `npm run dev:chat` (chat only)
- **Lint**: `npm run lint`
- **Build**: `npm run build` (full UI), see package.json for variants

### Code Style

- **TypeScript**: Strict mode with proper interfaces
- **Components**: Function components with React hooks
- **Formatting**: Follow ESLint Next.js configuration
- **UI components**: Use shadcn/ui components library

## Financial Data Analyst

### Setup & Development

- **Install dependencies**: `npm install`
- **Run dev server**: `npm run dev`
- **Lint**: `npm run lint`
- **Build**: `npm run build`

### Code Style

- **TypeScript**: Strict mode with proper type definitions
- **Components**: Function components with type annotations
- **Visualization**: Use Recharts library for data visualization
- **State management**: React hooks for state
