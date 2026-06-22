"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  BarChart3, Box, Truck, Sparkles, Bell, Cpu, 
  Lightbulb, Target, Users, Puzzle, Settings, ChevronLeft, ChevronRight 
} from "lucide-react";

interface SidebarProps {
  isCollapsed: boolean;
  setIsCollapsed: (collapsed: boolean) => void;
}

export default function Sidebar({ isCollapsed, setIsCollapsed }: SidebarProps) {
  const pathname = usePathname();

  const menuSections = [
    {
      title: "System Operations",
      items: [
        { href: "/", label: "Dashboard", icon: BarChart3 },
        { href: "/inventory", label: "Inventory", icon: Box },
        { href: "/shipments", label: "Shipments", icon: Truck },
        { href: "/simulation", label: "Simulation Center", icon: Sparkles },
        { href: "/alerts", label: "Alerts", icon: Bell },
      ]
    },
    {
      title: "AI & Insights",
      items: [
        { href: "/agents", label: "Agent Monitor", icon: Cpu },
        { href: "/insights", label: "AI Insights", icon: Lightbulb },
        { href: "/recommender", label: "Recommender", icon: Target },
      ]
    },
    {
      title: "Settings",
      items: [
        { href: "/users", label: "Users & Roles", icon: Users },
        { href: "/integrations", label: "Integrations", icon: Puzzle },
        { href: "/settings", label: "System Settings", icon: Settings },
      ]
    }
  ];

  return (
    <aside 
      className={`sticky top-0 h-screen bg-[#0F172A] border-r border-white/10 z-50 flex flex-col justify-between transition-all duration-300 ${
        isCollapsed ? "w-[72px]" : "w-[260px]"
      }`}
    >
      {/* LOGO SECTION */}
      <div>
        <div className="h-[72px] flex items-center px-6 border-b border-white/10">
          <Link href="/" className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center text-white text-lg font-bold shadow-md shadow-blue-500/20">
              🌊
            </div>
            {!isCollapsed && (
              <div className="flex flex-col">
                <span className="text-sm font-extrabold text-white tracking-tight leading-none">OmniFlow AI</span>
                <span className="text-[9px] text-[#94A3B8] uppercase tracking-widest font-semibold mt-1">AI Supply Chain</span>
              </div>
            )}
          </Link>
        </div>

        {/* NAVIGATION LISTS */}
        <div className="py-6 overflow-y-auto px-4 space-y-7 max-h-[calc(100vh-190px)]">
          {menuSections.map((section, sIdx) => (
            <div key={sIdx} className="space-y-2">
              {!isCollapsed && (
                <p className="text-[10px] uppercase tracking-widest text-slate-500 font-extrabold px-3">
                  {section.title}
                </p>
              )}
              <nav className="space-y-1.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`sidebar-link ${isActive ? "active" : ""}`}
                      title={isCollapsed ? item.label : ""}
                    >
                      <Icon className={`h-4.5 w-4.5 min-w-4.5 ${isActive ? "text-white" : "text-[#94A3B8]"}`} />
                      {!isCollapsed && <span className="truncate">{item.label}</span>}
                    </Link>
                  );
                })}
              </nav>
            </div>
          ))}
        </div>
      </div>

      {/* FOOTER USER PROFILE CARD */}
      <div className="p-4 border-t border-white/10 space-y-2 bg-[#0A0F1D]/45">
        <div className="flex items-center justify-between gap-3 overflow-hidden">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="h-9 w-9 rounded-xl bg-slate-800 border border-white/15 flex items-center justify-center font-bold text-xs text-white shadow-sm flex-shrink-0">
              A
            </div>
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <p className="text-xs font-bold text-white truncate leading-none mb-0.5">Admin User</p>
                <p className="text-[10px] text-slate-500 truncate leading-none">admin@omniflow.ai</p>
              </div>
            )}
          </div>
        </div>

        {/* Collapse toggle button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-start gap-3 p-2 hover:bg-white/5 rounded-lg text-[#94A3B8] hover:text-white transition-colors text-xs font-semibold cursor-pointer"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4.5 w-4.5 mx-auto" />
          ) : (
            <div className="flex items-center gap-2">
              <ChevronLeft className="h-4 w-4" />
              <span>Collapse</span>
            </div>
          )}
        </button>
      </div>
    </aside>
  );
}
