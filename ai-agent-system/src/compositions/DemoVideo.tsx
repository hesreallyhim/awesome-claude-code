import React from "react";
import { AbsoluteFill, Sequence, Img, staticFile } from "remotion";
import { Title } from "../components/Title";
import { Caption } from "../components/Caption";

interface CaptionData {
  start: number;
  end: number;
  text: string;
}

interface DemoVideoProps {
  title: string;
  screenshotPaths: string[];
  captions: CaptionData[];
}

const ScreenshotFrame: React.FC<{ path: string }> = ({ path }) => {
  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: 40,
        backgroundColor: "#0f0f1a",
      }}
    >
      <Img
        src={staticFile(path)}
        style={{
          maxWidth: "92%",
          maxHeight: "88%",
          borderRadius: 16,
          boxShadow: "0 25px 80px rgba(0, 0, 0, 0.6)",
          border: "1px solid rgba(255,255,255,0.08)",
        }}
      />
    </AbsoluteFill>
  );
};

export const DemoVideo: React.FC<DemoVideoProps> = ({
  title,
  screenshotPaths,
  captions,
}) => {
  const titleDuration = 60;
  const screenshotDuration = 150;

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f" }}>
      {/* Title */}
      <Sequence durationInFrames={titleDuration}>
        <Title text={title} subtitle="Live Demo" accentColor="#10b981" />
      </Sequence>

      {/* Screenshots */}
      {screenshotPaths.map((p, i) => (
        <Sequence
          key={i}
          from={titleDuration + i * screenshotDuration}
          durationInFrames={screenshotDuration}
        >
          <ScreenshotFrame path={p} />
        </Sequence>
      ))}

      {/* Caption overlay */}
      {captions.map((c, i) => (
        <Sequence key={`cap-${i}`} from={c.start} durationInFrames={c.end - c.start}>
          <Caption text={c.text} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
