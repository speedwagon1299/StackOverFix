import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { CodeBlock } from "@/components/code-block";
import { FileText, Info } from "lucide-react";
import { useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface DebugResultsProps {
    results: {
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
        updated_response?: string;
    };
}

export function normalizeDebugResponse(
    apiData: any
): DebugResultsProps["results"] {
    const docs = Array.isArray(apiData.retrieved_documents)
        ? apiData.retrieved_documents.map((url: string, i: number) => ({
              title: `Documentation Link ${i + 1}`,
              content: url,
          }))
        : [];

    return {
        requiresDocumentation: docs.length > 0,
        documentationResults: docs,
        searchPhrase: apiData.search_phrase || "",
        explanation: "",
        fixedCode: "",
        updated_response: apiData.updated_response,
    };
}

export function DebugResults({ results }: DebugResultsProps) {
    const docRequired = results.requiresDocumentation === true;

    useEffect(() => {
        console.log(
            "[DebugResults] requiresDocumentation:",
            results.requiresDocumentation
        );
        console.log("[DebugResults] docRequired:", docRequired);
        console.log(
            "[DebugResults] documentationResults:",
            results.documentationResults
        );
    }, [results]);

    let explanationPart = "";
    let codePart = "";
    let postCodePart = "";

    if (results.updated_response) {
        const parts = results.updated_response.split(/```(?:python)?\n|\n```/);
        explanationPart = parts[0]?.trim() || "";
        codePart = parts[1]?.trim() || "";
        postCodePart = parts[2]?.trim() || "";
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <Card className="bg-gray-900/60 border-gray-800 backdrop-blur-sm shadow-xl transition-all duration-300 hover:shadow-purple-900/20">
                <CardHeader className="border-b border-gray-800/50 pb-4">
                    <CardTitle className="flex items-center justify-between text-gray-100 text-xl">
                        <span className="font-medium">Debugging Results</span>
                        <Badge
                            variant={docRequired ? "default" : "outline"}
                            className={
                                docRequired
                                    ? "bg-gradient-to-r from-purple-dark to-purple text-white font-medium px-3 py-1"
                                    : "text-purple-light border-purple-light"
                            }
                        >
                            {docRequired
                                ? "Documentation Required"
                                : "Direct Fix"}
                        </Badge>
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-8 pt-6">
                    {/* Step 1: Documentation Relevance Check */}
                    <div>
                        <h3 className="text-lg font-medium mb-3 flex items-center text-gray-200">
                            <span className="bg-purple/10 p-1.5 rounded-full mr-2 text-purple-light flex items-center justify-center w-7 h-7">
                                1
                            </span>
                            Documentation Relevance Check
                        </h3>
                        <Alert
                            variant={docRequired ? "default" : "secondary"}
                            className={
                                docRequired
                                    ? "bg-gray-800/60 border-purple border-l-4 pl-4"
                                    : "bg-gray-800/60 border-gray-700 border-l-4 pl-4"
                            }
                        >
                            <Info className="h-4 w-4" />
                            <AlertTitle className="font-medium text-base">
                                {docRequired
                                    ? "Documentation retrieval required"
                                    : "Documentation retrieval not required"}
                            </AlertTitle>
                            <AlertDescription className="text-gray-300">
                                {docRequired && results.searchPhrase && (
                                    <div className="mt-2">
                                        <p className="font-medium">
                                            Search phrase generated:
                                        </p>
                                        <p className="text-sm italic text-purple-light">
                                            "{results.searchPhrase}"
                                        </p>
                                    </div>
                                )}
                            </AlertDescription>
                        </Alert>
                    </div>

                    {/* Step 2: FAISS Vector Search */}
                    {docRequired && results.documentationResults && (
                        <div>
                            <h3 className="text-lg font-medium mb-3 flex items-center text-gray-200">
                                <span className="bg-purple/10 p-1.5 rounded-full mr-2 text-purple-light flex items-center justify-center w-7 h-7">
                                    2
                                </span>
                                FAISS Vector Search Results
                            </h3>
                            <div className="space-y-4">
                                {results.documentationResults.map(
                                    (doc, index) => (
                                        <Card
                                            key={index}
                                            className="border-dashed bg-gray-800/40 hover:bg-gray-800/60 transition-all duration-200"
                                        >
                                            <CardContent className="p-4">
                                                <div className="flex items-start gap-3">
                                                    <FileText className="h-5 w-5 text-purple-light flex-shrink-0 mt-1" />
                                                    <div>
                                                        <h4 className="font-medium text-gray-200">
                                                            {doc.title}
                                                        </h4>
                                                        <p className="text-sm text-gray-300 mt-1 leading-relaxed">
                                                            {doc.content}
                                                        </p>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    )
                                )}
                            </div>
                        </div>
                    )}

                    {/* Step 3: Final Explanation from Submit Documents */}
                    {results.updated_response && (
                        <div>
                            <h3 className="text-lg font-medium mb-3 flex items-center text-gray-200">
                                <span className="bg-purple/10 p-1.5 rounded-full mr-2 text-purple-light flex items-center justify-center w-7 h-7">
                                    {docRequired ? "3" : "2"}
                                </span>
                                Final Explanation
                            </h3>
                            <div className="space-y-6">
                                {explanationPart && (
                                    <div className="bg-gray-800/50 p-6 rounded-xl border border-purple/30 text-sm text-gray-200 leading-relaxed font-sans">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                        >
                                            {explanationPart}
                                        </ReactMarkdown>
                                    </div>
                                )}
                                {codePart && (
                                    <div>
                                        <h4 className="font-medium mb-2 text-gray-200">
                                            Fixed Code
                                        </h4>
                                        <CodeBlock
                                            code={codePart}
                                            language="python"
                                        />
                                    </div>
                                )}
                                {postCodePart && (
                                    <div className="bg-gray-800/50 p-6 rounded-xl border border-purple/30 text-sm text-gray-200 leading-relaxed font-sans">
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                        >
                                            {postCodePart}
                                        </ReactMarkdown>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
