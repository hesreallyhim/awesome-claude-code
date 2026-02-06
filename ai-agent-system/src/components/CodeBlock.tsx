import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

interface CodeBlockProps {
  code: string;
  language?: string;
  typingSpeed?: number; // frames per character
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = "javascript",
  typingSpeed = 1,
}) => {
  const frame = useCurrentFrame();

  const visibleChars = Math.floor(
    interpolate(frame, [0, code.length * typingSpeed], [0, code.length], {
      extrapolateRight: "clamp",
    })
  );

  const visibleCode = code.slice(0, visibleChars);
  const cursorVisible = frame % 30 > 15;

  return (
    <div
      style={{
        backgroundColor: "#1a1b26",
        borderRadius: 16,
        padding: "32px 40px",
        fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
        fontSize: 22,
        color: "#a9b1d6",
        whiteSpace: "pre-wrap",
        lineHeight: 1.6,
        border: "1px solid rgba(255,255,255,0.06)",
        boxShadow: "0 20px 60px rgba(0,0,0,0.4)",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Window controls */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#ff5f57" }} />
        <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#febc2e" }} />
        <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#28c840" }} />
        <span style={{ marginLeft: 12, fontSize: 13, color: "#565f89" }}>{language}</span>
      </div>

      {/* Code content */}
      <div>
        {visibleCode}
        <span style={{ opacity: cursorVisible ? 1 : 0, color: "#7aa2f7" }}>|</span>
      </div>
    </div>
  );
};
