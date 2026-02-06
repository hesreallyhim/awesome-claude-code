---
name: create-video
description: Create a video using Remotion. Generates explainer or demo videos with animations, code displays, and captions.
disable-model-invocation: true
allowed-tools: Bash, Read, Write, Edit
---

# Create Video with Remotion

Generate a video using the Remotion framework.

## Usage

```
/create-video explainer "My Video Title" "A subtitle here"
/create-video demo "Demo Title"
```

## Process

1. Navigate to the Remotion project: `claude-agent/src/`

2. Choose video type:
   - **Explainer**: Animated title + content sections
   - **Demo**: Screenshots with captions

3. Customize the composition in `Root.tsx`:
   - Update defaultProps with your title, sections, etc.

4. Preview the video:
   ```bash
   cd claude-agent/src && npx remotion preview
   ```

5. Render the final video:
   ```bash
   cd claude-agent/src && npx remotion render ExplainerVideo ../output/video.mp4
   ```

6. Post-process with FFmpeg if needed:
   ```bash
   # Add voiceover
   ffmpeg -i output/video.mp4 -i audio/voiceover.mp3 -c:v copy -c:a aac output/final.mp4
   ```

## Arguments

- `$0` - Video type: `explainer` or `demo`
- `$1` - Title text
- `$2` - Subtitle text (optional)
