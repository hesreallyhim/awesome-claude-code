import React from "react";
import {
  AbsoluteFill,
  Sequence,
  Img,
  useCurrentFrame,
  interpolate,
  staticFile,
} from "remotion";

interface Caption {
  start: number;
  end: number;
  text: string;
}

interface DemoVideoProps {
  title: string;
  screenshotPaths: string[];
  captions: Caption[];
}

const DemoTitle: React.FC<{ title: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "#000000",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <h1
        style={{
          fontSize: 72,
          color: "#ffffff",
          opacity,
          fontWeight: "bold",
        }}
      >
        {title}
      </h1>
    </AbsoluteFill>
  );
};

const CaptionOverlay: React.FC<{ captions: Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const currentCaption = captions.find(
    (c) => frame >= c.start && frame < c.end
  );

  if (!currentCaption) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 80,
        left: 0,
        right: 0,
        textAlign: "center",
        zIndex: 100,
      }}
    >
      <span
        style={{
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          color: "#ffffff",
          fontSize: 36,
          padding: "12px 32px",
          borderRadius: 8,
          fontFamily: "system-ui, sans-serif",
        }}
      >
        {currentCaption.text}
      </span>
    </div>
  );
};

export const DemoVideo: React.FC<DemoVideoProps> = ({
  title,
  screenshotPaths,
  captions,
}) => {
  const titleDuration = 60;
  const screenshotDuration = 150; // 5 seconds each

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }}>
      <Sequence durationInFrames={titleDuration}>
        <DemoTitle title={title} />
      </Sequence>

      {screenshotPaths.map((path, index) => (
        <Sequence
          key={index}
          from={titleDuration + index * screenshotDuration}
          durationInFrames={screenshotDuration}
        >
          <AbsoluteFill
            style={{
              justifyContent: "center",
              alignItems: "center",
              padding: 40,
            }}
          >
            <Img
              src={staticFile(path)}
              style={{
                maxWidth: "90%",
                maxHeight: "85%",
                borderRadius: 12,
                boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
              }}
            />
          </AbsoluteFill>
        </Sequence>
      ))}

      <CaptionOverlay captions={captions} />
    </AbsoluteFill>
  );
};
