"use client";

import type React from "react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CodeEditor } from "@/components/code-editor";
import { DebugResults } from "@/components/debug-results";
import { Loader2, Zap } from "lucide-react";

interface DebugResponse {
    requiresDocumentation: boolean;
    searchPhrase?: string;
    documentationResults?: {
        title: string;
        content: string;
    }[];
    explanation: string;
    fixedCode: string;
    alternativeSolutions?: string[];
    documentationWasUseful?: boolean;
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

        try {
            // Simulated API call
            await new Promise((resolve) => setTimeout(resolve, 2000));

            const mockResponse: DebugResponse = {
                requiresDocumentation: true,
                searchPhrase: "python list index out of range error handling",
                documentationResults: [
                    {
                        title: "Python Lists and Index Errors",
                        content:
                            "When accessing elements in a list, Python raises an IndexError if the index is out of range. Always check that your index is valid before accessing a list element.",
                    },
                    {
                        title: "Error Handling in Python",
                        content:
                            "Use try/except blocks to handle potential IndexError exceptions when working with lists of unknown length.",
                    },
                ],
                explanation:
                    "Your code is trying to access an index in the list that doesn't exist. The list has fewer elements than the index you're trying to access.",
                fixedCode:
                    "try:\n    result = my_list[index]\nexcept IndexError:\n    result = None  # or some default value",
                alternativeSolutions: [
                    "if index < len(my_list):\n    result = my_list[index]\nelse:\n    result = None  # or some default value",
                ],
                documentationWasUseful: true,
            };

            setResults(mockResponse);
        } catch (error) {
            console.error("Error processing debug request:", error);
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="space-y-8 animate-fade-in">
            <form onSubmit={handleSubmit}>
                <Card className="bg-gray-900/60 border-gray-800 backdrop-blur-sm shadow-xl transition-all duration-300 hover:shadow-purple-900/20">
                    <CardContent className="p-8 space-y-8">
                        {/* Stack Trace and Code Snippet side by side */}
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

                        {/* Optional Prompt */}
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
