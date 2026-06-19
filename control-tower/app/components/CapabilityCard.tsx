import { LucideIcon } from "lucide-react";

interface CapabilityCardProps {
  icon: LucideIcon;
  title: string;
  points: string[];
}

export default function CapabilityCard({
  icon: Icon,
  title,
  points,
}: CapabilityCardProps) {
  return (
    <div className="flex flex-col gap-3 p-6 border border-gray-900 rounded-2xl bg-gray-950 hover:bg-gray-900 transition items-center">
      
      
      <Icon className="w-6 h-6 text-gray-400" />

      
      <h2 className="font-bold text-lg">{title}</h2>

      
      <div>
        {points.map((point, idx) => (
        <div key={idx} className="text-sm text-gray-500 ">
          {point}
        </div>
      ))}
      </div>
    </div>
  );
}
