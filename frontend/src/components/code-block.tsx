"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Copy, Check } from "lucide-react"

interface CodeBlockProps {
  code: string
  language: string
}

export function CodeBlock({ code, language }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy text: ", err)
    }
  }

  return (
    <div className="relative group">
      <pre
        className={`language-${language} p-5 rounded-md bg-gray-950 overflow-x-auto border border-gray-800 shadow-md transition-all duration-200 group-hover:border-gray-700`}
      >
        <code className="text-sm font-mono text-gray-200 leading-relaxed tracking-wide">{code}</code>
      </pre>
      <Button
        size="sm"
        variant="ghost"
        className="absolute top-2 right-2 h-8 w-8 p-0 opacity-70 hover:opacity-100 hover:bg-purple/20 transition-all duration-200"
        onClick={copyToClipboard}
      >
        {copied ? <Check className="h-4 w-4 text-green-400" /> : <Copy className="h-4 w-4 text-gray-400" />}
        <span className="sr-only">Copy code</span>
      </Button>
    </div>
  )
}

