import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Calculator, ChevronDown, ExternalLink, Loader2, ShieldAlert } from "lucide-react";
import { api, getOrCreateSessionId, type CalculatorResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

const VIOLATIONS = [
  { value: "speeding",        label: "Speeding" },
  { value: "helmet",          label: "No Helmet" },
  { value: "drunk_driving",   label: "Drunk Driving" },
  { value: "mobile_phone",    label: "Mobile Phone Use" },
  { value: "no_insurance",    label: "No Insurance" },
  { value: "no_license",      label: "No Licence" },
  { value: "no_puc",          label: "No PUC Certificate" },
  { value: "seatbelt",        label: "No Seatbelt" },
  { value: "red_light",       label: "Red Light Jump" },
  { value: "triple_riding",   label: "Triple Riding" },
  { value: "wrong_side",      label: "Wrong Side Driving" },
  { value: "juvenile_driving", label: "Juvenile Driving" },
];

const VEHICLE_TYPES = [
  { value: "two_wheeler",    label: "Two-Wheeler (Bike/Scooter)" },
  { value: "three_wheeler",  label: "Three-Wheeler (Auto)" },
  { value: "LMV",            label: "Light Motor Vehicle (Car)" },
  { value: "HMV",            label: "Heavy Motor Vehicle (Truck/Bus)" },
];

const STATES = [
  "Tamil Nadu", "Maharashtra", "Karnataka", "Delhi", "Gujarat",
  "Kerala", "Telangana", "West Bengal", "Andhra Pradesh", "Rajasthan",
  "Uttar Pradesh", "Madhya Pradesh", "Bihar", "Punjab", "Haryana",
  "Odisha", "Assam", "Chhattisgarh", "Jharkhand", "Goa",
];

const OFFENSE_TYPES = [
  { value: "first",  label: "First Offence" },
  { value: "repeat", label: "Repeat Offence" },
];

interface SelectProps {
  id: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  placeholder: string;
}

function Select({ id, value, onChange, options, placeholder }: SelectProps) {
  const [open, setOpen] = useState(false);
  const selected = options.find(o => o.value === value);

  return (
    <div className="relative" id={id}>
      <button
        type="button"
        onClick={() => setOpen(p => !p)}
        className={cn(
          "w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm",
          "bg-white/[0.04] border border-white/[0.08] text-left",
          "hover:bg-white/[0.07] hover:border-white/[0.14] transition-all",
          open && "border-blue-500/40 bg-blue-950/20",
        )}
      >
        <span className={selected ? "text-white/90" : "text-white/30"}>
          {selected?.label ?? placeholder}
        </span>
        <ChevronDown className={cn("w-4 h-4 text-white/40 transition-transform", open && "rotate-180")} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.12 }}
            className="absolute z-50 w-full mt-1 max-h-52 overflow-y-auto rounded-lg border border-white/10 bg-[#0d1a2b]/95 backdrop-blur-xl shadow-xl"
          >
            {options.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => { onChange(opt.value); setOpen(false); }}
                className={cn(
                  "w-full text-left px-3 py-2 text-sm transition-colors",
                  opt.value === value
                    ? "bg-blue-600/30 text-white"
                    : "text-white/70 hover:bg-white/[0.05] hover:text-white",
                )}
              >
                {opt.label}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

interface FineResultProps {
  result: CalculatorResponse;
}

function FineResult({ result }: FineResultProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 space-y-3"
    >
      <div className="flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-amber-400" />
        <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Fine Estimate</span>
      </div>

      <div className="text-2xl font-bold text-white">{result.fine_display}</div>

      <div className="space-y-1.5 text-xs text-white/60">
        <div><span className="text-white/40">Section:</span>{" "}<span className="text-white/80">{result.section}</span></div>
        <div><span className="text-white/40">State:</span>{" "}<span className="text-white/80">{result.state}</span></div>
        <div><span className="text-white/40">Offence:</span>{" "}<span className="text-white/80">{result.offense === "first" ? "First offence" : "Repeat offence"}</span></div>
      </div>

      {result.state_note && (
        <div className="text-xs text-amber-300/80 bg-amber-500/10 rounded-lg px-3 py-2 border border-amber-500/20">
          ℹ️ {result.state_note}
        </div>
      )}

      <a
        href={result.parivahan_link}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors pt-1"
      >
        <ExternalLink className="w-3.5 h-3.5" />
        Check & pay on echallan.parivahan.gov.in
      </a>
    </motion.div>
  );
}

