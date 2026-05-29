"use client";

import { useEffect, useRef, useCallback, useTransition, useState } from "react";
import { cn } from "@/lib/utils";
import {
    FileUp,
    MonitorIcon,
    CircleUserRound,
    Paperclip,
    PlusIcon,
    SendIcon,
    XIcon,
    LoaderIcon,
    Sparkles,
    Command,
    ShieldCheck,
    Gauge,
    FileText,
    ShieldAlert,
    MapPin,
    Clock,
    ExternalLink,
    Bot,
    User,
    AlertCircle,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as React from "react";
import { api, getOrCreateSessionId, type ChatResponse } from "@/lib/api";

// ── Auto-resize textarea hook ─────────────────────────────────────────────────
interface UseAutoResizeTextareaProps {
    minHeight: number;
    maxHeight?: number;
}

function useAutoResizeTextarea({ minHeight, maxHeight }: UseAutoResizeTextareaProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = useCallback(
        (reset?: boolean) => {
            const textarea = textareaRef.current;
            if (!textarea) return;
            if (reset) { textarea.style.height = `${minHeight}px`; return; }
            textarea.style.height = `${minHeight}px`;
            const newHeight = Math.max(minHeight, Math.min(textarea.scrollHeight, maxHeight ?? Number.POSITIVE_INFINITY));
            textarea.style.height = `${newHeight}px`;
        },
        [minHeight, maxHeight]
    );

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) textarea.style.height = `${minHeight}px`;
    }, [minHeight]);

    useEffect(() => {
        const handleResize = () => adjustHeight();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [adjustHeight]);

    return { textareaRef, adjustHeight };
}

// ── Typing indicator ──────────────────────────────────────────────────────────
function TypingDots() {
    return (
        <div className="flex items-center ml-1">
            {[1, 2, 3].map((dot) => (
                <motion.div
                    key={dot}
                    className="w-1.5 h-1.5 bg-white/90 rounded-full mx-0.5"
                    initial={{ opacity: 0.3 }}
                    animate={{ opacity: [0.3, 0.9, 0.3], scale: [0.85, 1.1, 0.85] }}
                    transition={{ duration: 1.2, repeat: Infinity, delay: dot * 0.15, ease: "easeInOut" }}
                    style={{ boxShadow: "0 0 4px rgba(255, 255, 255, 0.3)" }}
                />
            ))}
        </div>
    );
}

// ── Message types ─────────────────────────────────────────────────────────────
interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    parivahan_link?: string | null;
    error?: boolean;
    timestamp: Date;
}

