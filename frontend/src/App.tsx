import { useState } from "react";
import { Demo } from "./components/demo";
import { FineCalculator } from "./components/FineCalculator";
import { motion, AnimatePresence } from "framer-motion";
import { Calculator, X } from "lucide-react";
import { cn } from "./lib/utils";

function App() {
  const [showCalculator, setShowCalculator] = useState(false);

  return (
    <div className="min-h-screen bg-[#0B1829] text-white flex relative overflow-hidden">
      {/* Main Chat Area */}
      <div className={cn(
        "flex-1 transition-all duration-300",
        showCalculator ? "mr-[360px]" : ""
      )}>
        <Demo />
      </div>

      {/* Calculator Toggle Button */}
      <motion.button
        id="calculator-toggle-btn"
        type="button"
        onClick={() => setShowCalculator(p => !p)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.96 }}
        className={cn(
          "fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-3 rounded-xl",
          "text-sm font-semibold shadow-xl transition-all",
          showCalculator
            ? "bg-white/10 border border-white/20 text-white"
            : "bg-amber-500 text-black border border-amber-400/50 shadow-amber-500/30"
        )}
        title="Toggle Fine Calculator"
      >
        {showCalculator ? (
          <>
            <X className="w-4 h-4" />
            <span className="hidden sm:inline">Close</span>
          </>
        ) : (
          <>
            <Calculator className="w-4 h-4" />
            <span className="hidden sm:inline">Fine Calculator</span>
          </>
        )}
      </motion.button>

      {/* Calculator Sidebar */}
      <AnimatePresence>
        {showCalculator && (
          <motion.div
            initial={{ x: 360, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 360, opacity: 0 }}
            transition={{ type: "spring", damping: 22, stiffness: 250 }}
            className="fixed top-0 right-0 h-full w-[360px] z-40 flex flex-col backdrop-blur-2xl bg-[#0d1a2b]/95 border-l border-white/[0.06] shadow-2xl"
          >
            <FineCalculator />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Backdrop for mobile */}
      <AnimatePresence>
        {showCalculator && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-30 bg-black/30 backdrop-blur-[2px] sm:hidden"
            onClick={() => setShowCalculator(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