export function FineCalculator() {
  const [violation, setViolation]     = useState("");
  const [vehicleType, setVehicleType] = useState("");
  const [state, setState]             = useState("");
  const [offense, setOffense]         = useState("first");
  const [loading, setLoading]         = useState(false);
  const [result, setResult]           = useState<CalculatorResponse | null>(null);
  const [error, setError]             = useState<string | null>(null);

  const canCalculate = violation && vehicleType && state;

  const handleCalculate = async () => {
    if (!canCalculate) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await api.calculateFine({
        violation,
        vehicle_type: vehicleType,
        state,
        offense_count: offense,
        session_id: getOrCreateSessionId(),
      });
      setResult(resp);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to calculate fine");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-4 border-b border-white/[0.05]">
        <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
          <Calculator className="w-3.5 h-3.5 text-amber-400" />
        </div>
        <div>
          <div className="text-sm font-semibold text-white/90">Fine Calculator</div>
          <div className="text-[10px] text-white/40">MV Act 2019 Schedule</div>
        </div>
      </div>

      {/* Form */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-white/50 uppercase tracking-wider">Violation</label>
          <Select
            id="calc-violation"
            value={violation}
            onChange={setViolation}
            options={VIOLATIONS}
            placeholder="Select violation type"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-white/50 uppercase tracking-wider">Vehicle Type</label>
          <Select
            id="calc-vehicle"
            value={vehicleType}
            onChange={setVehicleType}
            options={VEHICLE_TYPES}
            placeholder="Select vehicle type"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-white/50 uppercase tracking-wider">State</label>
          <Select
            id="calc-state"
            value={state}
            onChange={setState}
            options={STATES.map(s => ({ value: s, label: s }))}
            placeholder="Select your state"
          />
        </div>

        <div className="space-y-1.5">
          <label className="text-xs font-medium text-white/50 uppercase tracking-wider">Offence Type</label>
          <div className="flex gap-2">
            {OFFENSE_TYPES.map(o => (
              <button
                key={o.value}
                type="button"
                onClick={() => setOffense(o.value)}
                className={cn(
                  "flex-1 py-2.5 rounded-lg text-xs font-medium transition-all border",
                  offense === o.value
                    ? "bg-blue-600/30 border-blue-500/40 text-blue-300"
                    : "bg-white/[0.03] border-white/[0.07] text-white/50 hover:bg-white/[0.06]",
                )}
              >
                {o.label}
              </button>
            ))}
          </div>
        </div>

        <motion.button
          type="button"
          onClick={handleCalculate}
          disabled={!canCalculate || loading}
          whileTap={{ scale: 0.98 }}
          className={cn(
            "w-full py-3 rounded-xl text-sm font-semibold transition-all flex items-center justify-center gap-2",
            canCalculate && !loading
              ? "bg-amber-500 hover:bg-amber-400 text-black shadow-lg shadow-amber-500/20"
              : "bg-white/[0.05] text-white/30 cursor-not-allowed",
          )}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Calculating…
            </>
          ) : (
            <>
              <Calculator className="w-4 h-4" />
              Calculate Fine
            </>
          )}
        </motion.button>

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2"
          >
            {error}
          </motion.div>
        )}

        <AnimatePresence>
          {result && <FineResult result={result} />}
        </AnimatePresence>
      </div>
    </div>
  );
}
