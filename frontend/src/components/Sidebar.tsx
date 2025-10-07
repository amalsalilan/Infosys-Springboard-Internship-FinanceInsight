import { Button } from "@/components/ui/button";
import { BarChart3, Tag, Languages } from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onAnalysisSelect: (type: string) => void;
  selectedAnalysis: string;
}

const Sidebar = ({ onAnalysisSelect, selectedAnalysis }: SidebarProps) => {
  const analysisTypes = [
    { id: 'sentiment', label: 'Sentiment Analysis', icon: BarChart3 },
    { id: 'ner', label: 'Named Entity Recognition', icon: Tag },
    { id: 'langextract', label: 'Language Extract', icon: Languages },
  ];

  return (
    <aside className="w-64 bg-[hsl(var(--sidebar))] p-3 flex flex-col gap-1 border-r border-border">
      {analysisTypes.map((type) => {
        const Icon = type.icon;
        const isActive = selectedAnalysis === type.id;

        return (
          <Button
            key={type.id}
            variant="ghost"
            className={cn(
              "justify-start text-sm h-10 gap-3 transition-all duration-200 border-l-4 border-transparent",
              isActive && "bg-accent font-semibold border-l-primary shadow-sm",
              !isActive && "text-sidebar-foreground hover:bg-accent/50 hover:border-l-accent"
            )}
            onClick={() => onAnalysisSelect(type.id)}
          >
            <Icon className={cn("h-4 w-4", isActive && "text-primary")} />
            {type.label}
          </Button>
        );
      })}
    </aside>
  );
};

export default Sidebar;
