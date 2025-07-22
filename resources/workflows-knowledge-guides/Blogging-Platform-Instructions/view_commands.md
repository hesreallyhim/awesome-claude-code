Here are all the available project commands, organized by category:

## Post Management

- `/project:posts:new` - Create a new blog post with proper front matter
- `/project:posts:check_language` - Check posts for UK English spelling and grammar
- `/project:posts:check_links` - Verify all links in posts are valid
- `/project:posts:publish` - Publish a draft post and push changes to GitHub
- `/project:posts:find_drafts` - List all draft posts with their details
- `/project:posts:check_images` - Verify all image references exist in the filesystem
- `/project:posts:recent` - Show the most recent blog posts

## Project Management

- `/project:projects:new` - Create a new project with proper structure and frontmatter
- `/project:projects:check_thumbnails` - Verify all project thumbnails exist and have correct dimensions

## Site Management

- `/project:site:preview` - Generate and serve the site locally
- `/project:site:check_updates` - Check for updates to Hugo and the Congo theme
- `/project:site:deploy` - Deploy the site to GitHub Pages
- `/project:site:find_orphaned_images` - Find unused images in static folder

To get more details about a specific command, look at the corresponding Markdown file in the `.claude/commands/` directory.