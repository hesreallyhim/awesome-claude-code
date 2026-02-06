---
name: create-video
description: Create a video using Remotion. Supports explainer videos, demo recordings, and short social clips with animations, code displays, and captions.
disable-model-invocation: true
---

# Create Video with Remotion

Generate a professional video using the Remotion React-based framework.

## Arguments
`$ARGUMENTS` = `<type> <title> [subtitle]`
- type: `explainer`, `demo`, or `short`
- title: The video title
- subtitle: Optional subtitle

## Process

### 1. Choose composition type

**Explainer** (`src/compositions/ExplainerVideo.tsx`):
- Animated title card with gradient background
- Content sections with slide-in animations
- Best for: "How X works", "Why X matters"

**Demo** (`src/compositions/DemoVideo.tsx`):
- Screenshot-based walkthrough
- Caption overlays synchronized to screenshots
- Best for: showing a running application

**Short** (`src/compositions/ShortVideo.tsx`):
- 15-30 second vertical video (1080x1920)
- Bold text, fast transitions
- Best for: X/LinkedIn/TikTok clips

### 2. Customize the composition

Edit `src/Root.tsx` to update `defaultProps`:
```tsx
<Composition
  id="ExplainerVideo"
  component={ExplainerVideo}
  durationInFrames={30 * 60}  // Adjust duration
  fps={30}
  width={1920}
  height={1080}
  defaultProps={{
    title: "YOUR TITLE",
    subtitle: "YOUR SUBTITLE",
    sections: [
      { title: "Section 1", content: "Content here", durationInFrames: 150 },
      { title: "Section 2", content: "Content here", durationInFrames: 150 },
    ],
  }}
/>
```

### 3. Preview
```bash
npm run video:preview
```

### 4. Render
```bash
npm run video:render      # Explainer
npm run video:demo        # Demo
npm run video:short       # Short
```

### 5. Post-process (optional)
```bash
# Add voiceover
ffmpeg -i output/videos/explainer.mp4 -i src/assets/audio/voiceover.mp3 \
  -c:v copy -c:a aac -shortest output/videos/final.mp4

# Add background music
ffmpeg -i output/videos/explainer.mp4 -i src/assets/audio/bgmusic.mp3 \
  -filter_complex "[1:a]volume=0.12[bg];[0:a][bg]amix=inputs=2:duration=first" \
  -c:v copy -c:a aac output/videos/final.mp4

# Generate thumbnail
ffmpeg -i output/videos/final.mp4 -ss 2 -vframes 1 output/videos/thumb.png
```
