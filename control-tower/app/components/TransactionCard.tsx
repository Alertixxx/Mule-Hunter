"use client";

import { ArrowLeftRight, AlertTriangle, ShieldCheck } from "lucide-react";
import { JSX } from "react/jsx-dev-runtime";

type RiskLevel = "HIGH" | "MEDIUM" | "LOW";

interface TransactionCardProps {
  nodeId: number;
  risk: RiskLevel;
  amount: number;
  onClick?: (nodeId: number) => void;
}

export default function TransactionCard({
  nodeId,
  risk,
  amount,
  onClick,
}: TransactionCardProps) {
  const riskStyles: Record<
    RiskLevel,
    { color: string; bg: string; icon: JSX.Element }
  > = {
    HIGH: {
      color: "text-red-400",
      bg: "bg-red-500",
      icon: <AlertTriangle className="w-3 h-3 text-black" strokeWidth={3} />,
    },
    MEDIUM: {
      color: "text-yellow-400",
      bg: "bg-yellow-400",
      icon: <ArrowLeftRight className="w-3 h-3 text-black" strokeWidth={3} />,
    },
    LOW: {
      color: "text-green-400",
      bg: "bg-lime-500",
      icon: <ShieldCheck className="w-3 h-3 text-black" strokeWidth={3} />,
    },
  };

  const { color, bg, icon } = riskStyles[risk];

  return (
    <div
      
      className="flex justify-between border border-gray-900 p-2 rounded-lg bg-gray-950  "
    >
      <div className="flex gap-3 items-center">
        <span className={`flex items-center justify-center w-5 h-5 rounded-full ${bg}`}>
          {icon}
        </span>

        <div>
          <div className="text-gray-400 text-sm">Node #{nodeId}</div>
          <div className={`text-sm font-medium ${color}`}>
            Risk: {risk}
          </div>
        </div>
      </div>

      <div className="text-gray-200 font-medium flex items-center">
        ₹{amount.toLocaleString("en-IN")}
      </div>
    </div>
  );
}
