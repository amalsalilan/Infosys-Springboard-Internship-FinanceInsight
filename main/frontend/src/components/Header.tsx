import { FileText } from "lucide-react";

const Header = () => {
  return (
    <header className="h-14 bg-[hsl(var(--header))] border-b border-border">
      <div className="h-full flex items-center px-6 gap-3">
        <div className="h-7 w-7 rounded flex items-center justify-center">
          <FileText className="h-5 w-5 text-foreground" />
        </div>
        <h1 className="text-foreground text-base font-medium">Document Analysis</h1>
      </div>
    </header>
  );
};

export default Header;
