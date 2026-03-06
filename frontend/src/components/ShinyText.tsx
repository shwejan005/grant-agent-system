"use client";

interface ShinyTextProps {
    text: string;
    disabled?: boolean;
    speed?: number;
    className?: string;
}

export default function ShinyText({ text, disabled = false, speed = 3, className = "" }: ShinyTextProps) {
    const animationDuration = `${speed}s`;

    return (
        <div
            className={`text-foreground/70 bg-clip-text inline-block ${disabled ? "" : "animate-shine"} ${className}`}
            style={{
                backgroundImage: "linear-gradient(120deg, rgba(0, 0, 0, 0) 40%, rgba(0, 0, 0, 0.8) 50%, rgba(0, 0, 0, 0) 60%)",
                backgroundSize: "200% 100%",
                WebkitBackgroundClip: "text",
                animationDuration: animationDuration,
            }}
        >
            {text}
        </div>
    );
}
