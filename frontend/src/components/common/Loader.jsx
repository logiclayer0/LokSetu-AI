const Loader = ({ size = 'md' }) => {
  const sizes = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-2',
    lg: 'w-12 h-12 border-3',
  }
  return (
    <div className="flex items-center justify-center p-4">
      <div className={`${sizes[size]} border-primary-600 border-t-transparent rounded-full animate-spin`} />
    </div>
  )
}

export default Loader