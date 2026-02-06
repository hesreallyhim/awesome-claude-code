# Coding Project Creation Skill

## Purpose
Create complete coding projects from scratch — web apps, CLI tools, APIs, and more.

## Workflows

### React + Vite Web App
```
1. npm create vite@latest my-app -- --template react
2. cd my-app && npm install
3. npm install lucide-react (icons)
4. Structure:
   src/
   ├── components/
   ├── pages/
   ├── hooks/
   ├── utils/
   └── styles/
5. npm run dev → test at localhost:5173
6. npm run build → production build
```

### Node.js Express API
```
1. mkdir my-api && cd my-api
2. npm init -y
3. npm install express cors dotenv
4. Create index.js:
   const express = require('express');
   const cors = require('cors');
   const app = express();
   app.use(cors());
   app.use(express.json());
   app.get('/api/health', (req, res) => res.json({ status: 'ok' }));
   app.listen(3000, () => console.log('Running on :3000'));
5. node index.js → test at localhost:3000
```

### Python CLI Tool
```
1. mkdir my-tool && cd my-tool
2. python -m venv venv && source venv/bin/activate
3. pip install click rich requests
4. Create main.py with @click.command()
5. python main.py → test
```

### Full-Stack App
```
1. Backend: Express or FastAPI
2. Frontend: React or Vue (Vite)
3. Connect via API calls
4. Add database if needed (SQLite)
5. Test end-to-end
```

## Quality Checklist

Before publishing, verify:
- [ ] README.md with description and usage
- [ ] .gitignore (node_modules, .env, dist, __pycache__)
- [ ] .env.example (never commit real .env)
- [ ] No hardcoded secrets or API keys
- [ ] Error handling for edge cases
- [ ] Input validation on user inputs
- [ ] Clean, readable code
- [ ] Works on first run after clone + install

## Templates

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

| Issue | Solution |
|-------|----------|
| Port in use | `lsof -ti:3000 \| xargs kill` |
| Module not found | `npm install` or check import paths |
| CORS errors | Add cors middleware or proxy config |
| Build fails | Clear cache: `rm -rf node_modules && npm install` |
