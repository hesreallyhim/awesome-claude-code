#!/usr/bin/env node
/**
 * Record a browser demo session for video creation.
 * Takes screenshots at intervals and compiles them into a video.
 *
 * Usage: node record-demo.js <url> [duration_seconds] [output_file]
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function recordDemo(url, durationSecs = 30, outputFile = 'demo.mp4') {
  let puppeteer;
  try {
    puppeteer = require('puppeteer-core');
  } catch {
    console.error('[Error] puppeteer-core not installed. Run: npm install puppeteer-core');
    process.exit(1);
  }

  const outputDir = path.join(__dirname, '..', 'output');
  const framesDir = path.join(outputDir, 'demo-frames');

  // Setup
  fs.mkdirSync(framesDir, { recursive: true });

  console.log(`[Demo Recorder] Starting recording of ${url}`);
  console.log(`[Demo Recorder] Duration: ${durationSecs}s`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    defaultViewport: { width: 1920, height: 1080 },
  });

  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

  const fps = 10; // Screenshots per second (10 is enough for demos)
  const totalFrames = durationSecs * fps;
  const interval = 1000 / fps;

  console.log(`[Demo Recorder] Capturing ${totalFrames} frames at ${fps}fps...`);

  for (let i = 0; i < totalFrames; i++) {
    const frameFile = path.join(framesDir, `frame-${String(i).padStart(5, '0')}.png`);
    await page.screenshot({ path: frameFile });

    if (i > 0 && i % (fps * 5) === 0) {
      console.log(`[Demo Recorder] Progress: ${Math.round((i / totalFrames) * 100)}%`);
    }

    await new Promise((r) => setTimeout(r, interval));
  }

  await browser.close();
  console.log('[Demo Recorder] Screenshots captured');

  // Compile frames into video using FFmpeg
  const outputPath = path.join(outputDir, outputFile);
  try {
    execSync(
      `ffmpeg -y -framerate ${fps} -i "${framesDir}/frame-%05d.png" ` +
        `-c:v libx264 -pix_fmt yuv420p -crf 23 "${outputPath}"`,
      { stdio: 'pipe' }
    );
    console.log(`[Demo Recorder] Video saved: ${outputPath}`);
  } catch (err) {
    console.error('[Demo Recorder] FFmpeg failed. Frames saved in:', framesDir);
    console.error('[Demo Recorder] Install FFmpeg and run manually:');
    console.error(
      `  ffmpeg -framerate ${fps} -i "${framesDir}/frame-%05d.png" -c:v libx264 -pix_fmt yuv420p "${outputPath}"`
    );
  }

  // Cleanup frames
  try {
    fs.rmSync(framesDir, { recursive: true });
  } catch {
    // Ignore cleanup errors
  }
}

// CLI entry point
const url = process.argv[2];
const duration = parseInt(process.argv[3]) || 30;
const output = process.argv[4] || 'demo.mp4';

if (!url) {
  console.log('Usage: node record-demo.js <url> [duration_seconds] [output_file]');
  console.log('');
  console.log('Examples:');
  console.log('  node record-demo.js http://localhost:3000 30 demo.mp4');
  console.log('  node record-demo.js https://example.com 10 example-demo.mp4');
  process.exit(1);
}

recordDemo(url, duration, output).catch((err) => {
  console.error('[Demo Recorder] Error:', err.message);
  process.exit(1);
});
