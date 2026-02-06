# Video Editing Skill (Remotion)

## Purpose
Create and render videos programmatically using Remotion (React-based video framework).

## Prerequisites
- Node.js 18+
- Remotion project at `src/` (run `cd src && npm install`)
- FFmpeg for encoding and post-processing

## Project Structure
```
src/
├── index.ts                   # Entry point
├── Root.tsx                   # Composition registry
├── compositions/
│   ├── ExplainerVideo.tsx     # Animated title + sections
│   ├── DemoVideo.tsx          # Screenshot walkthrough
│   └── ShortVideo.tsx         # Vertical social clip
├── components/
│   ├── Title.tsx              # Animated title card
│   ├── SectionCard.tsx        # Content section
│   ├── CodeBlock.tsx          # Typing code animation
│   ├── Caption.tsx            # Subtitle overlay
│   └── Transition.tsx         # Slide transitions
└── assets/
    ├── audio/                 # Voiceover, music
    ├── images/                # Screenshots, graphics
    └── fonts/                 # Custom fonts
```

## Workflows

### Create an Explainer Video
```
1. Edit src/Root.tsx defaultProps:
   - Set title, subtitle
   - Define sections array: { title, content, durationInFrames }
   - Choose accentColor
2. Preview: npm run video:preview
3. Render: npm run video:render
4. Output: output/videos/explainer.mp4
```

### Create a Demo Video
```
1. Place screenshots in src/assets/images/
2. Edit DemoVideo defaultProps:
   - Set screenshotPaths array
   - Define captions: { start, end, text }
3. Render: npm run video:demo
```

### Create a Short Video (vertical)
```
1. Edit ShortVideo defaultProps:
   - Define lines array (one statement per screen)
   - Set accentColor
2. Render: npm run video:short
3. Output: 1080x1920 vertical video
```

## Code Snippets

### Custom Section Component
```tsx
import { useCurrentFrame, spring, useVideoConfig } from 'remotion';

const MySection = ({ text }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame, fps, config: { damping: 12 } });
  return (
    <div style={{ transform: `scale(${scale})`, fontSize: 48, color: '#fff' }}>
      {text}
    </div>
  );
};
```

## Post-Processing (FFmpeg)

### Add Voiceover
```bash
ffmpeg -i output/videos/explainer.mp4 -i src/assets/audio/voiceover.mp3 \
  -c:v copy -c:a aac -shortest output/videos/final.mp4
```

### Add Background Music
```bash
ffmpeg -i output/videos/explainer.mp4 -i src/assets/audio/bgmusic.mp3 \
  -filter_complex "[1:a]volume=0.12[bg];[0:a][bg]amix=inputs=2:duration=first" \
  -c:v copy -c:a aac output/videos/final.mp4
```

### Generate Thumbnail
```bash
ffmpeg -i output/videos/final.mp4 -ss 2 -vframes 1 output/videos/thumbnail.png
```

### Compress for Social Media
```bash
ffmpeg -i output/videos/final.mp4 -c:v libx264 -crf 28 -preset fast \
  -c:a aac -b:a 128k output/videos/compressed.mp4
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Render fails | `npx remotion doctor`, check Node 18+ |
| Font missing | Use web-safe fonts or install custom ones |
| Audio sync | Match audio duration to durationInFrames |
| Large file | Increase CRF (lower quality) or reduce resolution |
| Slow render | Use `--concurrency` flag for parallel rendering |
