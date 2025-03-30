"use client";

import { useEffect, useRef } from "react";
import { Textarea } from "@/components/ui/textarea";

interface CodeEditorProps {
    value: string;
    onChange: (value: string) => void;
    language: string;
    placeholder?: string;
    minHeight?: string;
}

export function CodeEditor({
    value,
    onChange,
    language,
    placeholder,
    minHeight = "150px",
}: CodeEditorProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-resize textarea based on content
    useEffect(() => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        const adjustHeight = () => {
            textarea.style.height = minHeight;
            textarea.style.height = `${Math.max(
                textarea.scrollHeight,
                Number.parseInt(minHeight)
            )}px`;
        };

        adjustHeight();
        window.addEventListener("resize", adjustHeight);

        return () => window.removeEventListener("resize", adjustHeight);
    }, [value, minHeight]);

    return (
        <Textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            className="font-mono text-sm resize-none bg-gray-950 border-gray-800 text-gray-200 rounded-md transition-all duration-200 focus:border-purple-dark focus:ring-1 focus:ring-purple-dark"
            style={{
                minHeight,
                whiteSpace: "pre-wrap",
                overflowWrap: "break-word",
                overflowX: "hidden",
                overflowY: "hidden",
                lineHeight: "1.6",
                letterSpacing: "0.01em",
            }}
        />
    );
}
