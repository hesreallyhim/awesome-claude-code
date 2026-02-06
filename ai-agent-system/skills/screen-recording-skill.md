# Screen Recording Skill

## Purpose
Capture screen recordings of demos and browser interactions for video content.

## Prerequisites
- FFmpeg: `ffmpeg -version`
- For Linux: X11 or Wayland display
- For macOS: built-in avfoundation
- Optional: Puppeteer CDP for browser-only recording

## Workflows

### Record Full Screen (Linux/X11)
```bash
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 \
  -c:v libx264 -preset ultrafast -crf 18 \
  -t 60 output/videos/screen-recording.mp4
# Stop with Ctrl+C or -t for duration limit
```

### Record Full Screen (macOS)
```bash
ffmpeg -f avfoundation -framerate 30 -i "1:none" \
  -c:v libx264 -preset ultrafast -crf 18 \
  output/videos/screen-recording.mp4
```

### Record with Audio (Linux PulseAudio)
```bash
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :0.0 \
  -f pulse -i default \
  -c:v libx264 -preset ultrafast -crf 18 \
  -c:a aac -b:a 128k \
  output/videos/screen-with-audio.mp4
```

### Browser Demo Recording (Puppeteer CDP)
```bash
node scripts/record-demo.js http://localhost:3000 30 demo.mp4
```
This captures screenshots at 10fps and compiles them into a video.

### Headless Recording with Xvfb
```bash
# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

# Launch app in virtual display
google-chrome --display=:99 http://localhost:3000 &

# Record
ffmpeg -f x11grab -framerate 30 -video_size 1920x1080 -i :99.0 \
  -t 30 -c:v libx264 -preset ultrafast output/videos/headless-demo.mp4
```

## Post-Processing

### Trim
```bash
ffmpeg -i input.mp4 -ss 00:00:05 -t 00:00:25 -c copy output/trimmed.mp4
```

### Speed Up (2x)
```bash
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" output/fast.mp4
```

### Convert to GIF
```bash
ffmpeg -i input.mp4 -vf "fps=10,scale=640:-1:flags=lanczos" -c:v gif output/preview.gif
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No display | Use Xvfb: `Xvfb :99 -screen 0 1920x1080x24 &` |
| Permission denied | `xhost +local:` for X11 access |
| Poor quality | Lower CRF (default 23, lower = better) |
| Frame drops | Use `ultrafast` preset, lower fps/resolution |
