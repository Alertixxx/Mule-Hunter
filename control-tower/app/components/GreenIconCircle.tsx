import { LucideIcon } from "lucide-react";

interface GreenIconCircleProps {
  icon: LucideIcon;
  size?: "xs" | "sm" | "md";
  className?: string;
}

export default function GreenIconCircle({
  icon: Icon,
  size = "sm",
  className = "",
}: GreenIconCircleProps) {
  const sizeMap = {
    xs: {
      wrapper: "p-1",
      icon: "w-2 h-2",
    },
    sm: {
      wrapper: "p-1.5",
      icon: "w-3 h-3",
    },
    md: {
      wrapper: "p-2",
      icon: "w-4 h-4",
    },
  };

  return (
    <div
      className={`flex items-center justify-center rounded-full
      bg-lime-500/15 border border-lime-500
      ${sizeMap[size].wrapper} ${className}`}
    >
      <Icon className={`text-lime-400 ${sizeMap[size].icon}`} />
    </div>
  );
}
