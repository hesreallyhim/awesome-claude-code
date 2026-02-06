# Coding Project Creation Skill

## Purpose
Create complete coding projects from scratch — from idea to working application.
Supports web apps, CLI tools, APIs, and more.

## Workflows

### Create a Web Application (React + Vite)
```
1. Initialize project:
   npm create vite@latest my-app -- --template react
   cd my-app
   npm install

2. Install common dependencies:
   npm install axios react-router-dom lucide-react

3. Set up project structure:
   src/
   ├── components/     # Reusable UI components
   ├── pages/          # Page-level components
   ├── hooks/          # Custom React hooks
   ├── utils/          # Helper functions
   ├── styles/         # CSS/styling
   └── api/            # API client functions

4. Implement features iteratively:
   - Start with layout/navigation
   - Add core functionality
   - Style and polish
   - Add error handling

5. Test locally:
   npm run dev

6. Build for production:
   npm run build
```

### Create a Node.js API
```
1. Initialize:
   mkdir my-api && cd my-api
   npm init -y
   npm install express cors dotenv

2. Create server:
   // index.js
   const express = require('express');
   const cors = require('cors');
   const app = express();
   app.use(cors());
   app.use(express.json());

   app.get('/api/health', (req, res) => {
     res.json({ status: 'ok' });
   });

   app.listen(3000, () => console.log('Server on port 3000'));

3. Add routes and middleware

4. Test: node index.js
```

### Create a Python CLI Tool
```
1. Initialize:
   mkdir my-tool && cd my-tool
   python -m venv venv
   source venv/bin/activate
   pip install click rich requests

2. Create main script:
   # main.py
   import click

   @click.command()
   @click.argument('name')
   def hello(name):
       click.echo(f'Hello {name}!')

   if __name__ == '__main__':
       hello()

3. Add pyproject.toml for packaging

4. Test: python main.py World
```

### Create a Full-Stack App
```
1. Set up backend (Express/FastAPI)
2. Set up frontend (React/Vue)
3. Connect frontend to backend API
4. Add database if needed (SQLite/PostgreSQL)
5. Test end-to-end
6. Dockerize (optional)
```

## Code Quality Checklist

Before publishing:
- [ ] README.md with clear description and usage instructions
- [ ] .gitignore with appropriate exclusions
- [ ] Environment variables in .env.example (not .env)
- [ ] Error handling for edge cases
- [ ] Input validation for user-facing inputs
- [ ] No hardcoded secrets or API keys
- [ ] Clean, readable code structure
- [ ] Basic tests for core functionality

## Common Project Templates

### package.json (Node.js)
```json
{
  "name": "project-name",
  "version": "1.0.0",
  "description": "Project description",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest"
  },
  "license": "MIT"
}
```

### .gitignore
```
node_modules/
dist/
build/
.env
*.log
.DS_Store
__pycache__/
*.pyc
venv/
```

## Troubleshooting

- **Port in use**: Kill process on port: `lsof -ti:3000 | xargs kill`
- **Module not found**: Run `npm install` or check import paths
- **CORS errors**: Add cors middleware or proxy configuration
- **Build fails**: Check Node.js version, clear caches: `rm -rf node_modules && npm install`
