interface PageHeaderProps {
  title: string
  description: string
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div className="mb-10 text-center animate-fade-in">
      <h1 className="text-5xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-purple-light via-purple to-purple-light mb-3">
        {title}
      </h1>
      <p className="text-lg text-gray-300 font-light tracking-wide max-w-2xl mx-auto leading-relaxed">{description}</p>
    </div>
  )
}

