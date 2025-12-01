# [Kishore Kumar](https://akcube.github.io)

[![Deploy Hugo site to Pages](https://github.com/akcube/akcube.github.io/actions/workflows/hugo.yml/badge.svg)](https://github.com/akcube/akcube.github.io/actions/workflows/hugo.yml)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Fakcube.github.io&label=akcube.github.io)](https://akcube.github.io)
[![Hugo](https://img.shields.io/badge/Hugo-v0.124.1+-blue?logo=hugo)](https://gohugo.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/akcube/akcube.github.io)](https://github.com/akcube/akcube.github.io/commits/main)
[![Repo Size](https://img.shields.io/github/repo-size/akcube/akcube.github.io)](https://github.com/akcube/akcube.github.io)

Personal blog and portfolio site built with Hugo, featuring optimized images and a custom Obsidian-compatible theme.

## Prerequisites

- **Hugo Extended** v0.124.1+ (required for SCSS processing)
- **Go** 1.19+ (required for `hugo-obsidian` tool)
- **Python** 3.8+
- **Node.js** 18+ and npm
- **Git**

## First-Time Setup

### 1. Clone the repository with submodules

```bash
git clone --recurse-submodules https://github.com/akcube/akcube.github.io.git
cd akcube.github.io
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

### 2. Install theme dependencies

```bash
cd themes/obsidian-hugo-texify3
npm install
cd ../..
```

### 3. Set up Python environment for publisher

```bash
cd publisher
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

### 4. Install hugo-obsidian for link graph generation

```bash
go install github.com/jackyzha0/hugo-obsidian@latest
```

Verify installation:

```bash
hugo-obsidian --help
```

## Running the Site Locally

### Start the Hugo development server

```bash
hugo server -D
```

This will:
- Build the site with draft posts included (`-D` flag)
- Start a local server at `http://localhost:1313`
- Watch for file changes and auto-reload
- Enable live browser reload

**Additional useful flags:**
- `--bind 0.0.0.0` - Allow external connections (useful for testing on mobile)
- `--port 1313` - Specify custom port
- `--navigateToChanged` - Navigate to changed content on live reload

### Build for production

```bash
hugo --minify
```

Output will be in the `public/` directory.

## Publishing a New Blog Post

### Workflow Overview

To publish a blog post from your Obsidian vault:

1. Run the publisher script to convert Obsidian markdown to Hugo format
2. Run `hugo-obsidian` to generate link indices for the graph visualization
3. Review changes locally with `hugo server -D`
4. Commit and push to deploy

**Quick workflow:**

```bash
# 1. Activate Python environment and publish from Obsidian
cd publisher
source venv/bin/activate
python publisher.py \
  --source ~/Kishore-Brain/Zettelkasten/my-post.md \
  --dest ../content/blog \
  --idest ../static/images \
  --imgdirs ~/Kishore-Brain/Files
cd ..

# 2. Generate link indices for graph
hugo-obsidian -input=content -output=assets/indices -index -root=.

# 3. Test locally
hugo server -D
```

## Project Structure

```
.
├── content/           # Hugo content
│   ├── blog/         # Blog posts
│   └── ...
├── static/           # Static assets
│   ├── images/       # Optimized blog images (WebP + PNG)
│   ├── css/          # Custom CSS
│   └── js/           # Custom JavaScript
├── layouts/          # Hugo layout overrides
│   └── _default/
│       └── _markup/  # Custom markdown rendering (e.g., images)
├── themes/           # Hugo themes
│   └── obsidian-hugo-texify3/  # Custom theme (git submodule)
├── publisher/        # Publishing tools
│   ├── publisher.py              # Main conversion script
│   ├── optimize_existing_images.py  # Batch optimization script
│   └── requirements.txt
├── hugo.toml         # Hugo configuration
└── package-lock.json # NPM dependencies (theme)
```

## Image Optimization

All images are automatically optimized during publishing:
- **Display size**: Max 650px width (preserves natural size for smaller images)
- **Format**: WebP with PNG fallback for browser compatibility
- **Compression**: 85% WebP quality, optimized PNG
- **Zoom**: Click any image to view full-size with smooth animation

### Optimizing Existing Images

To batch optimize all images already in `static/images/`:

```bash
cd publisher
source venv/bin/activate
python optimize_existing_images.py
```

## License

Content is © Kishore Kumar. Theme based on [Obsidian TeXify3](https://github.com/akcube/obsidian-hugo-texify3).
