import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { CodeBlock } from "@/components/code-block"
import { CheckCircle, XCircle, FileText, Info, Lightbulb } from "lucide-react"

interface DebugResultsProps {
  results: {
    requiresDocumentation: boolean
    searchPhrase?: string
    documentationResults?: {
      title: string
      content: string
    }[]
    explanation: string
    fixedCode: string
    alternativeSolutions?: string[]
    documentationWasUseful?: boolean
  }
}

export function DebugResults({ results }: DebugResultsProps) {
  return (
    <div className="space-y-6 animate-fade-in">
      <Card className="bg-gray-900/60 border-gray-800 backdrop-blur-sm shadow-xl transition-all duration-300 hover:shadow-purple-900/20">
        <CardHeader className="border-b border-gray-800/50 pb-4">
          <CardTitle className="flex items-center justify-between text-gray-100 text-xl">
            <span className="font-medium">Debugging Results</span>
            <Badge
              variant={results.requiresDocumentation ? "default" : "outline"}
              className={
                results.requiresDocumentation
                  ? "bg-gradient-to-r from-purple-dark to-purple text-white font-medium px-3 py-1"
                  : "text-purple-light border-purple-light"
              }
            >
              {results.requiresDocumentation ? "Documentation Required" : "Direct Fix"}
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
              variant={results.requiresDocumentation ? "default" : "secondary"}
              className={
                results.requiresDocumentation
                  ? "bg-gray-800/60 border-purple border-l-4 pl-4"
                  : "bg-gray-800/60 border-gray-700 border-l-4 pl-4"
              }
            >
              <Info className="h-4 w-4" />
              <AlertTitle className="font-medium text-base">
                {results.requiresDocumentation
                  ? "Documentation retrieval required"
                  : "Documentation retrieval not required"}
              </AlertTitle>
              <AlertDescription className="text-gray-300">
                {results.requiresDocumentation && results.searchPhrase && (
                  <div className="mt-2">
                    <p className="font-medium">Search phrase generated:</p>
                    <p className="text-sm italic text-purple-light">"{results.searchPhrase}"</p>
                  </div>
                )}
              </AlertDescription>
            </Alert>
          </div>

          {/* Step 2: FAISS Vector Search (If Required) */}
          {results.requiresDocumentation && results.documentationResults && (
            <div>
              <h3 className="text-lg font-medium mb-3 flex items-center text-gray-200">
                <span className="bg-purple/10 p-1.5 rounded-full mr-2 text-purple-light flex items-center justify-center w-7 h-7">
                  2
                </span>
                FAISS Vector Search Results
              </h3>
              <div className="space-y-4">
                {results.documentationResults.map((doc, index) => (
                  <Card
                    key={index}
                    className="border-dashed bg-gray-800/40 hover:bg-gray-800/60 transition-all duration-200"
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <FileText className="h-5 w-5 text-purple-light flex-shrink-0 mt-1" />
                        <div>
                          <h4 className="font-medium text-gray-200">{doc.title}</h4>
                          <p className="text-sm text-gray-300 mt-1 leading-relaxed">{doc.content}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Step 3: AI-Powered Error Correction */}
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center text-gray-200">
              <span className="bg-purple/10 p-1.5 rounded-full mr-2 text-purple-light flex items-center justify-center w-7 h-7">
                {results.requiresDocumentation ? "3" : "2"}
              </span>
              AI-Powered Error Correction
            </h3>

            {results.requiresDocumentation && typeof results.documentationWasUseful === "boolean" && (
              <Alert
                variant={results.documentationWasUseful ? "success" : "destructive"}
                className={`mb-4 ${
                  results.documentationWasUseful
                    ? "bg-green-900/20 border-green-600 border-l-4 pl-4"
                    : "bg-red-900/20 border-red-600 border-l-4 pl-4"
                }`}
              >
                {results.documentationWasUseful ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                <AlertTitle className="font-medium">
                  {results.documentationWasUseful ? "Documentation was helpful" : "Documentation was not helpful"}
                </AlertTitle>
                <AlertDescription className="text-gray-300">
                  {results.documentationWasUseful
                    ? "The retrieved documentation was used to generate a better solution."
                    : "A direct fix was generated without using the documentation."}
                </AlertDescription>
              </Alert>
            )}

            <div className="space-y-6">
              <div className="bg-gray-800/40 p-5 rounded-lg border border-gray-800/80">
                <h4 className="font-medium mb-2 flex items-center text-gray-200">
                  <Lightbulb className="h-4 w-4 mr-2 text-yellow-400" />
                  Root Cause Explanation
                </h4>
                <p className="text-gray-300 leading-relaxed">{results.explanation}</p>
              </div>

              <div>
                <h4 className="font-medium mb-3 text-gray-200">Fixed Code</h4>
                <CodeBlock code={results.fixedCode} language="python" />
              </div>

              {results.alternativeSolutions && results.alternativeSolutions.length > 0 && (
                <div>
                  <h4 className="font-medium mb-3 text-gray-200">Alternative Solutions</h4>
                  <div className="space-y-4">
                    {results.alternativeSolutions.map((solution, index) => (
                      <div key={index}>
                        <p className="text-sm text-gray-400 mb-2">Alternative {index + 1}:</p>
                        <CodeBlock code={solution} language="python" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

