import React, { useEffect, useRef } from "react";

export default function VoiceWave({ active }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    let animationId;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const bars = 40;

      for (let i = 0; i < bars; i++) {
        const height = active
          ? Math.random() * 60 + 10
          : Math.random() * 5;

        ctx.fillStyle = "#00ffcc";
        ctx.fillRect(i * 6, 50 - height / 2, 3, height);
      }

      animationId = requestAnimationFrame(draw);
    };

    draw();

    return () => cancelAnimationFrame(animationId);
  }, [active]);

  return (
    <canvas
      ref={canvasRef}
      width={240}
      height={100}
      style={{ background: "black", borderRadius: 12 }}
    />
  );
}