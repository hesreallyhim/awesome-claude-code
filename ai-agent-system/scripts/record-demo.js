#!/usr/bin/env node
/**
 * Demo Recorder — Captures browser screenshots and compiles to video
 * Usage: node scripts/record-demo.js <url> [duration_sec] [output_name]
 */

const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

async function recordDemo(url, durationSecs = 30, outputName = 'demo.mp4') {
  let puppeteer;
  try {
    puppeteer = require('puppeteer-core');
  } catch {
    console.error('puppeteer-core not installed. Run: npm install');
    process.exit(1);
  }

  const outputDir = path.join(__dirname, '..', 'output', 'videos');
  const framesDir = path.join(outputDir, '.demo-frames');
  fs.mkdirSync(framesDir, { recursive: true });

  console.log(`[record] URL: ${url}`);
  console.log(`[record] Duration: ${durationSecs}s`);

  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: process.env.CHROME_PATH || 'google-chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1920, height: 1080 },
  });

  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

  const fps = 10;
  const totalFrames = durationSecs * fps;
  const interval = 1000 / fps;

  console.log(`[record] Capturing ${totalFrames} frames at ${fps}fps...`);

  for (let i = 0; i < totalFrames; i++) {
    await page.screenshot({
      path: path.join(framesDir, `frame-${String(i).padStart(6, '0')}.png`),
    });
    if (i > 0 && i % (fps * 5) === 0) {
      console.log(`[record] ${Math.round((i / totalFrames) * 100)}%`);
    }
    await new Promise((r) => setTimeout(r, interval));
  }

  await browser.close();
  console.log('[record] Frames captured. Encoding...');

  const outputPath = path.join(outputDir, outputName);
  try {
    execSync(
      `ffmpeg -y -framerate ${fps} -i "${framesDir}/frame-%06d.png" ` +
      `-c:v libx264 -pix_fmt yuv420p -crf 23 "${outputPath}"`,
      { stdio: 'pipe' }
    );
    console.log(`[record] Video saved: ${outputPath}`);
  } catch {
    console.error(`[record] FFmpeg failed. Raw frames in: ${framesDir}`);
    console.error(`[record] Encode manually: ffmpeg -framerate ${fps} -i "${framesDir}/frame-%06d.png" -c:v libx264 -pix_fmt yuv420p "${outputPath}"`);
  }

  try { fs.rmSync(framesDir, { recursive: true }); } catch {}
}

// CLI
const url = process.argv[2];
if (!url) {
  console.log('Usage: node scripts/record-demo.js <url> [seconds] [output.mp4]');
  process.exit(0);
}
recordDemo(url, parseInt(process.argv[3]) || 30, process.argv[4] || 'demo.mp4')
  .catch((e) => { console.error(e.message); process.exit(1); });
