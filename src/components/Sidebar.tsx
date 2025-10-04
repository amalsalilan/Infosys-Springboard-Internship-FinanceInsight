import { Button } from "@/components/ui/button";
import { BarChart3, Tag, Languages } from "lucide-react";

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
        return (
          <Button
            key={type.id}
            variant="ghost"
            className={`justify-start text-sm h-10 gap-3 transition-colors ${
              selectedAnalysis === type.id 
                ? "bg-secondary text-foreground" 
                : "text-sidebar-foreground hover:bg-secondary"
            }`}
            onClick={() => onAnalysisSelect(type.id)}
          >
            <Icon className="h-4 w-4" />
            {type.label}
          </Button>
        );
      })}
    </aside>
  );
};

export default Sidebar;
