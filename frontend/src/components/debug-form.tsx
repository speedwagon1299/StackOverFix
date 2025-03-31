"use client";

import type React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CodeEditor } from "@/components/code-editor";
import {
    DebugResults,
    normalizeDebugResponse,
} from "@/components/debug-results";
import { Loader2, Zap } from "lucide-react";

interface DebugResponse {
    requiresDocumentation: boolean;
    explanation: string;
    fixedCode: string;
    updated_response?: string;
}

export function DebugForm() {
    const [stackTrace, setStackTrace] = useState("");
    const [codeSnippet, setCodeSnippet] = useState("");
    const [prompt, setPrompt] = useState<string>("");
    const [isProcessing, setIsProcessing] = useState(false);
    const [results, setResults] = useState<DebugResponse | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!stackTrace.trim() || !codeSnippet.trim()) return;

        setIsProcessing(true);
        const sessionId = crypto.randomUUID();

        let parsedStackTrace;
        try {
            parsedStackTrace = JSON.parse(stackTrace);
        } catch {
            alert("⚠️ Stack Trace must be valid JSON.");
            setIsProcessing(false);
            return;
        }

        try {
            const analyzeResponse = await fetch(
                "http://127.0.0.1:8000/analyze_error",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                        user_prompt: prompt || "Please solve the bug",
                        code_snippet: codeSnippet,
                        stack_trace: parsedStackTrace,
                    }),
                }
            );

            if (!analyzeResponse.ok)
                throw new Error("analyze_error request failed");

            const submitResponse = await fetch(
                "http://127.0.0.1:8000/submit_documents",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        session_id: sessionId,
                    }),
                }
            );

            if (!submitResponse.ok)
                throw new Error("submit_documents request failed");

            const raw = await submitResponse.json();
            const normalized = normalizeDebugResponse(raw);
            setResults(normalized);
        } catch (error) {
            console.error("Error during debug flow:", error);
            alert("❌ Something went wrong. Check the console for details.");
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="space-y-8 animate-fade-in">
            <form onSubmit={handleSubmit}>
                <Card className="bg-gray-900/60 border-gray-800 backdrop-blur-sm shadow-xl transition-all duration-300 hover:shadow-purple-900/20">
                    <CardContent className="p-8 space-y-8">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            <div className="flex flex-col">
                                <h2 className="text-xl font-medium mb-3 text-gray-200 flex items-center">
                                    <span className="mr-2">Stack Trace</span>
                                    <div className="h-px flex-grow bg-gradient-to-r from-transparent via-gray-700 to-transparent ml-2 opacity-50"></div>
                                </h2>
                                <CodeEditor
                                    value={stackTrace}
                                    onChange={setStackTrace}
                                    language="python"
                                    placeholder="Paste your full error stack trace here..."
                                    minHeight="200px"
                                />
                            </div>

                            <div className="flex flex-col">
                                <h2 className="text-xl font-medium mb-3 text-gray-200 flex items-center">
                                    <span className="mr-2">Code Snippet</span>
                                    <div className="h-px flex-grow bg-gradient-to-r from-transparent via-gray-700 to-transparent ml-2 opacity-50"></div>
                                </h2>
                                <CodeEditor
                                    value={codeSnippet}
                                    onChange={setCodeSnippet}
                                    language="python"
                                    placeholder="Paste the relevant code snippet here..."
                                    minHeight="200px"
                                />
                            </div>
                        </div>

                        <div className="flex flex-col">
                            <h2 className="text-xl font-medium mb-3 text-gray-200 flex items-center">
                                <span className="mr-2">Optional Prompt</span>
                                <div className="h-px flex-grow bg-gradient-to-r from-transparent via-gray-700 to-transparent ml-2 opacity-50"></div>
                            </h2>
                            <CodeEditor
                                value={prompt}
                                onChange={setPrompt}
                                language="text"
                                placeholder="e.g. Can you explain why this error occurs and suggest best practices?"
                                minHeight="100px"
                            />
                        </div>

                        <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-purple-dark to-purple hover:from-purple hover:to-purple-light text-white font-medium py-6 transition-all duration-300 shadow-lg hover:shadow-purple/40"
                            size="lg"
                            disabled={
                                isProcessing ||
                                !stackTrace.trim() ||
                                !codeSnippet.trim()
                            }
                        >
                            {isProcessing ? (
                                <>
                                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    <Zap className="mr-2 h-5 w-5" />
                                    Fix My Code
                                </>
                            )}
                        </Button>
                    </CardContent>
                </Card>
            </form>

            {results && !isProcessing && <DebugResults results={results} />}
        </div>
    );
}
