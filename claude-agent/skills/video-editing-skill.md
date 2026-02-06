# Video Editing Skill (Remotion)

## Purpose
Create and edit videos programmatically using Remotion (React-based video framework).
Generate explainer videos, demos, tutorials with animations, transitions, and voiceover.

## Prerequisites
- Node.js 18+ installed
- Remotion project initialized (see Setup below)
- FFmpeg installed for encoding: `ffmpeg -version`
- Optional: ElevenLabs API key for TTS voiceover

## Setup

### Initialize Remotion Project
```bash
cd claude-agent/src
npx create-video@latest my-video --template blank
cd my-video
npm install
```

### Project Structure
```
src/
├── Video.tsx          # Main composition definition
├── Root.tsx           # Root component registering compositions
├── components/
│   ├── Title.tsx      # Animated title card
│   ├── CodeBlock.tsx  # Syntax-highlighted code display
│   ├── Transition.tsx # Transition effects
│   └── Caption.tsx    # Subtitle/caption overlay
└── assets/
    ├── audio/         # Voiceover and music files
    └── images/        # Screenshots and graphics
```

## Workflows

### Create an Explainer Video
```
1. Plan the video structure:
   - Title card (2 seconds)
   - Introduction (5 seconds)
   - Demo sections (variable)
   - Conclusion (3 seconds)

2. Create the composition in Root.tsx:
   registerRoot(() => (
     <Composition
       id="ExplainerVideo"
       component={ExplainerVideo}
       durationInFrames={30 * 60}  // 60 seconds at 30fps
       fps={30}
       width={1920}
       height={1080}
     />
   ));

3. Build each section as a React component

4. Preview: npx remotion preview

5. Render: npx remotion render ExplainerVideo output/video.mp4
```

### Add Animated Title
```jsx
import { useCurrentFrame, interpolate, spring } from 'remotion';

export const Title = ({ text }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: 'clamp',
  });
  const scale = spring({ frame, fps: 30, config: { damping: 10 } });

  return (
    <div style={{
      opacity,
      transform: `scale(${scale})`,
      fontSize: 72,
      fontWeight: 'bold',
      color: 'white',
      textAlign: 'center',
    }}>
      {text}
    </div>
  );
};
```

### Add Code Block Display
```jsx
import { useCurrentFrame, interpolate } from 'remotion';

export const CodeBlock = ({ code, language }) => {
  const frame = useCurrentFrame();
  const chars = Math.floor(interpolate(frame, [0, 90], [0, code.length], {
    extrapolateRight: 'clamp',
  }));

  return (
    <div style={{
      backgroundColor: '#1e1e1e',
      borderRadius: 12,
      padding: 40,
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: 24,
      color: '#d4d4d4',
      whiteSpace: 'pre-wrap',
    }}>
      {code.slice(0, chars)}
      <span style={{ opacity: frame % 30 > 15 ? 1 : 0 }}>|</span>
    </div>
  );
};
```

### Add Captions/Subtitles
```jsx
import { useCurrentFrame, Sequence } from 'remotion';

export const Captions = ({ segments }) => {
  // segments: [{ start: 0, end: 90, text: "Hello world" }, ...]
  return (
    <>
      {segments.map((seg, i) => (
        <Sequence key={i} from={seg.start} durationInFrames={seg.end - seg.start}>
          <div style={{
            position: 'absolute',
            bottom: 80,
            width: '100%',
            textAlign: 'center',
          }}>
            <span style={{
              backgroundColor: 'rgba(0,0,0,0.75)',
              color: 'white',
              padding: '8px 24px',
              borderRadius: 8,
              fontSize: 32,
            }}>
              {seg.text}
            </span>
          </div>
        </Sequence>
      ))}
    </>
  );
};
```

### Generate Voiceover with TTS
```bash
# Using ElevenLabs API
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your script here", "model_id": "eleven_monolingual_v1"}' \
  --output claude-agent/src/assets/audio/voiceover.mp3
```

### Render Final Video
```bash
# Preview first
npx remotion preview

# Render to MP4
npx remotion render ExplainerVideo output/video.mp4 --codec h264

# Render with higher quality
npx remotion render ExplainerVideo output/video.mp4 \
  --codec h264 \
  --crf 18 \
  --pixel-format yuv420p
```

## Post-Processing with FFmpeg

### Add Audio Track
```bash
ffmpeg -i output/video.mp4 -i assets/audio/voiceover.mp3 \
  -c:v copy -c:a aac -shortest output/final.mp4
```

### Add Background Music
```bash
ffmpeg -i output/video.mp4 \
  -i assets/audio/voiceover.mp3 \
  -i assets/audio/bgmusic.mp3 \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.15[music];[voice][music]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac output/final.mp4
```

### Generate Thumbnail
```bash
ffmpeg -i output/final.mp4 -ss 00:00:02 -vframes 1 output/thumbnail.png
```

## Troubleshooting

- **Render fails**: Check Node.js version (18+), run `npx remotion doctor`
- **Font missing**: Install fonts or use web-safe alternatives
- **Audio sync**: Match audio duration to video durationInFrames
- **Large file**: Increase CRF value (lower quality) or reduce resolution