// ── Chat bubble ───────────────────────────────────────────────────────────────
function ChatBubble({ message, index }: { message: Message; index: number }) {
    const isUser = message.role === "user";

    return (
        <motion.div
            initial={{ opacity: 0, y: 10, x: isUser ? 10 : -10 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.03 }}
            className={cn("flex items-start gap-3", isUser && "flex-row-reverse")}
        >
            {/* Avatar */}
            <div className={cn(
                "w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-1",
                isUser
                    ? "bg-blue-600/30 border border-blue-500/30"
                    : "bg-amber-500/10 border border-amber-500/20"
            )}>
                {isUser
                    ? <User className="w-3.5 h-3.5 text-blue-400" />
                    : <Bot className="w-3.5 h-3.5 text-amber-400" />
                }
            </div>

            {/* Bubble */}
            <div className={cn("max-w-[78%] space-y-2", isUser && "items-end")}>
                <div className={cn(
                    "rounded-2xl px-4 py-3 text-sm leading-relaxed",
                    isUser
                        ? "bg-[#1a5fa8] text-white rounded-tr-sm"
                        : message.error
                            ? "bg-red-500/10 border border-red-500/20 text-red-300 rounded-tl-sm"
                            : "bg-white/[0.05] border border-white/[0.07] text-white/90 rounded-tl-sm"
                )}>
                    {message.error && <AlertCircle className="w-4 h-4 inline mr-1.5 text-red-400" />}
                    <span className="whitespace-pre-wrap">{message.content}</span>
                </div>

                {/* Parivahan link */}
                {message.parivahan_link && (
                    <motion.a
                        href={message.parivahan_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors pl-1"
                    >
                        <ExternalLink className="w-3 h-3" />
                        Check & pay on echallan.parivahan.gov.in
                    </motion.a>
                )}

                {/* Timestamp */}
                <div className={cn("text-[10px] text-white/25 px-1", isUser && "text-right")}>
                    {message.timestamp.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
                </div>
            </div>
        </motion.div>
    );
}

// ── Command suggestion types ──────────────────────────────────────────────────
interface CommandSuggestion {
    icon: React.ReactNode;
    label: string;
    description: string;
    prefix: string;
}

// ── Textarea with ring ────────────────────────────────────────────────────────
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
    containerClassName?: string;
    showRing?: boolean;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
    ({ className, containerClassName, showRing = true, ...props }, ref) => {
        const [isFocused, setIsFocused] = React.useState(false);
        return (
            <div className={cn("relative", containerClassName)}>
                <textarea
                    className={cn(
                        "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                        "transition-all duration-200 ease-in-out",
                        "placeholder:text-muted-foreground",
                        "disabled:cursor-not-allowed disabled:opacity-50",
                        showRing ? "focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0" : "",
                        className
                    )}
                    ref={ref}
                    onFocus={() => setIsFocused(true)}
                    onBlur={() => setIsFocused(false)}
                    {...props}
                />
                {showRing && isFocused && (
                    <motion.span
                        className="absolute inset-0 rounded-md pointer-events-none ring-2 ring-offset-0 ring-[#1a5fa8]/30"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    />
                )}
            </div>
        );
    }
);
Textarea.displayName = "Textarea";

// ── Main chat component ───────────────────────────────────────────────────────
export function AnimatedAIChat() {
    const [value, setValue] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isPending, startTransition] = useTransition();
    const [activeSuggestion, setActiveSuggestion] = useState<number>(-1);
    const [showCommandPalette, setShowCommandPalette] = useState(false);
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [currentTime, setCurrentTime] = useState("");
    const [inputFocused, setInputFocused] = useState(false);
    const [sessionId] = useState(() => getOrCreateSessionId());

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const commandPaletteRef = useRef<HTMLDivElement>(null);
    const { textareaRef, adjustHeight } = useAutoResizeTextarea({ minHeight: 60, maxHeight: 200 });

    // Clock
    useEffect(() => {
        const updateTime = () => {
            setCurrentTime(new Date().toLocaleTimeString("en-IN", {
                hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: true,
            }));
        };
        updateTime();
        const iv = setInterval(updateTime, 1000);
        return () => clearInterval(iv);
    }, []);

    // Scroll to bottom on new messages
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    // Mouse tracking
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => setMousePosition({ x: e.clientX, y: e.clientY });
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    // Command palette outside click
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Node;
            const commandButton = document.querySelector("[data-command-button]");
            if (commandPaletteRef.current && !commandPaletteRef.current.contains(target) && !commandButton?.contains(target)) {
                setShowCommandPalette(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const commandSuggestions: CommandSuggestion[] = [
        { icon: <CircleUserRound className="w-4 h-4" />, label: "Speed Limits", description: "Speed limits by road type", prefix: "/speed" },
        { icon: <MonitorIcon className="w-4 h-4" />, label: "Road Signs",  description: "Meaning of traffic signs", prefix: "/signs" },
        { icon: <FileUp className="w-4 h-4" />, label: "Challan Check", description: "Check pending challans", prefix: "/challan" },
        { icon: <Sparkles className="w-4 h-4" />, label: "DUI Penalty",  description: "Drunk driving rules & fines", prefix: "/dui" },
    ];

    const quickReplyChips = [
        { label: "Speed Limits",   icon: <Gauge className="w-3.5 h-3.5 text-[#f5a623]" />,      text: "What are the speed limits on national highways in India?" },
        { label: "Helmet Fine",    icon: <MonitorIcon className="w-3.5 h-3.5 text-[#f5a623]" />, text: "What is the fine for not wearing a helmet?" },
        { label: "Licence Rules",  icon: <FileText className="w-3.5 h-3.5 text-[#f5a623]" />,   text: "What documents do I need to carry while driving?" },
        { label: "Drunk Driving",  icon: <ShieldAlert className="w-3.5 h-3.5 text-[#f5a623]" />,text: "What is the penalty for drunk driving in India?" },
        { label: "Challan Check",  icon: <FileUp className="w-3.5 h-3.5 text-[#f5a623]" />,     text: "How do I check and pay my traffic challan online?" },
    ];

    // Command palette auto-show
    useEffect(() => {
        if (value.startsWith("/") && !value.includes(" ")) {
            setShowCommandPalette(true);
            const idx = commandSuggestions.findIndex(cmd => cmd.prefix.startsWith(value));
            setActiveSuggestion(idx >= 0 ? idx : -1);
        } else {
            setShowCommandPalette(false);
        }
    }, [value]);

    // ── Command prefix → full text mapping ──────────────────────────────────
    const COMMAND_TEXT_MAP: Record<string, string> = {
        "/speed":   "What are the speed limits on Indian roads?",
        "/signs":   "Explain common Indian traffic road signs.",
        "/challan": "How do I check and pay my traffic challan online?",
        "/dui":     "What is the fine and penalty for drunk driving in India?",
        "/licence": "What are the rules for obtaining a driving licence in India?",
    };

    const selectCommandSuggestion = (index: number) => {
        const cmd = commandSuggestions[index];
        setValue(COMMAND_TEXT_MAP[cmd.prefix] ?? cmd.prefix + " ");
        setShowCommandPalette(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (showCommandPalette) {
            if (e.key === "ArrowDown") { e.preventDefault(); setActiveSuggestion(p => p < commandSuggestions.length - 1 ? p + 1 : 0); }
            else if (e.key === "ArrowUp") { e.preventDefault(); setActiveSuggestion(p => p > 0 ? p - 1 : commandSuggestions.length - 1); }
            else if ((e.key === "Tab" || e.key === "Enter") && activeSuggestion >= 0) { e.preventDefault(); selectCommandSuggestion(activeSuggestion); }
            else if (e.key === "Escape") { e.preventDefault(); setShowCommandPalette(false); }
        } else if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (value.trim()) handleSendMessage();
        }
    };

    const handleSendMessage = async (overrideText?: string) => {
        const text = (overrideText ?? value).trim();
        if (!text || isLoading) return;

        const userMsg: Message = {
            id: crypto.randomUUID(),
            role: "user",
            content: text,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMsg]);
        setValue("");
        adjustHeight(true);
        setIsLoading(true);

        try {
            const resp: ChatResponse = await api.sendChat({
                message: text,
                session_id: sessionId,
            });

            const assistantMsg: Message = {
                id: crypto.randomUUID(),
                role: "assistant",
                content: resp.reply,
                parivahan_link: resp.parivahan_link,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, assistantMsg]);
        } catch (err: unknown) {
            const errorMsg: Message = {
                id: crypto.randomUUID(),
                role: "assistant",
                content: err instanceof Error ? err.message : "Failed to connect to the server. Please make sure the backend is running.",
                error: true,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const isEmpty = messages.length === 0;

    return (
        <div className="min-h-screen flex flex-col w-full items-center justify-center bg-transparent text-white p-6 relative overflow-hidden">
            {/* Top Left Badge */}
            <div className="absolute top-6 left-6 z-20 flex items-center gap-3 text-[11px] text-white/50 bg-white/[0.02] border border-white/[0.06] backdrop-blur-xl px-3 py-1.5 rounded-full select-none">
                <div className="flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-[#f5a623]" />
                    <span className="font-medium text-white/80">DriveLegal AI</span>
                </div>
                <div className="h-3 w-px bg-white/10" />
                <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-[#f5a623]" />
                    <span className="tabular-nums">{currentTime}</span>
                </div>
            </div>

            {/* Ambient glow */}
            <div className="absolute inset-0 w-full h-full overflow-hidden">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-900/20 rounded-full mix-blend-normal filter blur-[128px] animate-pulse" />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-900/20 rounded-full mix-blend-normal filter blur-[128px] animate-pulse delay-700" />
                <div className="absolute top-1/4 right-1/3 w-64 h-64 bg-amber-500/5 rounded-full mix-blend-normal filter blur-[96px] animate-pulse delay-1000" />
            </div>

            <div className="w-full max-w-2xl mx-auto relative">
                <motion.div
                    className="relative z-10 space-y-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                >
                    {/* Header — only show when no messages */}
                    <AnimatePresence>
                        {isEmpty && (
                            <motion.div
                                className="text-center space-y-3"
                                initial={{ opacity: 1 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.3 }}
                            >
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.1, duration: 0.4 }}
                                    className="flex items-center justify-center gap-1.5 text-[10px] tracking-[0.2em] uppercase font-bold text-amber-500/80 mb-1"
                                >
                                    <ShieldCheck className="w-4 h-4 text-[#f5a623]" />
                                    <span>Official · Government of India</span>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.2, duration: 0.5 }}
                                    className="inline-block"
                                >
                                    <h1 className="text-3xl font-medium tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white/95 via-white/80 to-white/40 pb-1">
                                        Traffic Rules Assistant
                                    </h1>
                                    <motion.div
                                        className="h-px bg-gradient-to-r from-transparent via-[#1a5fa8]/50 to-transparent"
                                        initial={{ width: 0, opacity: 0 }}
                                        animate={{ width: "100%", opacity: 1 }}
                                        transition={{ delay: 0.5, duration: 0.8 }}
                                    />
                                </motion.div>
                                <motion.p
                                    className="text-sm text-white/50"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: 0.3 }}
                                >
                                    Ministry of Road Transport &amp; Highways · Official Guide
                                </motion.p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* ── Chat History ─────────────────────────────────────────── */}
                    {!isEmpty && (
                        <div className="space-y-4 max-h-[55vh] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                            {messages.map((msg, i) => (
                                <ChatBubble key={msg.id} message={msg} index={i} />
                            ))}
                            {/* Loading indicator */}
                            <AnimatePresence>
                                {isLoading && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 8 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0 }}
                                        className="flex items-start gap-3"
                                    >
                                        <div className="w-7 h-7 rounded-full bg-amber-500/10 border border-amber-500/20 flex items-center justify-center flex-shrink-0 mt-1">
                                            <Bot className="w-3.5 h-3.5 text-amber-400" />
                                        </div>
                                        <div className="bg-white/[0.05] border border-white/[0.07] rounded-2xl rounded-tl-sm px-4 py-3">
                                            <div className="flex items-center gap-2 text-sm text-white/60">
                                                <span>Thinking</span>
                                                <TypingDots />
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                            <div ref={messagesEndRef} />
                        </div>
                    )}

                    {/* ── Input Box ─────────────────────────────────────────────── */}
                    <motion.div
                        className="relative backdrop-blur-2xl bg-white/[0.02] rounded-2xl border border-white/[0.05] shadow-2xl"
                        initial={{ scale: 0.98 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.1 }}
                    >
                        {/* Command Palette */}
                        <AnimatePresence>
                            {showCommandPalette && (
                                <motion.div
                                    ref={commandPaletteRef}
                                    className="absolute left-4 right-4 bottom-full mb-2 backdrop-blur-xl bg-black/90 rounded-lg z-50 shadow-lg border border-white/10 overflow-hidden"
                                    initial={{ opacity: 0, y: 5 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: 5 }}
                                    transition={{ duration: 0.15 }}
                                >
                                    <div className="py-1 bg-black/95">
                                        {commandSuggestions.map((suggestion, index) => (
                                            <motion.div
                                                key={suggestion.prefix}
                                                className={cn(
                                                    "flex items-center gap-2 px-3 py-2 text-xs transition-colors cursor-pointer",
                                                    activeSuggestion === index ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5"
                                                )}
                                                onClick={() => selectCommandSuggestion(index)}
                                                initial={{ opacity: 0 }}
                                                animate={{ opacity: 1 }}
                                                transition={{ delay: index * 0.03 }}
                                            >
                                                <div className="w-5 h-5 flex items-center justify-center text-white/60">{suggestion.icon}</div>
                                                <div className="font-medium">{suggestion.label}</div>
                                                <div className="text-white/40 text-xs ml-1">{suggestion.prefix}</div>
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Textarea */}
                        <div className="p-4">
                            <Textarea
                                ref={textareaRef}
                                value={value}
                                onChange={(e) => { setValue(e.target.value); adjustHeight(); }}
                                onKeyDown={handleKeyDown}
                                onFocus={() => setInputFocused(true)}
                                onBlur={() => setInputFocused(false)}
                                placeholder="Ask about speed limits, fines, road signs, licence rules…"
                                containerClassName="w-full"
                                className={cn(
                                    "w-full px-4 py-3 resize-none bg-transparent border-none",
                                    "text-white/90 text-sm focus:outline-none",
                                    "placeholder:text-white/20 min-h-[60px]",
                                )}
                                style={{ overflow: "hidden" }}
                                showRing={false}
                            />
                        </div>

                        {/* Action bar */}
                        <div className="p-4 border-t border-white/[0.05] flex items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <motion.button
                                    type="button"
                                    data-command-button
                                    onClick={(e) => { e.stopPropagation(); setShowCommandPalette(p => !p); }}
                                    whileTap={{ scale: 0.94 }}
                                    className={cn(
                                        "p-2 text-white/40 hover:text-white/90 rounded-lg transition-colors relative group",
                                        showCommandPalette && "bg-white/10 text-white/90"
                                    )}
                                >
                                    <Command className="w-4 h-4" />
                                </motion.button>
                            </div>

                            <motion.button
                                type="button"
                                id="send-message-btn"
                                onClick={() => handleSendMessage()}
                                whileHover={{ scale: 1.01 }}
                                whileTap={{ scale: 0.98 }}
                                disabled={isLoading || !value.trim()}
                                className={cn(
                                    "px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2",
                                    value.trim() && !isLoading
                                        ? "bg-[#1a5fa8] text-white shadow-lg shadow-blue-900/30 hover:bg-[#154e8c]"
                                        : "bg-white/[0.05] text-white/40"
                                )}
                            >
                                {isLoading
                                    ? <LoaderIcon className="w-4 h-4 animate-[spin_2s_linear_infinite]" />
                                    : <SendIcon className="w-4 h-4" />
                                }
                                <span>{isLoading ? "Sending…" : "Send"}</span>
                            </motion.button>
                        </div>
                    </motion.div>

                    {/* Quick reply chips */}
                    <AnimatePresence>
                        {isEmpty && (
                            <motion.div
                                className="space-y-4"
                                initial={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                <div className="flex flex-wrap items-center justify-center gap-2">
                                    {commandSuggestions.map((suggestion, index) => (
                                        <motion.button
                                            key={suggestion.prefix}
                                            onClick={() => selectCommandSuggestion(index)}
                                            className="flex items-center gap-2 px-3 py-2 bg-white/[0.02] hover:bg-white/[0.05] rounded-lg text-sm text-white/60 hover:text-white/90 transition-all"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            {suggestion.icon}
                                            <span>{suggestion.label}</span>
                                        </motion.button>
                                    ))}
                                </div>

                                <div className="flex flex-wrap items-center justify-center gap-2 pt-2 border-t border-white/[0.03]">
                                    {quickReplyChips.map((chip, index) => (
                                        <motion.button
                                            key={chip.label}
                                            type="button"
                                            onClick={() => handleSendMessage(chip.text)}
                                            className="flex items-center gap-1.5 bg-white/[0.03] border border-white/[0.07] rounded-full text-white/50 hover:text-white/90 hover:bg-blue-900/30 hover:border-blue-600/50 text-xs px-3 py-1.5 transition-all cursor-pointer"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.3 + index * 0.05 }}
                                            whileHover={{ scale: 1.02 }}
                                            whileTap={{ scale: 0.98 }}
                                        >
                                            {chip.icon}
                                            <span>{chip.label}</span>
                                        </motion.button>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </div>

            {/* Mouse follow glow */}
            {inputFocused && (
                <motion.div
                    className="fixed w-[50rem] h-[50rem] rounded-full pointer-events-none z-0 opacity-[0.02] bg-gradient-to-r from-blue-800 via-amber-500/20 to-blue-900 blur-[96px]"
                    animate={{ x: mousePosition.x - 400, y: mousePosition.y - 400 }}
                    transition={{ type: "spring", damping: 25, stiffness: 150, mass: 0.5 }}
                />
            )}
        </div>
    );
}
