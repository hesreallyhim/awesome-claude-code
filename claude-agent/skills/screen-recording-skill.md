# Screen Recording Skill

## Purpose
Capture screen recordings of demos, browser interactions, and application usage
for inclusion in explainer videos.

## Prerequisites
- FFmpeg installed: `ffmpeg -version`
- On Linux: `xdotool`, `xwininfo` for window targeting
- On macOS: built-in `screencapture` or FFmpeg with avfoundation

## Workflows

### Record Full Screen (Linux/X11)
```bash
# Record at 30fps, 1920x1080
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 \
  -c:v libx264 -preset ultrafast -crf 18 \
  output/screen-recording.mp4

# Stop with Ctrl+C or after N seconds:
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 \
  -t 60 -c:v libx264 -preset ultrafast -crf 18 \
  output/screen-recording.mp4
```

### Record Specific Window (Linux)
```bash
# Get window ID
WINDOW_ID=$(xdotool getactivewindow)
GEOM=$(xwininfo -id $WINDOW_ID | grep -E "Width|Height|Absolute" | awk '{print $NF}')

# Record that window
ffmpeg -f x11grab -framerate 30 \
  -video_size ${WIDTH}x${HEIGHT} \
  -i :0.0+${X},${Y} \
  -c:v libx264 -preset ultrafast \
  output/window-recording.mp4
```

### Record with Audio (Linux PulseAudio)
```bash
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 \
  -f pulse -i default \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac -b:a 128k \
  output/screen-with-audio.mp4
```

### Record macOS Screen
```bash
# List available devices
ffmpeg -f avfoundation -list_devices true -i ""

# Record screen (device 1 is typically the main display)
ffmpeg -f avfoundation -framerate 30 -i "1:none" \
  -c:v libx264 -preset ultrafast -crf 18 \
  output/screen-recording.mp4

# Record with audio
ffmpeg -f avfoundation -framerate 30 -i "1:0" \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac -b:a 128k \
  output/screen-with-audio.mp4
```

### Automated Demo Recording with Puppeteer
```javascript
const { launchBrowser, navigateTo, sleep } = require('./browser');

async function recordDemo(url, actions, outputFile) {
  const browser = await launchBrowser();
  const page = (await browser.pages())[0];

  // Start recording using CDP
  const client = await page.target().createCDPSession();
  await client.send('Page.startScreencast', {
    format: 'png',
    quality: 100,
    everyNthFrame: 1,
  });

  const frames = [];
  client.on('Page.screencastFrame', async ({ data, sessionId }) => {
    frames.push(Buffer.from(data, 'base64'));
    await client.send('Page.screencastFrameAck', { sessionId });
  });

  // Execute demo actions
  await navigateTo(page, url);
  for (const action of actions) {
    await action(page);
    await sleep(500);
  }

  await client.send('Page.stopScreencast');

  // Save frames as video using FFmpeg
  const { execSync } = require('child_process');
  const fs = require('fs');
  const tmpDir = '/tmp/demo-frames';
  fs.mkdirSync(tmpDir, { recursive: true });

  frames.forEach((frame, i) => {
    fs.writeFileSync(`${tmpDir}/frame-${String(i).padStart(5, '0')}.png`, frame);
  });

  execSync(`ffmpeg -framerate 30 -i ${tmpDir}/frame-%05d.png -c:v libx264 -pix_fmt yuv420p ${outputFile}`);

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true });
  await browser.close();
  console.log(`Demo recorded: ${outputFile}`);
}

module.exports = { recordDemo };
```

## Post-Processing

### Trim Recording
```bash
# Trim from 5s to 30s
ffmpeg -i input.mp4 -ss 00:00:05 -t 00:00:25 -c copy output/trimmed.mp4
```

### Speed Up / Slow Down
```bash
# 2x speed
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" output/fast.mp4

# 0.5x speed (slow motion)
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" -filter:a "atempo=0.5" output/slow.mp4
```

### Add Cursor Highlight (post-processing)
```bash
# Overlay a cursor highlight circle
ffmpeg -i input.mp4 \
  -vf "drawbox=x=CURSOR_X-10:y=CURSOR_Y-10:w=20:h=20:color=yellow@0.5:t=fill" \
  output/highlighted.mp4
```

### Convert to GIF (for previews)
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=640:-1:flags=lanczos" \
  -c:v gif output/preview.gif
```

## Troubleshooting

- **No display (headless)**: Use Xvfb for virtual display: `Xvfb :99 -screen 0 1920x1080x24 &`
- **Permission denied**: Run with display access or use `xhost +local:`
- **Poor quality**: Decrease CRF value (lower = better quality, bigger file)
- **Frame drops**: Use `ultrafast` preset, lower resolution, or reduce framerate
